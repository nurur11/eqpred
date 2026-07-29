from pathlib import Path

from scrapy import Spider
from scrapy.crawler import CrawlerProcess

from eqpred.config import RAW_BULLETIN_DIR


_SCHEMA = {
    "record_type_identifier":        "A1",
    "year":                          "I4",
    "month":                         "I2",
    "day":                           "I2",
    "hour":                          "I2",
    "minute":                        "I2",
    "second":                        "F4.2",
    "second_standard_error":         "F4.2",
    "latitude_degrees":              "I3",
    "latitude_minutes":              "F4.2",
    "latitude_standard_error":       "F4.2",
    "longitude_degrees":             "I4",
    "longitude_minutes":             "F4.2",
    "longitude_standard_error":      "F4.2",
    "depth":                         "F5.2",
    "depth_standard_error":          "F3.2",
    "magnitude_1":                   "F2.1",
    "magnitude_1_type":              "A1",
    "magnitude_2":                   "F2.1",
    "magnitude_2_type":              "A1",
    "travel_time_table":             "A1",
    "hypocenter_location_precision": "A1",
    "subsidiary_information":        "A1",
    "maximum_intensity":             "A1",
    "damage_class":                  "A1",
    "tsunami_class":                 "A1",
    "district_number":               "I1",
    "region_number":                 "I3",
    "region_name":                   "A24",
    "number_of_stations":            "I3",
    "hypocenter_determination_flag": "A1"
}


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
