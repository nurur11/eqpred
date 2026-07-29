from pathlib import Path

from scrapy import Spider
from scrapy.crawler import CrawlerProcess

from eqpred.config import RAW_BULLETIN_DIR


class _BulletinSpider(Spider):
    name = "bulletin"
    start_urls = ["https://www.data.jma.go.jp/eqev/data/bulletin/hypo.html"]
    
    def parse(self, response):
        for href in response.css("tr a::attr(href)").getall():
            yield response.follow(href, self.save_file)

    def save_file(self, response):
        filename = Path(response.url).name
        save_path = RAW_BULLETIN_DIR / filename
        save_path.write_bytes(response.body)


def _download_bulletin():
    process = CrawlerProcess()
    process.crawl(_BulletinSpider)
    process.start()
