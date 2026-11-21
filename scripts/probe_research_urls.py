"""Bounded research GETs: stop a host after an unavailable/disallowed robots result.

Print compact evidence only; this helper never updates the public catalog.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from collector.pipeline import now
from collector.runtime import BudgetClient


def probe(urls, client=None):
    client = client or BudgetClient(seconds=60, max_requests=20)
    blocked = {}
    output = []
    for url in dict.fromkeys(urls):
        host = urlsplit(url).hostname
        if urlsplit(url).scheme != 'https' or not host:
            raise ValueError('Research URLs must be explicit HTTPS URLs')
        if host in blocked:
            output.append(dict(url=url, checked_at=now(), status='skipped-host', reason=blocked[host]))
            continue
        try:
            body, status, final = client.request(url)
            output.append(dict(url=url, final=final, checked_at=now(), status=status,
                               sha256=hashlib.sha256(body).hexdigest(), bytes=len(body)))
        except Exception as exc:
            reason = str(exc)
            output.append(dict(url=url, checked_at=now(), status='unread', reason=reason))
            if 'robots' in reason.lower():
                blocked[host] = reason
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('urls', nargs='+')
    args = parser.parse_args()
    print(json.dumps(probe(args.urls), ensure_ascii=False, indent=2))
