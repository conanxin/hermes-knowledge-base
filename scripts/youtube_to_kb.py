#!/usr/bin/env python3
"""YouTube transcript -> Hermes KB import.

This importer is deliberately narrow: it fetches public YouTube metadata and
caption/transcript text only. It never downloads the video file, never uses
browser cookies, and hard-stops when no usable transcript is available.

Usage:
    python scripts/youtube_to_kb.py --url "<YOUTUBE_URL>" --dry-run
    python scripts/youtube_to_kb.py --url "<YOUTUBE_URL>" --import
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import re
import sys
import unicodedata
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

KB_HOME = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = KB_HOME / "scripts"
CONTENT_DIR = KB_HOME / "content"
ARTICLES_DIR = CONTENT_DIR / "articles"
INBOX_YOUTUBE = KB_HOME / "inbox" / "raw" / "youtube"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import import_wechat_article_capture as kb_helpers  # type: ignore

BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

STATUS_IMPORTED = "IMPORTED"
STATUS_DRY_RUN_OK = "DRY_RUN_OK"
STATUS_DRY_RUN_DUPLICATE = "DRY_RUN_DUPLICATE"
STATUS_SKIPPED_DUPLICATE = "SKIPPED_DUPLICATE"
STATUS_BLOCKED_UNSUPPORTED = "BLOCKED_UNSUPPORTED"
STATUS_BLOCKED_FETCH_FAILED = "BLOCKED_FETCH_FAILED"
STATUS_BLOCKED_INCOMPLETE_TEXT = "BLOCKED_INCOMPLETE_TEXT"
STATUS_FAILED_IMPORT = "FAILED_IMPORT"

MIN_TRANSCRIPT_CHARS = 320
MIN_TRANSCRIPT_WORDS = 80
MIN_TRANSCRIPT_CJK = 80


class YouTubeImportError(Exception):
    def __init__(self, status: str, reason: str):
        super().__init__(reason)
        self.status = status
        self.reason = reason


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Import a YouTube transcript into Hermes KB.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--url", required=True, help="youtube.com/watch, youtu.be, or youtube.com/shorts URL")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="validate without writing a KB entry")
    mode.add_argument("--import", dest="do_import", action="store_true", help="write the KB entry")
    parser.add_argument("--language", default="", help="preferred transcript language, e.g. zh-CN or en")
    parser.add_argument("--prefer-auto-captions", action="store_true", help="prefer automatic captions over manual captions")
    parser.add_argument("--no-auto-captions", action="store_true", help="block if only automatic captions are available")
    parser.add_argument("--timeout", type=int, default=20, help="HTTP timeout in seconds")

    # Offline smoke-test hooks. They are intentionally undocumented in user docs.
    parser.add_argument("--metadata-file", help=argparse.SUPPRESS)
    parser.add_argument("--transcript-file", help=argparse.SUPPRESS)
    return parser


def _now_iso() -> str:
    return dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _today_date() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d")


def slugify(text: str, max_len: int = 56) -> str:
    text = unicodedata.normalize("NFKC", text or "")
    text = re.sub(r"[^\u4e00-\u9fff\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text.strip())
    text = re.sub(r"-+", "-", text)
    if len(text) > max_len:
        head = text[:max_len]
        text = head.rsplit("-", 1)[0] if "-" in head else head
    return text.lower().strip("-") or "untitled"


def _clean_text(value: str | None) -> str:
    if not value:
        return ""
    value = html.unescape(value)
    value = re.sub(r"<[^>]+>", "", value)
    return re.sub(r"\s+", " ", value).strip()


def _yaml_quote(value: Any) -> str:
    return kb_helpers.escape_yaml_string(str(value or ""))


def _yaml_list(items: list[str], indent: int = 0) -> str:
    return kb_helpers.format_yaml_list(items, indent=indent)


def _format_duration(seconds: int | str | None) -> str:
    try:
        total = int(seconds or 0)
    except (TypeError, ValueError):
        total = 0
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def _format_timestamp(seconds: float) -> str:
    total = max(0, int(seconds))
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def _safe_date(value: str) -> str:
    if not value:
        return ""
    value = value.strip()
    if re.fullmatch(r"\d{8}", value):
        return f"{value[:4]}-{value[4:6]}-{value[6:8]}"
    match = re.match(r"(\d{4}-\d{2}-\d{2})", value)
    if match:
        return match.group(1)
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%Y-%m-%d")
    except ValueError:
        return ""


def parse_video_id(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    host = parsed.netloc.lower()
    if host == "youtu.be" or host.endswith(".youtu.be"):
        candidate = parsed.path.strip("/").split("/")[0]
        return candidate if re.fullmatch(r"[\w-]{6,}", candidate or "") else ""
    if "youtube.com" in host:
        if parsed.path == "/watch":
            return urllib.parse.parse_qs(parsed.query).get("v", [""])[0]
        parts = [p for p in parsed.path.split("/") if p]
        if len(parts) >= 2 and parts[0] in {"shorts", "embed", "live"}:
            return parts[1]
    return ""


def canonical_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}" if video_id else ""


def _normalize_url(url: str) -> str:
    parsed = urllib.parse.urlsplit((url or "").strip())
    return urllib.parse.urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path.rstrip("/") or "/", parsed.query, ""))


def _content_hash(text: str) -> str:
    visible = re.sub(r"\s+", " ", text or "").strip()
    return hashlib.sha256(visible.encode("utf-8", errors="replace")).hexdigest()


def _request_text(url: str, timeout: int) -> str:
    try:
        import requests  # type: ignore
    except ImportError as exc:
        raise YouTubeImportError(STATUS_FAILED_IMPORT, "requests is required for YouTube URL fetch") from exc
    headers = {
        "User-Agent": BROWSER_UA,
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
    except Exception as exc:
        raise YouTubeImportError(STATUS_BLOCKED_FETCH_FAILED, f"network error fetching YouTube URL: {exc}") from exc
    if resp.status_code != 200:
        raise YouTubeImportError(STATUS_BLOCKED_FETCH_FAILED, f"non-200 HTTP status from YouTube: {resp.status_code}")
    return resp.text


def _extract_balanced_json(text: str, marker: str) -> dict[str, Any]:
    start = text.find(marker)
    if start < 0:
        return {}
    brace = text.find("{", start)
    if brace < 0:
        return {}
    depth = 0
    in_string = False
    escape = False
    for i in range(brace, len(text)):
        ch = text[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[brace:i + 1])
                except json.JSONDecodeError:
                    return {}
    return {}


def _simple_text(value: Any) -> str:
    if isinstance(value, str):
        return _clean_text(value)
    if isinstance(value, dict):
        if "simpleText" in value:
            return _clean_text(str(value.get("simpleText") or ""))
        runs = value.get("runs")
        if isinstance(runs, list):
            return _clean_text(" ".join(str(r.get("text", "")) for r in runs if isinstance(r, dict)))
    return ""


def _last_thumbnail(thumbnails: Any) -> str:
    if isinstance(thumbnails, dict):
        thumbnails = thumbnails.get("thumbnails")
    if isinstance(thumbnails, list) and thumbnails:
        for item in reversed(thumbnails):
            if isinstance(item, dict) and item.get("url"):
                return str(item["url"])
    return ""


def _metadata_from_player(player: dict[str, Any], source_url: str, video_id: str) -> dict[str, Any]:
    status = player.get("playabilityStatus", {})
    play_status = status.get("status")
    if play_status and play_status not in {"OK", "LIVE_STREAM_OFFLINE"}:
        reason = status.get("reason") or play_status
        raise YouTubeImportError(STATUS_BLOCKED_UNSUPPORTED, f"YouTube playability status is {play_status}: {reason}")

    video = player.get("videoDetails", {}) if isinstance(player.get("videoDetails"), dict) else {}
    micro = player.get("microformat", {}).get("playerMicroformatRenderer", {})
    title = _clean_text(str(video.get("title") or micro.get("title", {}).get("simpleText") or ""))
    if not title:
        raise YouTubeImportError(STATUS_BLOCKED_INCOMPLETE_TEXT, "cannot extract YouTube title")
    channel = _clean_text(str(video.get("author") or micro.get("ownerChannelName") or "Unknown"))
    channel_url = str(micro.get("ownerProfileUrl") or "")
    if channel_url.startswith("/"):
        channel_url = urllib.parse.urljoin("https://www.youtube.com", channel_url)
    if not channel_url and video.get("channelId"):
        channel_url = f"https://www.youtube.com/channel/{video.get('channelId')}"
    published = _safe_date(str(micro.get("publishDate") or micro.get("uploadDate") or ""))
    duration = int(video.get("lengthSeconds") or 0)
    description = _clean_text(str(video.get("shortDescription") or micro.get("description", {}).get("simpleText") or ""))
    view_count = 0
    try:
        view_count = int(video.get("viewCount") or micro.get("viewCount") or 0)
    except (TypeError, ValueError):
        view_count = 0
    return {
        "title": title,
        "channel": channel,
        "author": channel,
        "channel_url": channel_url,
        "published_date": published,
        "upload_date": _safe_date(str(micro.get("uploadDate") or "")),
        "duration": duration,
        "duration_hms": _format_duration(duration),
        "view_count": view_count,
        "description": description,
        "thumbnail_url": _last_thumbnail(video.get("thumbnail")) or _last_thumbnail(micro.get("thumbnail")),
        "source_url": source_url,
        "canonical_url": canonical_url(video_id),
        "video_id": video_id,
        "source_site": "YouTube",
        "raw_metadata_source": "ytInitialPlayerResponse",
    }


def _caption_tracks(player: dict[str, Any]) -> list[dict[str, Any]]:
    captions = player.get("captions", {})
    renderer = captions.get("playerCaptionsTracklistRenderer", {}) if isinstance(captions, dict) else {}
    tracks = renderer.get("captionTracks", []) if isinstance(renderer, dict) else []
    out: list[dict[str, Any]] = []
    for track in tracks:
        if not isinstance(track, dict) or not track.get("baseUrl"):
            continue
        lang = str(track.get("languageCode") or "")
        kind = "auto" if track.get("kind") == "asr" or str(track.get("vssId", "")).startswith("a.") else "manual"
        out.append({
            "language": lang,
            "name": _simple_text(track.get("name")),
            "kind": kind,
            "base_url": html.unescape(str(track.get("baseUrl"))),
        })
    return out


def _language_priority(preferred: str) -> list[str]:
    if preferred:
        base = preferred.lower()
        if base.startswith("zh"):
            return [base, "zh-cn", "zh-hans", "zh"]
        if base.startswith("en"):
            return [base, "en"]
        return [base]
    return ["zh-cn", "zh-hans", "zh", "en"]


def select_caption_track(tracks: list[dict[str, Any]], preferred: str, prefer_auto: bool, allow_auto: bool) -> dict[str, Any]:
    ranked = rank_caption_tracks(tracks, preferred, prefer_auto=prefer_auto, allow_auto=allow_auto)
    return ranked[0]


def rank_caption_tracks(tracks: list[dict[str, Any]], preferred: str, prefer_auto: bool, allow_auto: bool) -> list[dict[str, Any]]:
    if not tracks:
        raise YouTubeImportError(STATUS_BLOCKED_INCOMPLETE_TEXT, "no YouTube captions/transcript tracks are available")
    candidates = [t for t in tracks if allow_auto or t.get("kind") != "auto"]
    if not candidates:
        raise YouTubeImportError(STATUS_BLOCKED_INCOMPLETE_TEXT, "only automatic captions are available and --no-auto-captions was set")
    langs = _language_priority(preferred)

    def score(track: dict[str, Any]) -> tuple[int, int, int]:
        lang = str(track.get("language", "")).lower()
        try:
            lang_score = langs.index(lang)
        except ValueError:
            lang_score = 99
        kind = track.get("kind")
        kind_score = 0 if (kind == "auto" and prefer_auto) or (kind == "manual" and not prefer_auto) else 1
        return (kind_score, lang_score, 0 if lang.startswith(tuple(langs)) else 1)

    return sorted(candidates, key=score)


def _caption_url(base_url: str) -> str:
    parsed = urllib.parse.urlparse(base_url)
    query = urllib.parse.parse_qs(parsed.query)
    query["fmt"] = ["vtt"]
    return urllib.parse.urlunparse(parsed._replace(query=urllib.parse.urlencode(query, doseq=True)))


def fetch_caption_text(track: dict[str, Any], timeout: int) -> str:
    return _request_text(_caption_url(str(track["base_url"])), timeout=timeout)


def parse_vtt(text: str) -> list[dict[str, Any]]:
    segments: list[dict[str, Any]] = []
    lines = text.replace("\ufeff", "").splitlines()
    i = 0
    time_re = re.compile(r"(?P<start>\d{1,2}:\d{2}(?::\d{2})?[.,]\d{3})\s+-->\s+(?P<end>\d{1,2}:\d{2}(?::\d{2})?[.,]\d{3})")
    while i < len(lines):
        line = lines[i].strip()
        match = time_re.search(line)
        if not match:
            i += 1
            continue
        start = _timestamp_to_seconds(match.group("start"))
        i += 1
        text_lines: list[str] = []
        while i < len(lines) and lines[i].strip():
            raw = lines[i].strip()
            if not raw.startswith(("NOTE", "STYLE")):
                text_lines.append(raw)
            i += 1
        caption = _clean_text(" ".join(text_lines))
        if caption:
            segments.append({"start": start, "text": caption})
        i += 1
    return _dedupe_segments(segments)


def parse_xml_transcript(text: str) -> list[dict[str, Any]]:
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return []
    segments: list[dict[str, Any]] = []
    for node in root.findall(".//text"):
        try:
            start = float(node.attrib.get("start", "0"))
        except ValueError:
            start = 0.0
        caption = _clean_text(node.text or "")
        if caption:
            segments.append({"start": start, "text": caption})
    return _dedupe_segments(segments)


def _timestamp_to_seconds(value: str) -> float:
    value = value.replace(",", ".")
    parts = value.split(":")
    try:
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
        return int(parts[0]) * 60 + float(parts[1])
    except (ValueError, IndexError):
        return 0.0


def _dedupe_segments(segments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    last = ""
    for seg in segments:
        text = _clean_text(seg.get("text", ""))
        if not text or text == last:
            continue
        out.append({"start": float(seg.get("start", 0.0)), "text": text})
        last = text
    return out


def transcript_markdown(segments: list[dict[str, Any]]) -> str:
    paragraphs: list[str] = []
    current: list[str] = []
    current_start = 0.0
    char_count = 0
    for seg in segments:
        text = seg["text"]
        if not current:
            current_start = float(seg.get("start", 0.0))
        current.append(text)
        char_count += len(text)
        if char_count >= 420 or len(current) >= 8:
            paragraphs.append(f"[{_format_timestamp(current_start)}] " + " ".join(current))
            current = []
            char_count = 0
    if current:
        paragraphs.append(f"[{_format_timestamp(current_start)}] " + " ".join(current))
    return "\n\n".join(paragraphs).strip()


def detect_language(language_code: str, text: str) -> str:
    lang = (language_code or "").lower()
    if lang.startswith("zh"):
        return "zh-CN"
    if lang.startswith("en"):
        return "en"
    cjk = kb_helpers.count_cjk_chars(text)
    words = len(re.findall(r"[A-Za-z]{2,}", text))
    return "zh-CN" if cjk >= 80 and cjk >= words else "en"


def validate_transcript(markdown: str, source_language: str) -> None:
    visible = re.sub(r"\[[0-9:]+\]", " ", markdown)
    visible = re.sub(r"\s+", " ", visible).strip()
    if len(visible) < MIN_TRANSCRIPT_CHARS:
        raise YouTubeImportError(STATUS_BLOCKED_INCOMPLETE_TEXT, f"transcript too short ({len(visible)} chars < {MIN_TRANSCRIPT_CHARS})")
    cjk = kb_helpers.count_cjk_chars(visible)
    words = len(re.findall(r"[A-Za-z]{2,}", visible))
    if source_language == "zh-CN" and cjk < MIN_TRANSCRIPT_CJK:
        raise YouTubeImportError(STATUS_BLOCKED_INCOMPLETE_TEXT, f"too few Chinese transcript characters ({cjk} < {MIN_TRANSCRIPT_CJK})")
    if source_language != "zh-CN" and words < MIN_TRANSCRIPT_WORDS:
        raise YouTubeImportError(STATUS_BLOCKED_INCOMPLETE_TEXT, f"too few transcript words ({words} < {MIN_TRANSCRIPT_WORDS})")


def fetch_youtube_capture(url: str, preferred_language: str, prefer_auto: bool, allow_auto: bool, timeout: int) -> dict[str, Any]:
    video_id = parse_video_id(url)
    if not video_id:
        raise YouTubeImportError(STATUS_BLOCKED_FETCH_FAILED, "could not parse YouTube video id")
    page = _request_text(canonical_url(video_id), timeout=timeout)
    player = _extract_balanced_json(page, "ytInitialPlayerResponse")
    if not player:
        raise YouTubeImportError(STATUS_BLOCKED_FETCH_FAILED, "could not extract ytInitialPlayerResponse")
    metadata = _metadata_from_player(player, source_url=url, video_id=video_id)
    tracks = _caption_tracks(player)
    tried: list[str] = []
    for track in rank_caption_tracks(tracks, preferred_language, prefer_auto=prefer_auto, allow_auto=allow_auto):
        label = f"{track.get('language', '')}/{track.get('kind', '')}/{track.get('name', '')}"
        try:
            caption_text = fetch_caption_text(track, timeout=timeout)
        except YouTubeImportError as exc:
            tried.append(f"{label}: fetch failed: {exc.reason}")
            continue
        if not caption_text.strip():
            tried.append(f"{label}: caption endpoint returned empty text")
            continue
        segments = parse_vtt(caption_text) or parse_xml_transcript(caption_text)
        if not segments:
            tried.append(f"{label}: caption text was unparsable")
            continue
        return build_capture(metadata, track, segments, raw={
            "caption_track_count": len(tracks),
            "metadata_source": "youtube_watch_page",
            "caption_attempts": tried + [f"{label}: ok"],
        })
    reason = "; ".join(tried) if tried else "no usable caption tracks after filtering"
    raise YouTubeImportError(STATUS_BLOCKED_INCOMPLETE_TEXT, reason)


def load_fixture_capture(url: str, metadata_path: Path, transcript_path: Path | None, preferred_language: str, prefer_auto: bool, allow_auto: bool) -> dict[str, Any]:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    video_id = metadata.get("video_id") or parse_video_id(url)
    metadata.setdefault("video_id", video_id)
    metadata.setdefault("source_url", url)
    metadata.setdefault("canonical_url", canonical_url(video_id))
    metadata.setdefault("source_site", "YouTube")
    metadata.setdefault("author", metadata.get("channel", "Unknown"))
    metadata.setdefault("channel", metadata.get("author", "Unknown"))
    metadata.setdefault("duration", metadata.get("duration_seconds", 0))
    metadata.setdefault("duration_hms", _format_duration(metadata.get("duration")))
    tracks = metadata.get("caption_tracks") or []
    if transcript_path is None:
        raise YouTubeImportError(STATUS_BLOCKED_INCOMPLETE_TEXT, "fixture metadata has no transcript file")
    if not tracks:
        tracks = [{
            "language": metadata.get("transcript_language") or preferred_language or "en",
            "kind": metadata.get("transcript_kind") or "manual",
            "name": "fixture",
        }]
    track = select_caption_track(tracks, preferred_language, prefer_auto=prefer_auto, allow_auto=allow_auto)
    raw_text = transcript_path.read_text(encoding="utf-8")
    segments = parse_vtt(raw_text) or parse_xml_transcript(raw_text)
    return build_capture(metadata, track, segments, raw={"metadata_source": "fixture"})


def build_capture(metadata: dict[str, Any], track: dict[str, Any], segments: list[dict[str, Any]], raw: dict[str, Any]) -> dict[str, Any]:
    if not segments:
        raise YouTubeImportError(STATUS_BLOCKED_INCOMPLETE_TEXT, "transcript track was empty or unparsable")
    transcript_md = transcript_markdown(segments)
    source_language = detect_language(str(track.get("language") or ""), transcript_md)
    validate_transcript(transcript_md, source_language)
    transcript_text = re.sub(r"\[[0-9:]+\]", " ", transcript_md)
    transcript_text = re.sub(r"\s+", " ", transcript_text).strip()
    capture = {
        "title": metadata.get("title", ""),
        "channel": metadata.get("channel") or metadata.get("author", "Unknown"),
        "author": metadata.get("author") or metadata.get("channel", "Unknown"),
        "channel_url": metadata.get("channel_url", ""),
        "published_date": metadata.get("published_date", ""),
        "upload_date": metadata.get("upload_date", ""),
        "captured_at": _now_iso(),
        "duration": int(metadata.get("duration") or 0),
        "duration_hms": metadata.get("duration_hms") or _format_duration(metadata.get("duration")),
        "view_count": int(metadata.get("view_count") or 0),
        "description": metadata.get("description", ""),
        "thumbnail_url": metadata.get("thumbnail_url", ""),
        "source_url": metadata.get("source_url", ""),
        "canonical_url": metadata.get("canonical_url", ""),
        "video_id": metadata.get("video_id", ""),
        "source_site": "YouTube",
        "source_platform": "youtube",
        "source_language": source_language,
        "translation_language": "zh-CN",
        "transcript_language": track.get("language") or source_language,
        "transcript_kind": track.get("kind") or "manual",
        "transcript_track_name": track.get("name", ""),
        "transcript_segments": segments,
        "content_markdown": transcript_md,
        "transcript_text": transcript_text,
        "content_hash": _content_hash(transcript_text),
        "raw": raw,
    }
    if not capture["title"]:
        raise YouTubeImportError(STATUS_BLOCKED_INCOMPLETE_TEXT, "metadata title is empty")
    return capture


def _captured_date(capture: dict[str, Any]) -> str:
    captured = str(capture.get("captured_at") or "")
    return captured.split("T", 1)[0] if "T" in captured else (captured[:10] or _today_date())


def _published_or_captured_date(capture: dict[str, Any]) -> str:
    return capture.get("published_date") or capture.get("upload_date") or _captured_date(capture)


def item_dir_for_capture(capture: dict[str, Any]) -> Path:
    date_part = _published_or_captured_date(capture)
    year = (date_part or _today_date())[:4]
    channel_slug = slugify(capture.get("channel") or "youtube", max_len=24)
    title_slug = slugify(capture.get("title") or "untitled", max_len=54)
    return ARTICLES_DIR / year / f"{date_part}-youtube-{channel_slug}-{title_slug}"


def _translation_for_capture(capture: dict[str, Any]) -> tuple[str, bool]:
    transcript = capture.get("content_markdown", "").strip()
    title = capture.get("title", "Untitled")
    if capture.get("source_language") == "zh-CN":
        return transcript, True
    preview = "\n\n".join(transcript.split("\n\n")[:6])
    text = f"""# 中文翻译（待人工补全）：{title}

> 本条目由 YouTube 字幕/转录稿导入路线生成。当前仓库没有配置稳定翻译引擎，因此这里先保留合法的中文占位草稿，避免伪装成完整人工翻译。
> 请在后续人工或 LLM 校对流程中补全正式译文。

## 原字幕结构参考

{preview}
"""
    return text.strip(), False


def generate_source_md(capture: dict[str, Any]) -> str:
    lines = [
        f"# {capture.get('title', 'Untitled')}",
        "",
        f"- **Channel**: {capture.get('channel', '')}",
        f"- **Video URL**: {capture.get('canonical_url') or capture.get('source_url', '')}",
        f"- **Published date**: {capture.get('published_date', '')}",
        f"- **Duration**: {capture.get('duration_hms', '')}",
        f"- **Transcript language**: {capture.get('transcript_language', '')}",
        f"- **Transcript kind**: {capture.get('transcript_kind', '')}",
        "",
        "## Transcript",
        "",
        capture.get("content_markdown", "").strip(),
        "",
    ]
    return "\n".join(lines)


def _first_transcript_quotes(capture: dict[str, Any], count: int = 3) -> list[str]:
    paras = [p.strip() for p in capture.get("content_markdown", "").split("\n\n") if p.strip()]
    return [re.sub(r"\s+", " ", p)[:260] for p in paras[:count]]


def generate_summary_md(capture: dict[str, Any]) -> str:
    title = capture.get("title", "Untitled")
    description = capture.get("description", "").strip()
    quotes = _first_transcript_quotes(capture, count=3)
    quote_lines = "\n".join(f"- {q}" for q in quotes) or "- （请查看 source.md 中的完整字幕。）"
    return f"""# {title}

## 一句话总结

这个视频围绕「{title}」展开，当前入库内容来自 YouTube 字幕/转录稿，适合作为后续精读、翻译和主题卡片整理的基础材料。

## 视频核心问题

- 视频试图回答的核心问题，需要在人工精读字幕后进一步压缩确认。
- 当前可确认的信息来自标题、频道、描述和字幕正文。

## 主要观点

- 字幕已经完整入库，可从时间戳结构追踪讲述顺序。
- 需要后续人工校对，把机器字幕中的口语、省略和识别误差整理成正式知识笔记。
- 若本视频与现有 KB 条目相关，应优先建立主题、人物和概念之间的链接。

## 结构 / 时间线

- 频道：{capture.get('channel', '')}
- 发布时间：{capture.get('published_date', '')}
- 视频时长：{capture.get('duration_hms', '')}
- 字幕语言：{capture.get('transcript_language', '')}
- 字幕类型：{capture.get('transcript_kind', '')}

## 关键概念

- YouTube 字幕
- 视频转录
- 结构化观看
- 后续翻译校对

## 背景补充

{description or '暂无可靠描述；建议后续结合视频页面描述与字幕内容补充背景。'}

## 值得摘录的句子

{quote_lines}

## 与知识库已有条目的可能关联

- 可与同主题文章、演讲、访谈或视频条目互链。
- 若出现重复视频 ID、来源 URL 或转录稿 hash，导入脚本会阻止重复入库。

## 我的个人观看提示

先沿 `source.md` 的时间戳快速复看，再补全正式中文翻译和概念卡片；不要把当前占位翻译当作人工译稿。
"""


def generate_notes_md(capture: dict[str, Any]) -> str:
    quotes = _first_transcript_quotes(capture, count=5)
    quote_lines = "\n".join(f"- {q}" for q in quotes) or "- （暂无可摘录片段。）"
    return f"""# 观看笔记：{capture.get('title', 'Untitled')}

## 我接受的观点

- 先接受字幕作为可检索材料，而不是把它误认为已经完成的深度解读。

## 我反思的观点

- 自动字幕可能有识别误差；涉及事实、人名、数字和引用时需要回看视频核对。

## 我联想到的材料

- 现有 YouTube 视频知识包。
- 同主题普通网页文章和访谈条目。

## 可执行行动

- 补全正式中文翻译。
- 从 transcript 中抽取 5-10 张概念卡片。
- 给相关 KB 条目加互链。

## 关键摘录

{quote_lines}

## 概念卡片

- **视频转录稿**：把视频内容转成可搜索、可引用、可复看的文本材料。
- **字幕类型**：manual 表示人工字幕，auto 表示 YouTube 自动字幕。
- **导入边界**：没有字幕或字幕过短时不写 KB 半成品。

## 结构笔记

- 来源：YouTube
- 频道：{capture.get('channel', '')}
- 发布时间：{capture.get('published_date', '')}
- 视频 ID：{capture.get('video_id', '')}

## 复看提醒

复看时优先检查转录中听感不自然的段落，再决定哪些内容值得翻译、摘录或扩展成独立笔记。
"""


def _infer_youtube_tags(capture: dict[str, Any]) -> list[str]:
    text = " ".join([capture.get("title", ""), capture.get("description", ""), capture.get("transcript_text", "")])
    tags = kb_helpers.infer_tags(text, capture.get("title", ""), capture.get("channel", ""))
    for tag in [capture.get("channel", ""), "YouTube", "视频", "字幕", "转录稿"]:
        if tag and tag not in tags:
            tags.append(tag)
    return tags[:12]


def generate_metadata_yaml(capture: dict[str, Any], item_dir: Path, source_md: str, translation_md: str, is_mirror: bool) -> str:
    source_count = int(kb_helpers.count_words_mixed(source_md))
    transcript_words = len(re.findall(r"[A-Za-z]+", capture.get("transcript_text", "")))
    if transcript_words <= 0:
        transcript_words = int(kb_helpers.count_words_mixed(capture.get("transcript_text", "")))
    translation_count = int(kb_helpers.count_cjk_chars(translation_md)) or int(kb_helpers.count_words_mixed(translation_md))
    topics = kb_helpers.infer_topics(capture.get("transcript_text", ""), capture.get("title", ""))
    tags = _infer_youtube_tags(capture)
    status = "translated" if is_mirror else "needs_translation_review"
    rel_path = item_dir.relative_to(KB_HOME).as_posix() + "/"
    return f'''title: "{_yaml_quote(capture.get('title', ''))}"
title_zh: "{_yaml_quote(capture.get('title', ''))}"
source_url: "{_yaml_quote(capture.get('source_url', ''))}"
canonical_url: "{_yaml_quote(capture.get('canonical_url', ''))}"
source_site: "YouTube"
author: "{_yaml_quote(capture.get('author', capture.get('channel', 'Unknown')))}"
channel: "{_yaml_quote(capture.get('channel', ''))}"
channel_url: "{_yaml_quote(capture.get('channel_url', ''))}"
published_date: "{_yaml_quote(capture.get('published_date', ''))}"
captured_date: "{_captured_date(capture)}"
language: "{_yaml_quote(capture.get('source_language', ''))}"
source_language: "{_yaml_quote(capture.get('source_language', ''))}"
translation_language: "zh-CN"
status: "{status}"
type: "article"
content_kind: "youtube_transcript"
source_platform: "youtube"
source_type: "youtube"
dedupe_key: "youtube:{_yaml_quote(capture.get('video_id', ''))}"
content_hash: "{_yaml_quote(capture.get('content_hash', ''))}"
is_translation_mirror: {str(is_mirror).lower()}
transcript_language: "{_yaml_quote(capture.get('transcript_language', ''))}"
transcript_kind: "{_yaml_quote(capture.get('transcript_kind', ''))}"
video_id: "{_yaml_quote(capture.get('video_id', ''))}"
duration: {int(capture.get('duration') or 0)}
duration_hms: "{_yaml_quote(capture.get('duration_hms', ''))}"
view_count: {int(capture.get('view_count') or 0)}
thumbnail_url: "{_yaml_quote(capture.get('thumbnail_url', ''))}"
topics:
{_yaml_list(topics, indent=2)}
tags:
{_yaml_list(tags, indent=2)}
word_count:
  source: {source_count}
  translation: {translation_count}
  transcript: {transcript_words}
youtube:
  video_id: "{_yaml_quote(capture.get('video_id', ''))}"
  transcript_track_name: "{_yaml_quote(capture.get('transcript_track_name', ''))}"
  description: "{_yaml_quote(capture.get('description', ''))}"
capture:
  tool: "youtube_to_kb.py"
  captured_at: "{_yaml_quote(capture.get('captured_at', ''))}"
  version: "1.0"
path: "{rel_path}"
'''


def generate_output_bundle(capture: dict[str, Any]) -> dict[str, str]:
    item_dir = item_dir_for_capture(capture)
    source_md = generate_source_md(capture)
    translation_md, is_mirror = _translation_for_capture(capture)
    summary_md = generate_summary_md(capture)
    notes_md = generate_notes_md(capture)
    metadata_yaml = generate_metadata_yaml(capture, item_dir, source_md, translation_md, is_mirror)
    return {
        "metadata.yaml": metadata_yaml,
        "source.md": source_md,
        "translation.zh-CN.md": translation_md,
        "summary.md": summary_md,
        "notes.md": notes_md,
        "raw_payload.json": json.dumps(capture, ensure_ascii=False, indent=2),
    }


def _read_yaml_field(text: str, field: str) -> str:
    match = re.search(rf"^{re.escape(field)}\s*:\s*\"?([^\"\n]*)\"?\s*$", text, re.MULTILINE)
    return match.group(1).strip() if match else ""


def build_existing_index() -> dict[str, dict[str, str]]:
    index: dict[str, dict[str, str]] = {
        "by_video_id": {},
        "by_source_url": {},
        "by_canonical_url": {},
        "by_title_channel_date": {},
        "by_content_hash": {},
    }
    for meta in CONTENT_DIR.rglob("metadata.yaml"):
        try:
            text = meta.read_text(encoding="utf-8")
        except OSError:
            continue
        rel = meta.parent.relative_to(KB_HOME).as_posix()
        source_url = _read_yaml_field(text, "source_url")
        canonical = _read_yaml_field(text, "canonical_url")
        title = _read_yaml_field(text, "title")
        channel = _read_yaml_field(text, "channel") or _read_yaml_field(text, "author")
        published = _read_yaml_field(text, "published_date")
        video_id = _read_yaml_field(text, "video_id") or parse_video_id(source_url) or parse_video_id(canonical)
        content_hash = _read_yaml_field(text, "content_hash")
        raw_payload = meta.parent / "raw_payload.json"
        if raw_payload.exists():
            try:
                payload = json.loads(raw_payload.read_text(encoding="utf-8"))
                video_id = video_id or payload.get("video_id", "")
                content_hash = content_hash or payload.get("content_hash", "")
            except Exception:
                pass
        if video_id:
            index["by_video_id"].setdefault(video_id, rel)
        if source_url:
            index["by_source_url"].setdefault(_normalize_url(source_url), rel)
        if canonical:
            index["by_canonical_url"].setdefault(_normalize_url(canonical), rel)
        if title and channel and published:
            index["by_title_channel_date"].setdefault(f"{title}\0{channel}\0{published}", rel)
        if content_hash:
            index["by_content_hash"].setdefault(content_hash, rel)
    return index


def find_duplicate(capture: dict[str, Any], index: dict[str, dict[str, str]]) -> tuple[str, str, str]:
    video_id = capture.get("video_id", "")
    if video_id and video_id in index["by_video_id"]:
        return "video_id", index["by_video_id"][video_id], "video_id already exists"
    source_norm = _normalize_url(capture.get("source_url", ""))
    if source_norm and source_norm in index["by_source_url"]:
        return "source_url", index["by_source_url"][source_norm], "source_url already exists"
    canonical_norm = _normalize_url(capture.get("canonical_url", ""))
    if canonical_norm and canonical_norm in index["by_canonical_url"]:
        return "canonical_url", index["by_canonical_url"][canonical_norm], "canonical_url already exists"
    key = f"{capture.get('title', '')}\0{capture.get('channel', '')}\0{capture.get('published_date', '')}"
    if all(key.split("\0")) and key in index["by_title_channel_date"]:
        return "title_channel_date", index["by_title_channel_date"][key], "title + channel + published_date already exists"
    content_hash = capture.get("content_hash", "")
    if content_hash and content_hash in index["by_content_hash"]:
        return "content_hash", index["by_content_hash"][content_hash], "transcript content_hash already exists"
    return "", "", ""


def _unique_capture_path(capture: dict[str, Any]) -> Path:
    date_part = _published_or_captured_date(capture)
    slug = slugify(capture.get("title", "untitled"), max_len=64)
    base = INBOX_YOUTUBE / f"{date_part}-{slug}.json"
    if not base.exists():
        return base
    for i in range(2, 1000):
        candidate = INBOX_YOUTUBE / f"{date_part}-{slug}-{i}.json"
        if not candidate.exists():
            return candidate
    raise YouTubeImportError(STATUS_FAILED_IMPORT, "could not allocate unique capture path")


def write_capture(capture: dict[str, Any]) -> Path:
    INBOX_YOUTUBE.mkdir(parents=True, exist_ok=True)
    path = _unique_capture_path(capture)
    path.write_text(json.dumps(capture, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def write_kb_entry(capture: dict[str, Any], bundle: dict[str, str]) -> Path:
    item_dir = item_dir_for_capture(capture)
    if item_dir.exists():
        raise YouTubeImportError(STATUS_FAILED_IMPORT, f"target article directory already exists: {item_dir.relative_to(KB_HOME).as_posix()}")
    item_dir.mkdir(parents=True)
    for name, text in bundle.items():
        (item_dir / name).write_text(text, encoding="utf-8")
    return item_dir


def build_capture_from_args(args: argparse.Namespace) -> dict[str, Any]:
    metadata_file = args.metadata_file or ""
    transcript_file = args.transcript_file or ""
    # Environment hooks let material_to_kb.py smoke tests route YouTube offline.
    import os
    metadata_file = metadata_file or os.environ.get("HERMES_YOUTUBE_FIXTURE_METADATA", "")
    transcript_file = transcript_file or os.environ.get("HERMES_YOUTUBE_FIXTURE_TRANSCRIPT", "")
    if metadata_file:
        transcript_path = Path(transcript_file) if transcript_file else None
        return load_fixture_capture(
            args.url,
            Path(metadata_file),
            transcript_path,
            preferred_language=args.language,
            prefer_auto=args.prefer_auto_captions,
            allow_auto=not args.no_auto_captions,
        )
    return fetch_youtube_capture(
        args.url,
        preferred_language=args.language,
        prefer_auto=args.prefer_auto_captions,
        allow_auto=not args.no_auto_captions,
        timeout=args.timeout,
    )


def _print_capture_summary(capture: dict[str, Any], capture_path: Path) -> None:
    rel = capture_path.relative_to(KB_HOME).as_posix()
    print(f"[capture] {rel}", file=sys.stderr)
    print(f"  title: {capture.get('title')}", file=sys.stderr)
    print(f"  channel: {capture.get('channel')}", file=sys.stderr)
    print(f"  video_id: {capture.get('video_id')}", file=sys.stderr)
    print(f"  published_date: {capture.get('published_date')}", file=sys.stderr)
    print(f"  transcript_language: {capture.get('transcript_language')}", file=sys.stderr)
    print(f"  transcript_kind: {capture.get('transcript_kind')}", file=sys.stderr)
    print(f"  transcript_chars: {len(capture.get('content_markdown', ''))}", file=sys.stderr)


def main() -> int:
    args = build_arg_parser().parse_args()
    dry_run = not args.do_import
    try:
        capture = build_capture_from_args(args)
        capture_path = write_capture(capture)
        _print_capture_summary(capture, capture_path)

        index = build_existing_index()
        dup_layer, duplicate_of, dup_reason = find_duplicate(capture, index)
        if duplicate_of:
            status = STATUS_DRY_RUN_DUPLICATE if dry_run else STATUS_SKIPPED_DUPLICATE
            print(f"DUPLICATE: {dup_reason}", file=sys.stderr)
            print(f"DUPLICATE_LAYER: {dup_layer}", file=sys.stderr)
            print(f"DUPLICATE_OF: {duplicate_of}", file=sys.stderr)
            print(f"\nSTATUS: {status}")
            return 0

        bundle = generate_output_bundle(capture)
        target_dir = item_dir_for_capture(capture)
        if dry_run:
            print("DRY RUN: Would create the following files:")
            print(f"  Directory: {target_dir}")
            for name, text in bundle.items():
                print(f"    - {name} ({len(text)} chars)")
            print(f"  Dedupe key: youtube:{capture.get('video_id', '')}")
            print(f"  Content hash: {capture.get('content_hash')}")
            print("\nSTATUS: DRY_RUN_OK")
            return 0

        item_dir = write_kb_entry(capture, bundle)
        print(f"SUCCESS: YouTube transcript imported to {item_dir}")
        print(f"  Dedupe key: youtube:{capture.get('video_id', '')}")
        print(f"  Content hash: {capture.get('content_hash')}")
        print("\nSTATUS: IMPORTED")
        return 0
    except YouTubeImportError as exc:
        print(f"{exc.status}: {exc.reason}", file=sys.stderr)
        print(f"\nSTATUS: {exc.status}", file=sys.stderr)
        return 1 if exc.status in {
            STATUS_BLOCKED_UNSUPPORTED,
            STATUS_BLOCKED_FETCH_FAILED,
            STATUS_BLOCKED_INCOMPLETE_TEXT,
        } else 3
    except Exception as exc:
        print(f"{STATUS_FAILED_IMPORT}: unhandled error: {exc}", file=sys.stderr)
        print(f"\nSTATUS: {STATUS_FAILED_IMPORT}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
