"""Abstract base class for all company scrapers."""

import asyncio
import logging
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class ScraperConfig:
    name: str
    company_display: str
    source_url: str
    min_delay: float = 2.0
    max_delay: float = 5.0
    max_retries: int = 3
    timeout: int = 30
    use_playwright: bool = False
    enabled: bool = True


@dataclass
class JobResult:
    id: str
    company: str
    title: str
    location: str
    location_city: str
    job_type: str
    category: str
    post_date: str
    collect_date: str
    is_new: bool
    url: str
    description: str
    requirements: str
    salary: str
    source: str
    source_url: str
    tags: list = field(default_factory=list)


class BaseScraper(ABC):
    def __init__(self, config: ScraperConfig):
        self.config = config
        self.session = None
        self.browser = None
        self._pw = None

    async def __aenter__(self):
        if self.config.use_playwright:
            from playwright.async_api import async_playwright
            self._pw = await async_playwright().start()
            self.browser = await self._pw.chromium.launch(headless=True)
        else:
            import aiohttp
            self.session = aiohttp.ClientSession(headers=self._default_headers())
        return self

    async def __aexit__(self, *args):
        if self.browser:
            await self.browser.close()
        if self._pw:
            await self._pw.stop()
        if self.session:
            await self.session.close()

    def _default_headers(self) -> dict:
        return {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 "
                "(JobAggregator/1.0; edu purpose)"
            ),
            "Accept": "application/json, text/html, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }

    async def _rate_limit(self):
        delay = random.uniform(self.config.min_delay, self.config.max_delay)
        await asyncio.sleep(delay)

    async def _retry_post(self, url: str, **kwargs) -> dict:
        last_error = None
        for attempt in range(self.config.max_retries):
            try:
                await self._rate_limit()
                async with self.session.post(url, timeout=self.config.timeout, **kwargs) as resp:
                    if resp.status == 429:
                        wait = int(resp.headers.get("Retry-After", 60))
                        logger.warning(f"[{self.config.name}] Rate limited, waiting {wait}s")
                        await asyncio.sleep(wait)
                        continue
                    resp.raise_for_status()
                    return await resp.json()
            except Exception as e:
                last_error = e
                wait = 2 ** attempt
                logger.warning(f"[{self.config.name}] POST attempt {attempt+1}/{self.config.max_retries} failed: {e}")
                await asyncio.sleep(wait)
        raise last_error

    @abstractmethod
    async def fetch_job_ids(self) -> list:
        ...

    @abstractmethod
    async def parse_job_detail(self, job_id) -> Optional[JobResult]:
        ...

    def should_include(self, job: JobResult) -> bool:
        location = job.location or ""
        return "广州" in location or "深圳" in location

    def should_include_by_keyword(self, job: JobResult, keywords: list) -> bool:
        text = (job.title + " " + job.description).lower()
        return any(kw.lower() in text for kw in keywords)

    def suitable_for_fresh_grad(self, job: JobResult) -> bool:
        """Filter out jobs requiring advanced degrees or years of experience."""
        text = f"{job.title} {job.description} {job.requirements}".lower()

        # Exclude advanced degrees
        if any(w in text for w in ["硕士", "博士", "研究生"]):
            return False

        # Exclude multi-year experience
        if any(w in text for w in ["两年以上", "三年以上", "五年以上", "八年以上",
                                     "年以上经验", "年以上工作",
                                     "3年以上", "5年以上", "2年以上"]):
            return False

        # Exclude clearly senior titles
        if any(w in job.title for w in ["高级", "资深", "专家", "架构师", "总监"]):
            return False

        return True

    async def run(self, keywords: list) -> list:
        logger.info(f"[{self.config.name}] Starting: {self.config.company_display}")
        results = []
        try:
            job_ids = await self.fetch_job_ids()
            logger.info(f"[{self.config.name}] Found {len(job_ids)} job IDs")
        except Exception as e:
            logger.error(f"[{self.config.name}] Failed to fetch job IDs: {e}")
            return results
        for jid in job_ids:
            try:
                job = await self.parse_job_detail(jid)
                if not job:
                    continue
                if not self.suitable_for_fresh_grad(job):
                    continue
                if not self.should_include(job):
                    continue
                if not self.should_include_by_keyword(job, keywords):
                    continue
                results.append(job)
            except Exception as e:
                logger.error(f"[{self.config.name}] Failed job {jid}: {e}")
        logger.info(f"[{self.config.name}] Matched {len(results)} jobs")
        return results
