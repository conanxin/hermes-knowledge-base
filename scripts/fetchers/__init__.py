"""Material fetch layer adapters."""

from __future__ import annotations

from .wechat_fetcher import WeChatFetcher
from .web_fetcher import WebFetcher
from .youtube_fetcher import YouTubeFetcher


def fetcher_for(route_kind: str, route_flag: str = ""):
    if route_kind == "wechat":
        return WeChatFetcher(route_flag=route_flag)
    if route_kind == "web":
        return WebFetcher(route_flag=route_flag)
    if route_kind == "youtube":
        return YouTubeFetcher(route_flag=route_flag)
    return None
