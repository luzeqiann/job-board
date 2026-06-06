"""Utilities for merge, dedup, metadata."""

import json
import logging
from pathlib import Path
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "jobs"
MERGED_PATH = PROJECT_ROOT / "data" / "merged.json"
META_PATH = PROJECT_ROOT / "data" / "meta.json"

TARGET_KEYWORDS = [
    "AI应用工程师", "RPA开发", "流程自动化", "智能客服", "AI训练师",
    "提示词工程", "对话机器人", "自动化测试", "低代码开发", "AI产品",
    "大模型应用",
]


def load_existing_jobs(source: str) -> list:
    fp = DATA_DIR / f"{source}.json"
    if fp.exists():
        try: return json.loads(fp.read_text(encoding="utf-8"))
        except: return []
    return []


def merge_and_deduplicate(new_jobs: list, source: str) -> list:
    """Replace existing data with new scrape. Jobs not in new scrape are removed."""
    old_map = {j["id"]: j for j in load_existing_jobs(source)}
    tz = timezone(timedelta(hours=8))
    now = datetime.now(tz).isoformat()
    new_count = 0

    merged = []
    for job in new_jobs:
        d = {
            "id": job.id, "company": job.company, "title": job.title,
            "location": job.location, "locationCity": job.location_city,
            "jobType": job.job_type, "category": job.category,
            "postDate": job.post_date, "collectDate": now, "isNew": False,
            "url": job.url, "description": job.description,
            "requirements": job.requirements, "salary": job.salary,
            "source": job.source, "sourceUrl": job.source_url, "tags": job.tags,
        }
        if job.id in old_map:
            d["collectDate"] = old_map[job.id].get("collectDate", now)
            d["isNew"] = old_map[job.id].get("isNew", False)
        else:
            d["isNew"] = True
            new_count += 1
        merged.append(d)

    removed = len(old_map) - len(merged)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / f"{source}.json").write_text(
        json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(f"[{source}] {len(merged)} total, {new_count} new, {removed} removed")
    return merged


def rebuild_merged() -> list:
    all_jobs = []
    for fp in sorted(DATA_DIR.glob("*.json")):
        if fp.name.startswith("."): continue
        try: all_jobs.extend(json.loads(fp.read_text(encoding="utf-8")))
        except: pass
    all_jobs.sort(key=lambda j: (j.get("postDate", ""), j.get("company", "")), reverse=True)
    MERGED_PATH.parent.mkdir(parents=True, exist_ok=True)
    MERGED_PATH.write_text(json.dumps(all_jobs, ensure_ascii=False, indent=2), encoding="utf-8")
    return all_jobs


def update_meta(status: dict, errors: list):
    tz = timezone(timedelta(hours=8))
    all_jobs = rebuild_merged()
    meta = {
        "lastRun": datetime.now(tz).isoformat(),
        "totalJobs": len(all_jobs),
        "newJobsThisRun": sum(1 for j in all_jobs if j.get("isNew")),
        "statusPerSource": status,
        "errors": errors,
    }
    META_PATH.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def cleanup_old_new_flags(days: int = 3):
    cutoff = datetime.now(timezone(timedelta(hours=8))) - timedelta(days=days)
    for fp in DATA_DIR.glob("*.json"):
        if fp.name.startswith("."): continue
        try: jobs = json.loads(fp.read_text(encoding="utf-8"))
        except: continue
        changed = False
        for j in jobs:
            if j.get("isNew"):
                try:
                    cd = datetime.fromisoformat(j.get("collectDate", ""))
                    if cd < cutoff: j["isNew"] = False; changed = True
                except: pass
        if changed:
            fp.write_text(json.dumps(jobs, ensure_ascii=False, indent=2), encoding="utf-8")
