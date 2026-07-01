"""Generic web article material fetcher adapter."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .base_fetcher import BaseFetcher

import web_article_to_kb as web_article  # type: ignore


class WebFetcher(BaseFetcher):
    def __init__(self, route_flag: str = ""):
        self.route_flag = route_flag

    def fetch(self, source: str) -> dict[str, Any]:
        try:
            capture = self._capture(source)
        except web_article.WebArticleError as exc:
            return self.blocked(str(exc), metadata={"error_status": exc.status})
        except Exception as exc:
            return self.blocked(str(exc), metadata={"error_status": "BLOCKED_FETCH_FAILED"})
        text = capture.get("content_markdown", "")
        if not text.strip():
            return self.blocked("web fetch produced no article text", metadata={"capture": capture, "error_status": "BLOCKED_INCOMPLETE_TEXT"})
        return self.ok(
            capture.get("title", ""),
            text,
            images=capture.get("images", []),
            metadata={
                "capture": capture,
                "source_platform": "web",
                "extraction_method": capture.get("extraction_method", ""),
            },
        )

    def _capture(self, source: str) -> dict[str, Any]:
        if source.startswith(("http://", "https://")):
            html, final_url = web_article.fetch_url_html(source)
            return web_article.parse_html_capture(html, source_url=source, final_url=final_url)
        path = Path(source)
        suffix = path.suffix.lower()
        if self.route_flag == "--html-file" or suffix in {".html", ".htm"}:
            html = path.read_text(encoding="utf-8", errors="replace")
            return web_article.parse_html_capture(html, source_url=path.resolve().as_uri(), final_url=path.resolve().as_uri())
        if self.route_flag == "--markdown-file" or suffix in {".md", ".markdown"}:
            return web_article.parse_markdown_capture(path)
        if self.route_flag == "--text-file" or suffix == ".txt":
            return web_article.parse_text_capture(path)
        raise web_article.WebArticleError(web_article.STATUS_BLOCKED_UNSUPPORTED, "unsupported web source")
