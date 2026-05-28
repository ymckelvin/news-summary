import feedparser
from .base import RawItem

def fetch_xiaoyuzhou_podcast(rss_url, source_name, max_entries=3):
    items = []
    try:
        feed = feedparser.parse(rss_url, request_headers={"User-Agent": "AIDistillery/1.0"})
        for entry in feed.entries[:max_entries]:
            title = entry.get("title", "(无标题)")
            link = entry.get("link", "")
            published = entry.get("published", "")
            summary = entry.get("summary", entry.get("description", ""))
            items.append(RawItem(source_name=source_name, source_type="xiaoyuzhou",
                title=title, content=(summary or title)[:5000], link=link, published=published))
    except Exception as e:
        items.append(RawItem(source_name=source_name, source_type="xiaoyuzhou",
            title="[小宇宙抓取失败]", content=str(e), link=rss_url))
    return items

def fetch_xiaoyuzhou_with_transcript(rss_url, source_name, max_entries=3, whisper_model="base"):
    return fetch_xiaoyuzhou_podcast(rss_url, source_name, max_entries)
