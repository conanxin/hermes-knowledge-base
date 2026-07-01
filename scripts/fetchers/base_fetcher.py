"""Base interface and helpers for material fetchers."""

from __future__ import annotations

from typing import Any


FETCH_OK = "ok"
FETCH_PARTIAL = "partial"
FETCH_BLOCKED = "blocked"

QUALITY_FULL = "full"
QUALITY_PARTIAL = "partial"
QUALITY_METADATA_ONLY = "metadata_only"
QUALITY_NONE = "none"


class BaseFetcher:
    def fetch(self, source: str) -> dict[str, Any]:
        """
        Return a normalized material fetch result:
        {
            "title": str,
            "text": str,
            "images": [],
            "metadata": {},
            "status": "ok | partial | blocked",
            "reason": "",
            "fetch_quality": "full | partial | metadata_only"
        }
        """
        raise NotImplementedError

    def ok(
        self,
        title: str,
        text: str,
        *,
        images: list[Any] | None = None,
        metadata: dict[str, Any] | None = None,
        reason: str = "",
        fetch_quality: str = QUALITY_FULL,
    ) -> dict[str, Any]:
        return self._result(title, text, images, metadata, FETCH_OK, reason, fetch_quality)

    def partial(
        self,
        title: str,
        text: str,
        *,
        images: list[Any] | None = None,
        metadata: dict[str, Any] | None = None,
        reason: str = "",
        fetch_quality: str = QUALITY_PARTIAL,
    ) -> dict[str, Any]:
        return self._result(title, text, images, metadata, FETCH_PARTIAL, reason, fetch_quality)

    def blocked(
        self,
        reason: str,
        *,
        title: str = "",
        text: str = "",
        images: list[Any] | None = None,
        metadata: dict[str, Any] | None = None,
        fetch_quality: str = QUALITY_NONE,
    ) -> dict[str, Any]:
        return self._result(title, text, images, metadata, FETCH_BLOCKED, reason, fetch_quality)

    def _result(
        self,
        title: str,
        text: str,
        images: list[Any] | None,
        metadata: dict[str, Any] | None,
        status: str,
        reason: str,
        fetch_quality: str,
    ) -> dict[str, Any]:
        return {
            "title": title or "",
            "text": text or "",
            "images": images or [],
            "metadata": metadata or {},
            "status": status,
            "reason": reason or "",
            "fetch_quality": fetch_quality or QUALITY_NONE,
        }
