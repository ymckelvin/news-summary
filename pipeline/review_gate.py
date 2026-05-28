import json, hashlib
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class BriefItem:
    id: str
    title: str
    summary: str
    source_platform: str
    source_url: str
    source_name: str
    content_type: str
    ai_subfield: str
    speaker_identity: str
    speaker_name: str
    language: str
    duration_or_length: str
    heat_score: str
    tags: list
    has_transcript: bool
    status: str
    raw_content_path: Optional[str] = None
    briefed_at: str = ""
    def __post_init__(self):
        if not self.briefed_at:
            self.briefed_at = datetime.now().isoformat()

@dataclass
class DailyBrief:
    date: str
    items: list
    generated_at: str = ""
    def __post_init__(self):
        if not self.generated_at:
            self.generated_at = datetime.now().isoformat()

def generate_item_id(source_name, title, date):
    raw = f"{source_name}:{title}:{date}"
    return f"aid_{date}_{hashlib.md5(raw.encode()).hexdigest()[:8]}"

def classify_content_type(raw_type, title=""):
    mapping = {"youtube": "interview", "youtube_transcript": "interview", "rss": "tech_share",
               "twitter": "opinion", "bilibili": "tech_share", "xiaoyuzhou": "interview"}
    return mapping.get(raw_type, "tech_share")

def classify_ai_subfield(source_name, title=""):
    keywords_map = {
        "infrastructure": ["model", "llm", "training", "gpu", "chip", "基础", "算力"],
        "application": ["product", "app", "tool", "agent", "应用", "产品"],
        "tools": ["sdk", "api", "framework", "工具", "开发"],
        "ethics": ["safety", "alignment", "安全", "伦理"],
        "business": ["startup", "vc", "fund", "invest", "商业", "投资"],
    }
    text = f"{source_name} {title}".lower()
    for subfield, keywords in keywords_map.items():
        if any(kw in text for kw in keywords):
            return subfield
    return "application"

def classify_speaker_identity(source_name, title=""):
    keywords_map = {
        "bigco_exec": ["ceo", "cto", "vp", "head", "负责人", "高管"],
        "startup_founder": ["founder", "创始人"],
        "researcher": ["researcher", "phd", "professor", "研究员"],
        "investor": ["vc", "fund", "capital", "投资人"],
    }
    text = f"{source_name} {title}".lower()
    for identity, keywords in keywords_map.items():
        if any(kw in text for kw in keywords):
            return identity
    return "unknown"

def rawitem_to_briefitem(raw, date):
    return BriefItem(
        id=generate_item_id(raw.source_name, raw.title, date),
        title=raw.title,
        summary=(raw.content or "")[:200],
        source_platform=raw.source_type,
        source_url=raw.link or "",
        source_name=raw.source_name,
        content_type=classify_content_type(raw.source_type, raw.title),
        ai_subfield=classify_ai_subfield(raw.source_name, raw.title),
        speaker_identity=classify_speaker_identity(raw.source_name, raw.title),
        speaker_name="",
        language="en" if any(c in (raw.content or "") for c in ["the ", "is ", "and "]) else "zh",
        duration_or_length=str(len(raw.content or "")),
        heat_score="0",
        tags=[],
        has_transcript=bool(raw.content and len(raw.content) > 100),
        status="pending",
        raw_content_path=None,
    )

def generate_daily_brief(raw_items, date=None):
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    brief_items = []
    for raw in raw_items:
        item = rawitem_to_briefitem(raw, date)
        if raw.content:
            content_dir = Path("briefs") / date / "raw"
            content_dir.mkdir(parents=True, exist_ok=True)
            content_path = content_dir / f"{item.id}.txt"
            content_path.write_text(raw.content, encoding="utf-8")
            item.raw_content_path = str(content_path)
        brief_items.append(item)
    return DailyBrief(date=date, items=brief_items)

def save_brief(brief, output_dir="briefs"):
    dir_path = Path(output_dir)
    dir_path.mkdir(parents=True, exist_ok=True)
    file_path = dir_path / f"{brief.date}.json"
    data = {"date": brief.date, "generated_at": brief.generated_at, "items": [asdict(item) for item in brief.items]}
    file_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return file_path

def load_brief(date, input_dir="briefs"):
    file_path = Path(input_dir) / f"{date}.json"
    data = json.loads(file_path.read_text(encoding="utf-8"))
    items = [BriefItem(**item) for item in data["items"]]
    return DailyBrief(date=data["date"], items=items, generated_at=data.get("generated_at",""))

def mark_items(brief, selections):
    for item in brief.items:
        if item.id in selections:
            item.status = selections[item.id]
    return brief

def get_selected_items(brief):
    return [item for item in brief.items if item.status == "selected"]

def render_brief_markdown(brief):
    lines = [f"# AI 简报 — {brief.date}", f"共 {len(brief.items)} 条", ""]
    groups = {}
    for item in brief.items:
        key = item.ai_subfield
        if key not in groups: groups[key] = []
        groups[key].append(item)
    for subfield, items in groups.items():
        lines.append(f"## {subfield}")
        for item in items:
            lines.append(f"- **{item.title}**")
            lines.append(f"  - {item.summary[:80]}")
            lines.append(f"  - 来源: {item.source_name} | ID: `{item.id}`")
            if item.source_url: lines.append(f"  - [原文]({item.source_url})")
            lines.append("")
    lines.append("---")
    lines.append("回复「我要听 ID1, ID2」选择内容")
    return "\n".join(lines)
