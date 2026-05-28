"""
AI Info Distillery Runner
"""
import os, yaml
from datetime import datetime
from pathlib import Path

# 导入 news-summary 的 fetcher
from src.fetchers import fetch_rss, fetch_youtube, fetch_youtube_transcript
from src.fetchers.base import RawItem

# 导入我们的模块
from pipeline.review_gate import generate_daily_brief, save_brief, render_brief_markdown
from pipeline.crawler.bilibili_fetcher import fetch_bilibili_with_subtitles
from pipeline.crawler.xiaoyuzhou_fetcher import fetch_xiaoyuzhou_podcast

def get_llm_client():
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    base_url = os.environ.get("ANTHROPIC_BASE_URL", "")
    if not api_key:
        print("未配置 LLM，使用规则提取")
        return None
    import openai
    kwargs = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    return openai.OpenAI(**kwargs)

def load_config(path):
    if not Path(path).exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def fetch_all():
    items = []
    # 主配置
    for src in load_config("sources.yaml").get("sources", []):
        stype = src.get("type", "rss")
        name = src.get("name", "未命名")
        max_e = min(src.get("max_entries", 3), 5)
        try:
            if stype == "rss":
                items.extend(fetch_rss(src.get("url",""), name, max_entries=max_e, fetch_fulltext=src.get("fetch_fulltext", False)))
            elif stype == "youtube":
                items.extend(fetch_youtube(src.get("url",""), name))
            elif stype == "youtube_transcript":
                items.extend(fetch_youtube_transcript(src.get("url",""), name))
        except Exception as e:
            items.append(RawItem(source_name=name, source_type=stype, title="[抓取失败]", content=str(e), link=src.get("url","")))
    # B站
    for src in load_config("config/bilibili_xiaoyuzhou_sources.yaml").get("bilibili_sources", []):
        uid = src.get("uid", "")
        name = src.get("name", "未命名")
        if uid:
            try:
                items.extend(fetch_bilibili_with_subtitles(uid, name, max_entries=3))
            except Exception as e:
                items.append(RawItem(source_name=name, source_type="bilibili", title="[B站抓取失败]", content=str(e)))
    # 小宇宙
    for src in load_config("config/bilibili_xiaoyuzhou_sources.yaml").get("xiaoyuzhou_sources", []):
        rss = src.get("rss_url", "")
        name = src.get("name", "未命名")
        if rss:
            try:
                items.extend(fetch_xiaoyuzhou_podcast(rss, name, max_entries=3))
            except Exception as e:
                items.append(RawItem(source_name=name, source_type="xiaoyuzhou", title="[小宇宙抓取失败]", content=str(e)))
    return items

if __name__ == "__main__":
    print("=== 抓取信息源 ===")
    items = fetch_all()
    print(f"抓取到 {len(items)} 条内容")

    print("=== 生成简报 ===")
    date = datetime.now().strftime("%Y-%m-%d")
    brief = generate_daily_brief(items, date)
    path = save_brief(brief)
    print(f"简报保存到: {path}")

    md = render_brief_markdown(brief)
    Path("briefs").joinpath(f"{date}.md").write_text(md, encoding="utf-8")
    print(f"包含 {len(brief.items)} 条内容")
