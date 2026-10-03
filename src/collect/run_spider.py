import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from collect.spiders.violins import ViolinSpider
from logger import setup_logger

# Initialize the logger
logger = setup_logger()

# scrapy.cfg lives in src/, but app.py runs from the project root, so Scrapy's
# own discovery walks up from there, never finds it and silently falls back to
# its defaults (no delay, 8 concurrent requests per domain). Naming the settings
# module makes the load independent of the working directory.
os.environ.setdefault("SCRAPY_SETTINGS_MODULE", "collect.settings")


def run_spider():

    try:

        logger.info(
            "Spider execution... Getting data",
            extra={"table": "violins", "step": "collect"},
        )

        settings = get_project_settings()

        # Keeping the crawler gives access to its stats and to the spider
        # instance the process actually ran
        process = CrawlerProcess(settings)
        crawler = process.create_crawler(ViolinSpider)
        process.crawl(crawler)

        process.start()

        stats = crawler.stats.get_stats()
        data = crawler.spider.collected_data

        # An empty crawl used to reach the transform step as a bare DataFrame,
        # which failed later with an unhelpful KeyError on the first column
        if not data:
            status_counts = {
                key.rsplit("/", 1)[-1]: value
                for key, value in stats.items()
                if key.startswith("downloader/response_status_count/")
            }
            raise RuntimeError(
                "Spider finished without collecting any item. "
                f"HTTP responses: {status_counts or 'none'}. "
                "A 429 here means the site rate-limited this IP."
            )

        logger.info(
            f"Spider collected {len(data)} items",
            extra={"table": "violins", "step": "collect"},
        )

        return data

    except Exception as e:
        logger.error(
            f"Error running spider: {e!r}",
            extra={"table": "violins", "step": "collect"},
            exc_info=True,
        )
        raise