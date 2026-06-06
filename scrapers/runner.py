#!/usr/bin/env python3
"""Main scraper runner."""

import asyncio
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scrapers.tencent import TencentScraper
from scrapers.gdut import GdutScraper
from scrapers.netease import NeteaseScraper
from scrapers.huawei import HuaweiScraper
from scrapers.state_owned import StateOwnedScraper
from scrapers.bytedance import ByteDanceScraper
from scrapers.alibaba import AlibabaScraper
from scrapers.utils import (
    merge_and_deduplicate, update_meta, cleanup_old_new_flags, TARGET_KEYWORDS,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger("runner")

ALL_SCRAPERS = [
    ("tencent", TencentScraper),
    ("gdut", GdutScraper),
    ("netease", NeteaseScraper),
    ("huawei", HuaweiScraper),
    ("state_owned", StateOwnedScraper),
    ("bytedance", ByteDanceScraper),
    ("alibaba", AlibabaScraper),
]


async def run_scrapers(targets=None, dry_run=False):
    status = {}
    errors = []
    all_results = []
    to_run = [(n, c) for n, c in ALL_SCRAPERS if targets is None or n in targets]

    for name, cls in to_run:
        start = time.time()
        try:
            async with cls() as scraper:
                results = await scraper.run(TARGET_KEYWORDS)
                all_results.append((name, results))
                status[name] = "success"
            logger.info(f"[{name}] Done in {time.time()-start:.1f}s, {len(results)} jobs")
        except Exception as e:
            status[name] = "failed"
            errors.append({"source": name, "error": str(e), "time": f"{time.time()-start:.1f}s"})
            logger.error(f"[{name}] FAILED: {e}")

    if dry_run:
        logger.info("DRY RUN")
        for n, r in all_results: logger.info(f"  {n}: {len(r)} jobs")
        return

    for name, results in all_results:
        merge_and_deduplicate(results, name)
    cleanup_old_new_flags(3)
    update_meta(status, errors)
    logger.info(f"DONE. Status: {status}")


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("targets", nargs="*")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    asyncio.run(run_scrapers(args.targets or None, args.dry_run))


if __name__ == "__main__":
    main()
