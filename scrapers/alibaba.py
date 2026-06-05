import logging
from typing import Optional
from scrapers.base import BaseScraper, ScraperConfig, JobResult
logger = logging.getLogger(__name__)

class AlibabaScraper(BaseScraper):
    def __init__(self):
        super().__init__(ScraperConfig(name="alibaba", company_display="阿里巴巴", source_url="https://talent.alibaba.com", min_delay=3.0, max_delay=6.0, timeout=60, use_playwright=True))
    async def fetch_job_ids(self) -> list:
        logger.info("[alibaba] Not yet implemented - needs Playwright + API interception")
        return []
    async def parse_job_detail(self, job_id: str) -> Optional[JobResult]:
        return None
