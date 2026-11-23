"""Read only Common Crawl Parquet metadata and selected SURT ranges."""
import gzip
import json
from pathlib import Path
import re
import time
from urllib.request import urlopen

DATA = "https://data.commoncrawl.org/"
META = """select min(stats_min_value), max(stats_max_value), count(*),
                 count(stats_min_value), count(stats_max_value)
          from parquet_metadata(?) where path_in_schema = 'url_surtkey'"""
SCAN = """select distinct url, url_host_name
          from read_parquet(?) where url_surtkey >= ? and url_surtkey < ?
          and fetch_status = 200"""


def overlaps(bounds, prefix):
    low, high = bounds
    return high >= prefix and low < prefix + "\uffff"


class ColumnarIndex:
    def __init__(self, staging):
        import duckdb

        self.staging = staging
        self.events = []
        self.connection = duckdb.connect(config={"threads": 1, "home_directory": str(staging)})
        self.connection.execute("INSTALL httpfs; LOAD httpfs; CALL enable_logging('HTTP')")
        self.connection.execute("SET enable_http_metadata_cache=true; SET http_retries=1; SET http_timeout=15")

    def download(self, url):
        started = time.monotonic()
        with urlopen(url, timeout=20) as response:
            body = response.read(2_000_001)
            if len(body) > 2_000_000:
                raise ValueError("Unexpected manifest size")
        self.events.append({"type": "manifest", "get": 1, "bytes": len(body),
                            "seconds": round(time.monotonic() - started, 3)})
        return body

    def recent(self):
        rows = json.loads(self.download("https://index.commoncrawl.org/collinfo.json"))
        return [row["id"] for row in rows[:3]]

    def parquet(self, sql, params, kind):
        self.connection.execute("CALL truncate_duckdb_logs()")
        started = time.monotonic()
        try:
            return self.connection.execute(sql, params).fetchall()
        finally:
            logs = self.connection.execute("select message from duckdb_logs").fetchall()
            counts = {"type": kind, "get": 0, "head": 0, "bytes": 0,
                      "seconds": round(time.monotonic() - started, 3)}
            for (log,) in logs:
                if "'type': HEAD," in log:
                    counts["head"] += 1
                if "'type': GET," in log:
                    counts["get"] += 1
                    length = re.search(r"(?i)content-length=(\d+)", log.split("'response':", 1)[-1])
                    if length:
                        counts["bytes"] += int(length[1])
                    else:
                        counts["unknown_lengths"] = counts.get("unknown_lengths", 0) + 1
            self.events.append(counts)

    def partitions(self, crawl):
        raw = self.download(f"{DATA}crawl-data/{crawl}/cc-index-table.paths.gz")
        pattern = rf"cc-index/table/cc-main/warc/crawl={crawl}/subset=warc/part-[\w.-]+\.parquet"
        paths = sorted({path for path in gzip.decompress(raw).decode().splitlines()
                        if re.fullmatch(pattern, path)})
        if not paths:
            raise ValueError("No WARC index partitions in manifest")
        return paths

    def bounds(self, path):
        low, high, total, minima, maxima = self.parquet(META, [DATA + path], "metadata")[0]
        if not low or not high or total != minima or total != maxima:
            raise ValueError("Incomplete SURT statistics")
        return low, high

    def urls(self, path, prefix, provider):
        # Only providers with path-encoded identity or scoped corporate routes need URL data.
        if provider in {"recruitee", "personio-xml", "teamtailor", "factorial", "softgarden"} or (provider == "talentclue" and prefix.endswith(",")):
            sql = SCAN.replace("url, url_host_name", "'https://' || url_host_name, url_host_name")
        else:
            sql = SCAN
        return self.parquet(sql, [DATA + path, prefix, prefix + "\uffff"], "scan")
