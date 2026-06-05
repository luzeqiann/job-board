import logging
from typing import Optional
from scrapers.base import BaseScraper, ScraperConfig, JobResult
logger = logging.getLogger(__name__)

class StateOwnedScraper(BaseScraper):
    def __init__(self):
        super().__init__(ScraperConfig(name="state_owned", company_display="央国企", source_url="https://job.10086.cn", min_delay=3.0, max_delay=6.0))
    async def fetch_job_ids(self) -> list:
        logger.info("[state_owned] Not yet implemented - skipping")
        return []
    async def parse_job_detail(self, job_id: str) -> Optional[JobResult]:
        return None
