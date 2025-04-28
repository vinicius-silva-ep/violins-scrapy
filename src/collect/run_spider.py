import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from collect.spiders.violins import ViolinSpider
from logger import setup_logger

# Initialize the logger
logger = setup_logger()

def run_spider():

    try:

        logger.info(
            "Spider execution... Getting data",
            extra={"table": "violins", "step": "collect"},
        )        

        process = CrawlerProcess(get_project_settings())

        # Starts spider
        spider = ViolinSpider()
        process.crawl(ViolinSpider)

        process.start()           

        logger.info(
            "teste handler",
            extra={"table": "violins", "step": "collect"},
        )                      

        # After the collect process, it creates a dataframe
        data = spider.collected_data     

        return data
    
    except Exception as e:
        logger.error(f"Error running spider: {e}", extra={"table": "violins", "step": "collect"})
        raise