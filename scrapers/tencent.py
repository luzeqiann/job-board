"""Tencent career scraper using public REST API."""

import logging
import re
from datetime import datetime, timezone, timedelta
from typing import Optional
from scrapers.base import BaseScraper, ScraperConfig, JobResult

logger = logging.getLogger(__name__)

TENCENT_KEYWORDS = [
    "AI", "人工智能", "大模型", "机器学习", "深度学习",
    "RPA", "自动化", "流程", "智能客服", "对话", "机器人",
    "提示词", "Prompt", "Agent", "智能体",
    "训练师", "标注", "低代码", "应用",
]

TENCENT_LIST_API = "https://careers.tencent.com/tencentcareer/api/post/Query"
TENCENT_DETAIL_API = "https://careers.tencent.com/tencentcareer/api/post/ByPostId"

CATEGORY_MAP = [
    ("AI应用工程师", ["ai应用", "ai产品应用", "应用工程师"]),
    ("RPA开发", ["rpa", "机器人流程", "uipath", "影刀"]),
    ("智能客服", ["智能客服", "对话机器人", "客服机器人"]),
    ("AI训练师", ["训练师", "数据标注"]),
    ("提示词工程", ["提示词", "prompt engineer", "prompt"]),
    ("大模型应用", ["大模型应用", "大模型开发", "llm应用", "大模型"]),
    ("对话机器人", ["聊天机器人", "chatbot"]),
    ("自动化测试", ["自动化测试"]),
    ("低代码开发", ["低代码"]),
    ("AI产品", ["ai产品"]),
]

TAG_WORDS = [
    "AI", "大模型", "GPT", "LLM", "RAG", "Agent", "Coze",
    "Python", "RPA", "影刀", "UiPath", "LangChain",
    "NLP", "机器学习", "深度学习", "PyTorch", "Docker",
]


class TencentScraper(BaseScraper):
    def __init__(self):
        config = ScraperConfig(
            name="tencent",
            company_display="腾讯",
            source_url="https://careers.tencent.com",
            min_delay=2.0,
            max_delay=4.0,
        )
        super().__init__(config)

    async def fetch_job_ids(self) -> list:
        all_posts = []
        page = 1
        while page <= 20:
            payload = {
                "timestamp": int(datetime.now().timestamp() * 1000),
                "countryId": 1, "cityId": 0, "bgIds": [],
                "productId": [], "categoryId": [], "parentCategoryId": [],
                "attrId": [], "keyword": "",
                "pageIndex": page, "pageSize": 30,
                "language": "zh-cn", "area": "cn",
            }
            try:
                data = await self._retry_post(TENCENT_LIST_API, json=payload)
            except Exception as e:
                logger.error(f"[tencent] API failed page {page}: {e}")
                break
            if data.get("Status") != "SUCCESS":
                break
            posts = data.get("Data", {}).get("Posts", [])
            if not posts:
                break
            all_posts.extend(posts)
            logger.info(f"[tencent] Page {page}: {len(posts)} posts (total {len(all_posts)})")
            page += 1

        matched = []
        for post in all_posts:
            title = post.get("RecruitPostName", "")
            location = post.get("LocationName", "")
            if self._title_matches(title) and self._location_matches(location):
                matched.append(post)
        logger.info(f"[tencent] Total {len(all_posts)}, matched {len(matched)}")
        return matched

    async def parse_job_detail(self, post_data: dict) -> Optional[JobResult]:
        post_id = post_data.get("PostId")
        description = ""
        requirements = ""
        try:
            detail_url = f"{TENCENT_DETAIL_API}?postId={post_id}&language=zh-cn"
            async with self.session.get(detail_url, timeout=self.config.timeout) as resp:
                detail_data = await resp.json()
                if detail_data.get("Status") == "SUCCESS":
                    d = detail_data.get("Data", {})
                    description = d.get("Responsibility", "") or ""
                    requirements = d.get("Requirement", "") or ""
        except Exception:
            description = post_data.get("Responsibility", "") or ""
            requirements = post_data.get("Requirement", "") or ""

        title = post_data.get("RecruitPostName", "")
        location = post_data.get("LocationName", "")
        bg = post_data.get("BGName", "")
        recruit_type = post_data.get("RecruitTypeName", "")

        return JobResult(
            id=f"tencent_{post_id}",
            company="腾讯",
            title=f"{title}（{bg}）" if bg else title,
            location=location,
            location_city=self._city(location),
            job_type="校招" if "校园" in str(recruit_type) else "社招",
            category=self._classify(title, description, requirements),
            post_date=self._parse_date(post_data.get("LastUpdateTime", "")),
            collect_date=datetime.now(timezone(timedelta(hours=8))).isoformat(),
            is_new=False,
            url=f"https://careers.tencent.com/job/detail?id={post_id}",
            description=description,
            requirements=requirements,
            salary=post_data.get("Salary", "面议") or "面议",
            source="tencent",
            source_url=self.config.source_url,
            tags=self._tags(title, description, requirements),
        )

    @staticmethod
    def _title_matches(t: str) -> bool:
        return any(kw.lower() in (t or "").lower() for kw in TENCENT_KEYWORDS)

    @staticmethod
    def _location_matches(loc: str) -> bool:
        return "广州" in str(loc) or "深圳" in str(loc)

    @staticmethod
    def _city(loc: str) -> str:
        if not loc: return "未知"
        if "广州" in loc: return "广州"
        if "深圳" in loc: return "深圳"
        return "其他"

    @staticmethod
    def _classify(title, desc, reqs) -> str:
        text = f"{title} {desc or ''} {reqs or ''}".lower()
        for cat, kws in CATEGORY_MAP:
            if any(kw in text for kw in kws):
                return cat
        return "AI相关"

    @staticmethod
    def _tags(title, desc, reqs) -> list:
        text = f"{title} {desc or ''} {reqs or ''}".lower()
        return [tw for tw in TAG_WORDS if tw.lower() in text]

    @staticmethod
    def _parse_date(s: str) -> str:
        if not s: return datetime.now().strftime("%Y-%m-%d")
        for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"]:
            try: return datetime.strptime(s[:10], fmt[:10]).strftime("%Y-%m-%d")
            except ValueError: continue
        m = re.search(r"(\d+)天前", s)
        if m: return (datetime.now() - timedelta(days=int(m.group(1)))).strftime("%Y-%m-%d")
        return datetime.now().strftime("%Y-%m-%d")
