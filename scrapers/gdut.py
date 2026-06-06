"""GDUT (广东工业大学) career center scraper.

Targets: https://career.gdut.edu.cn

Scrapes job listings posted on GDUT's employment portal. This is a goldmine
because it aggregates ALL companies recruiting at GDUT, including:
- Tech companies (腾讯, 字节, 中厂, etc.)
- State-owned enterprises (央国企)
- Local Guangzhou/Shenzhen companies

Strategy:
1. Search by keywords (AI, RPA, 自动化, etc.) via /search/list
2. Parse the paginated search results (HTML, server-rendered)
3. For each result, fetch the detail page to get company/location/salary
4. Filter by location (广州, 深圳)
"""

import logging
import re
from datetime import datetime, timezone, timedelta
from typing import Optional
from bs4 import BeautifulSoup

from scrapers.base import BaseScraper, ScraperConfig, JobResult

logger = logging.getLogger(__name__)

GDUT_BASE = "https://career.gdut.edu.cn"
SEARCH_URL = f"{GDUT_BASE}/search/list"

# Keywords to search for
SEARCH_KEYWORDS = [
    "AI", "人工智能", "大模型", "RPA", "自动化",
    "智能客服", "提示词", "Agent", "低代码",
    "机器人", "语音", "NLP", "机器学习",
]

# Map job categories to our standard categories
CATEGORY_MAP = [
    ("AI应用工程师", ["ai应用", "应用开发", "ai开发", "ai工程师"]),
    ("RPA开发", ["rpa", "机器人流程", "自动化流程"]),
    ("智能客服", ["智能客服", "对话机器人"]),
    ("AI训练师", ["训练师", "数据标注", "ai训练"]),
    ("提示词工程", ["提示词", "prompt"]),
    ("大模型应用", ["大模型", "llm", "模型应用"]),
    ("对话机器人", ["聊天机器人", "chatbot"]),
    ("自动化测试", ["自动化测试"]),
    ("低代码开发", ["低代码"]),
    ("AI产品", ["ai产品", "产品经理"]),
]

TAG_WORDS = [
    "AI", "大模型", "GPT", "LLM", "Agent", "Python",
    "RPA", "机器学习", "深度学习", "NLP",
]


class GdutScraper(BaseScraper):
    """GDUT career center scraper using HTML parsing."""

    def __init__(self):
        config = ScraperConfig(
            name="gdut",
            company_display="广工就业网",
            source_url=GDUT_BASE,
            min_delay=1.0,  # School site — lighter rate limiting
            max_delay=3.0,
            use_playwright=False,
        )
        super().__init__(config)

    async def _get_page(self, url: str) -> str:
        """Fetch HTML page with retry."""
        last_error = None
        for attempt in range(3):
            try:
                await self._rate_limit()
                async with self.session.get(url, timeout=self.config.timeout) as resp:
                    resp.raise_for_status()
                    text = await resp.text()
                    return text
            except Exception as e:
                last_error = e
                wait = 2 ** attempt
                logger.warning(f"[gdut] Attempt {attempt+1}/3 for {url}: {e}")
                await self._rate_limit()
        raise last_error

    async def fetch_job_ids(self) -> list:
        """Search for matching jobs across all keywords and pages.

        Returns list of tuples: (job_id, title, date_str) combined from search results.
        """
        all_results = []  # list of {"id": ..., "title": ..., "date": ...}
        seen_ids = set()

        for kw in SEARCH_KEYWORDS:
            page = 1
            while page <= 5:  # max 5 pages per keyword
                url = (
                    f"{SEARCH_URL}/keyword/{kw}"
                    f"/do123/career.gdut.edu.cn/domain/gdut"
                    f"?type=1"  # 职位信息 only
                )
                if page > 1:
                    url += f"&page={page}"

                try:
                    html = await self._get_page(url)
                except Exception as e:
                    logger.error(f"[gdut] Failed search '{kw}' page {page}: {e}")
                    break

                soup = BeautifulSoup(html, "lxml")
                items = soup.select("ul.pub-list li.clearfix")
                if not items:
                    break

                for item in items:
                    link = item.select_one("p.css-title a")
                    date_el = item.select_one("p:last-child")
                    if not link:
                        continue

                    href = link.get("href", "")
                    title = link.get_text(strip=True)
                    # Clean highlighted keyword markers
                    title = re.sub(r"<[^>]*>", "", title) if "<" in title else title

                    match = re.search(r"/job/view/id/(\d+)", href)
                    if not match:
                        continue
                    job_id = match.group(1)

                    date_str = ""
                    if date_el:
                        date_text = date_el.get_text(strip=True)
                        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", date_text)
                        if date_match:
                            date_str = date_match.group(1)

                    if job_id not in seen_ids:
                        seen_ids.add(job_id)
                        all_results.append({
                            "id": job_id,
                            "title": title,
                            "date": date_str,
                        })

                logger.info(
                    f"[gdut] Search '{kw}' page {page}: {len(items)} items "
                    f"(total unique: {len(all_results)})"
                )

                # Check if there's a next page
                next_link = soup.select_one("li.next:not(.hidden) a")
                if not next_link:
                    break
                page += 1

        logger.info(f"[gdut] Total unique jobs found: {len(all_results)}")
        return all_results

    async def parse_job_detail(self, job_info: dict) -> Optional[JobResult]:
        """Parse a single job detail page."""
        job_id = job_info["id"]
        title_from_list = job_info.get("title", "")
        date_from_list = job_info.get("date", "")

        url = f"{GDUT_BASE}/job/view/id/{job_id}"
        try:
            html = await self._get_page(url)
        except Exception as e:
            logger.warning(f"[gdut] Failed to fetch detail {job_id}: {e}")
            return None

        soup = BeautifulSoup(html, "lxml")

        # Title
        title_el = soup.select_one("span.title, .details-title h5")
        title = title_el.get_text(strip=True) if title_el else title_from_list

        # Company
        company_el = soup.select_one(".unit-info a[href*='/company/view/']")
        company = company_el.get_text(strip=True) if company_el else "未知公司"

        # Location
        location = ""
        location_city = "其他"
        edu_el = soup.select_one("span.education")
        if edu_el:
            location_text = edu_el.get_text(separator=" ", strip=True)
            location = location_text
            if "广州" in location_text:
                location_city = "广州"
            elif "深圳" in location_text:
                location_city = "深圳"

        # Salary
        salary_el = soup.select_one("span.salary")
        salary = salary_el.get_text(strip=True) if salary_el else "面议"

        # Job type (实习/全职)
        job_type = "社招"  # default
        if edu_el:
            edu_text = edu_el.get_text(strip=True)
            if "实习" in edu_text:
                job_type = "实习"
            elif "全职" in edu_text or "校招" in edu_text:
                job_type = "校招"

        # Category (职能类别)
        category = "AI相关"
        cat_el = soup.select_one(".details-list li")
        if cat_el:
            cat_text = cat_el.get_text(strip=True)
            for cat, kws in CATEGORY_MAP:
                if any(kw in cat_text.lower() for kw in kws):
                    category = cat
                    break
            # Also check title
            if category == "AI相关":
                full_text = f"{title} {cat_text}".lower()
                for cat, kws in CATEGORY_MAP:
                    if any(kw in full_text for kw in kws):
                        category = cat
                        break

        # Post date
        post_date = date_from_list
        if not post_date:
            date_el = soup.select_one(".share li:first-child")
            if date_el:
                date_text = date_el.get_text(strip=True)
                date_match = re.search(r"(\d{4}-\d{2}-\d{2})", date_text)
                if date_match:
                    post_date = date_match.group(1)
        if not post_date:
            post_date = datetime.now().strftime("%Y-%m-%d")

        # Description and requirements
        description = ""
        requirements = ""
        desc_el = soup.select_one(".details-mge .aContent")
        if desc_el:
            description = desc_el.get_text(separator="\n", strip=True)[:3000]
        # Requirements usually embedded in description
        req_match = re.search(
            r"(?:任职要求|岗位要求|职位要求|任职资格)[：:]?\s*(.*?)(?:\n\n|\Z)",
            description, re.DOTALL
        )
        if req_match:
            requirements = req_match.group(1).strip()[:1000]
        else:
            requirements = description[:500]

        # Tags
        full_text = f"{title} {description}"
        tags = [tw for tw in TAG_WORDS if tw.lower() in full_text.lower()]

        return JobResult(
            id=f"gdut_{job_id}",
            company=company,
            title=title,
            location=location,
            location_city=location_city,
            job_type=job_type,
            category=category,
            post_date=post_date,
            collect_date=datetime.now(timezone(timedelta(hours=8))).isoformat(),
            is_new=False,
            url=url,
            description=description[:5000],
            requirements=requirements,
            salary=salary,
            source="gdut",
            source_url=GDUT_BASE,
            tags=tags,
        )
