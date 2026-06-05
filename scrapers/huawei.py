import logging
from typing import Optional
from scrapers.base import BaseScraper, ScraperConfig, JobResult
logger = logging.getLogger(__name__)

class HuaweiScraper(BaseScraper):
    def __init__(self):
        super().__init__(ScraperConfig(name="huawei", company_display="华为", source_url="https://career.huawei.com", min_delay=3.0, max_delay=5.0, use_playwright=True))
    async def fetch_job_ids(self) -> list:
        logger.info("[huawei] Not yet implemented - skipping")
        return []
    async def parse_job_detail(self, job_id: str) -> Optional[JobResult]:
        return None
