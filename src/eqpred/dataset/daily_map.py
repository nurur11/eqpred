from pathlib import Path
from shutil import rmtree

from scrapy import Spider
from scrapy.crawler import CrawlerProcess

from eqpred.config import RAW_DAILY_MAP_DIR


class _DailyMapSpider(Spider):
    name = "daily_map"
    start_urls = ["https://www.data.jma.go.jp/eqev/data/daily_map/index.html"]

    def parse(self, response):
        for href in response.css("#menu a::attr(href)").getall():
            yield response.follow(href, self.save_file)

    def save_file(self, response):
        filename = Path(response.url).name
        save_path = RAW_DAILY_MAP_DIR / filename
        save_path.write_bytes(response.body)


def _download_daily_map():
    rmtree(RAW_DAILY_MAP_DIR)
    RAW_DAILY_MAP_DIR.mkdir()

    process = CrawlerProcess()
    process.crawl(_DailyMapSpider)
    process.start()
