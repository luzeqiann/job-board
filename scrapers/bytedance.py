import logging
from typing import Optional
from scrapers.base import BaseScraper, ScraperConfig, JobResult
logger = logging.getLogger(__name__)

class ByteDanceScraper(BaseScraper):
    def __init__(self):
        super().__init__(ScraperConfig(name="bytedance", company_display="字节跳动", source_url="https://jobs.bytedance.com", min_delay=3.0, max_delay=6.0, timeout=60, use_playwright=True))
    async def fetch_job_ids(self) -> list:
        logger.info("[bytedance] Not yet implemented - hardest company, needs Playwright")
        return []
    async def parse_job_detail(self, job_id: str) -> Optional[JobResult]:
        return None
