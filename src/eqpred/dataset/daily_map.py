from io import StringIO
from pathlib import Path
from shutil import rmtree

import pandas as pd
from lxml import html
from scrapy import Spider
from scrapy.crawler import CrawlerProcess

from eqpred.config import RAW_DAILY_MAP_DIR, INTERIM_DAILY_MAP_PATH


_SCHEMA = {
    "year":        (0, 4),
    "month":       (5, 7),
    "day":         (8, 10),
    "hour":        (11, 13),
    "minute":      (14, 16),
    "second":      (17, 21),
    "latitude":    (23, 32),
    "longitude":   (33, 43),
    "depth":       (45, 48),
    "magnitude":   (52, 56),
    "region_name": (58, 82)
}


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


def update_daily_map():
    _download_daily_map()

    colspecs = list(_SCHEMA.values())
    names = _SCHEMA.keys()

    filepaths = sorted(RAW_DAILY_MAP_DIR.glob("*.html"))
    dfs = []

    for filepath in filepaths:
        tree = html.parse(filepath)
        pre_text = tree.xpath("string(//pre)")

        df = pd.read_fwf(
            StringIO(pre_text),
            colspecs=colspecs,
            dtype="string[pyarrow]",
            skiprows=3,
            skip_blank_lines=True,
            names=names,
            delimiter="\0"
        )
        dfs.append(df)

    df = pd.concat(dfs, ignore_index=True)
    df["magnitude"] = df["magnitude"].replace(" -  ", pd.NA)
    df["region_name"] = df["region_name"].str.rstrip()

    df = df.astype({
        "year":        "int16",
        "month":       "int8",
        "day":         "int8",
        "hour":        "int8",
        "minute":      "int8",
        "second":      "float64",
        "latitude":    "category",
        "longitude":   "category",
        "depth":       "int16",
        "magnitude":   "float32",
        "region_name": "category"
    })
    df.to_pickle(INTERIM_DAILY_MAP_PATH)
