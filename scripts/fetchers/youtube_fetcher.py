"""YouTube material fetcher adapter with partial fallback."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .base_fetcher import BaseFetcher, QUALITY_FULL, QUALITY_METADATA_ONLY, QUALITY_PARTIAL

import youtube_to_kb as youtube  # type: ignore


class YouTubeFetcher(BaseFetcher):
    def __init__(self, route_flag: str = ""):
        self.route_flag = route_flag

    def fetch(self, source: str) -> dict[str, Any]:
        try:
            capture = self._capture(source)
        except youtube.YouTubeImportError as exc:
            return self.blocked(str(exc), metadata={"error_status": exc.status})
        except Exception as exc:
            return self.blocked(str(exc), metadata={"error_status": "BLOCKED_FETCH_FAILED"})

        import_allowed, import_block_reason, warning = youtube.evaluate_import_quality(
            capture,
            allow_partial=False,
            allow_auto_captions=False,
        )
        capture["transcript_char_count"] = youtube.transcript_char_count(capture)
        capture["import_allowed"] = import_allowed
        capture["import_block_reason"] = import_block_reason
        if warning:
            capture["warning"] = warning

        text = capture.get("content_markdown", "") or capture.get("transcript_text", "")
        quality = capture.get("fetch_quality") or QUALITY_FULL
        status_reason = capture.get("fetch_reason", "")
        metadata = {
            "capture": capture,
            "source_platform": "youtube",
            "video_id": capture.get("video_id", ""),
            "transcript_kind": capture.get("transcript_kind", ""),
            "transcript_language": capture.get("transcript_language", ""),
            "provider_attempts": capture.get("provider_attempts", []),
        }
        images = []
        if capture.get("thumbnail_url"):
            images.append({"url": capture["thumbnail_url"], "source": "thumbnail"})
        if not text.strip():
            return self.blocked("YouTube fetch produced no metadata or transcript text", metadata={**metadata, "error_status": "BLOCKED_INCOMPLETE_TEXT"})
        if quality in {QUALITY_PARTIAL, QUALITY_METADATA_ONLY}:
            return self.partial(capture.get("title", ""), text, images=images, metadata=metadata, reason=status_reason, fetch_quality=quality)
        return self.ok(capture.get("title", ""), text, images=images, metadata=metadata, fetch_quality=quality)

    def _capture(self, source: str) -> dict[str, Any]:
        metadata_file = os.environ.get("HERMES_YOUTUBE_FIXTURE_METADATA", "")
        transcript_file = os.environ.get("HERMES_YOUTUBE_FIXTURE_TRANSCRIPT", "")
        if metadata_file:
            transcript_path = Path(transcript_file) if transcript_file else None
            return youtube.load_fixture_capture(
                source,
                Path(metadata_file),
                transcript_path,
                preferred_language="",
                prefer_auto=False,
                allow_auto=True,
                caption_provider=os.environ.get("HERMES_YOUTUBE_CAPTION_PROVIDER", "auto"),
            )
        return youtube.fetch_youtube_capture(
            source,
            preferred_language="",
            prefer_auto=False,
            allow_auto=True,
            timeout=20,
            caption_provider=os.environ.get("HERMES_YOUTUBE_CAPTION_PROVIDER", "auto"),
        )
