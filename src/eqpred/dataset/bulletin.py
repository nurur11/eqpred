from pathlib import Path

import pandas as pd
from scrapy import Spider
from scrapy.crawler import CrawlerProcess

from eqpred.config import RAW_BULLETIN_DIR, INTERIM_BULLETIN_PATH


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


def _parse_column(series, descriptor):
    type_ = descriptor[0]
    w = int(descriptor[1:].split(".")[0])
    d = int(descriptor[1:].split(".")[-1])

    series.replace(" "*w, pd.NA, inplace=True)

    if type_ == "A":
        return series.str.rstrip().astype("category")

    series = series.str.lstrip()
    series = series.str.replace(" ", "0")
    series = series.str.replace({"A": "-1", "B": "-2", "C": "-3"})

    if type_ == "F":
        if d == 1:
            return series.astype("float32") / 10
        if d == 2:
            return series.astype("float64") / 100

    if type_ == "I":
        if series.isna().any():
            series = series.astype("int16[pyarrow]")
        else:
            series = series.astype("int16")
        return pd.to_numeric(series, downcast="integer")


def update_bulletin():
    _download_bulletin()

    widths = [int(float(descriptor[1:])) for descriptor in _SCHEMA.values()]
    names = _SCHEMA.keys()

    filepaths = sorted(RAW_BULLETIN_DIR.glob("*.zip"))
    dfs = []

    for filepath in filepaths:
        df = pd.read_fwf(
            filepath,
            widths=widths,
            dtype="string[pyarrow]",
            compression="zip",
            names=names,
            delimiter="\0"
        )
        dfs.append(df)

    df = pd.concat(dfs, ignore_index=True)
    for column in df.columns:
        df[column] = _parse_column(df[column], _SCHEMA[column])

    df.to_pickle(INTERIM_BULLETIN_PATH)
