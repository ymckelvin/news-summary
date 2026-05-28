"""MyFlicker 集成"""
import json, requests
from datetime import datetime

GITHUB_REPO = "ymckelvin/news-summary"
BRIEF_BRANCH = "main"

def fetch_brief_from_github(date=None):
    if not date: date = datetime.now().strftime("%Y-%m-%d")
    url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{BRIEF_BRANCH}/briefs/{date}.json"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200: return r.json()
    except: pass
    return None

def format_brief_for_kim(brief_data):
    items = brief_data.get("items", [])
    date = brief_data.get("date", "")
    lines = [f"📋 AI 简报 — {date}", f"共 {len(items)} 条", ""]
    for i, item in enumerate(items[:20], 1):
        lines.append(f"{i}. {item['title']}")
        lines.append(f"   来源: {item['source_name']} | ID: {item['id']}")
        lines.append("")
    lines.append("回复「我要听 ID1, ID2」选择")
    return "\n".join(lines)
