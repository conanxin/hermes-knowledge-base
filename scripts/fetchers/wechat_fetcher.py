"""WeChat material fetcher adapter."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .base_fetcher import BaseFetcher

import wechat_url_to_kb as wechat  # type: ignore


class WeChatFetcher(BaseFetcher):
    def __init__(self, route_flag: str = ""):
        self.route_flag = route_flag

    def fetch(self, source: str) -> dict[str, Any]:
        try:
            capture = self._capture(source)
        except Exception as exc:
            return self.blocked(
                str(exc),
                metadata={"error_status": "BLOCKED_FETCH_FAILED" if "network" in str(exc).lower() else "BLOCKED_INCOMPLETE_TEXT"},
            )
        text = capture.get("content_markdown", "")
        if not text.strip():
            return self.blocked("WeChat fetch produced no article text", metadata={"capture": capture, "error_status": "BLOCKED_INCOMPLETE_TEXT"})
        images = []
        if capture.get("cover_url"):
            images.append({"url": capture["cover_url"], "source": "cover"})
        return self.ok(
            capture.get("title", ""),
            text,
            images=images,
            metadata={"capture": capture, "source_platform": "wechat"},
        )

    def _capture(self, source: str) -> dict[str, Any]:
        if source.startswith(("http://", "https://")):
            html, final_url, status_code = wechat.fetch_url_html(source)
            if status_code != 200:
                raise RuntimeError(f"non-200 HTTP status from WeChat: {status_code}")
            return wechat.parse_wechat_html(html, final_url or source)
        if self.route_flag == "--html-file" or source.lower().endswith((".html", ".htm")):
            return wechat.parse_html_file(Path(source))
        if self.route_flag == "--markdown-file" or source.lower().endswith((".md", ".markdown")):
            return wechat.parse_markdown_file(Path(source))
        if self.route_flag == "--text-file" or source.lower().endswith(".txt"):
            return wechat.parse_text_file(Path(source))
        raise RuntimeError("unsupported WeChat source")
