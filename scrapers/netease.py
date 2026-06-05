import logging
from typing import Optional
from scrapers.base import BaseScraper, ScraperConfig, JobResult
logger = logging.getLogger(__name__)

class NeteaseScraper(BaseScraper):
    def __init__(self):
        super().__init__(ScraperConfig(name="netease", company_display="网易", source_url="https://hr.163.com", min_delay=3.0, max_delay=5.0))
    async def fetch_job_ids(self) -> list:
        logger.info("[netease] Not yet implemented - skipping")
        return []
    async def parse_job_detail(self, job_id: str) -> Optional[JobResult]:
        return None
