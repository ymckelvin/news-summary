import re, json, subprocess
from pathlib import Path
from typing import Optional
import feedparser
from .base import RawItem

def fetch_bilibili_rss(uid, source_name, max_entries=3):
    rss_url = f"https://rsshub.app/bilibili/user/video/{uid}"
    items = []
    try:
        feed = feedparser.parse(rss_url, request_headers={"User-Agent": "AIDistillery/1.0"})
        for entry in feed.entries[:max_entries]:
            title = entry.get("title", "(无标题)")
            link = entry.get("link", "")
            published = entry.get("published", "")
            summary = entry.get("summary", "")
            items.append(RawItem(source_name=source_name, source_type="bilibili",
                title=title, content=(summary or title)[:5000], link=link, published=published))
    except Exception as e:
        items.append(RawItem(source_name=source_name, source_type="bilibili",
            title="[B站抓取失败]", content=str(e), link=f"https://space.bilibili.com/{uid}"))
    return items

def fetch_bilibili_with_subtitles(uid, source_name, max_entries=3):
    return fetch_bilibili_rss(uid, source_name, max_entries)
