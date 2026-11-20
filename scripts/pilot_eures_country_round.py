"""Read-only EURES first-page experiment. Run with python -m scripts.pilot_eures_country_round."""
import json
from pathlib import Path
from urllib.parse import urlsplit

from collector.classify import classify_role
from collector.public_sources import EURES_API, eures_criteria, eures_fingerprint, eures_record, eures_records
from collector.runtime import BudgetClient

TERMS = {
    "AT": "Praktikum Personal", "BE": "stage RH", "BG": "стаж човешки ресурси",
    "CH": "stage RH", "CY": "HR internship", "CZ": "stáž personalistika",
    "DE": "Praktikum Personal", "DK": "praktik rekruttering", "EE": "personalipraktika",
    "ES": "prácticas recursos humanos", "FI": "HR harjoittelu", "FR": "stage recrutement",
    "GR": "πρακτική ανθρώπινου δυναμικού", "HR": "praksa ljudski resursi",
    "HU": "HR gyakornok", "IE": "human resources intern", "IT": "stage risorse umane",
    "LT": "personalo praktika", "LU": "stage RH", "LV": "personāla prakse",
    "MT": "HR internship", "NL": "stage hr", "PL": "staż rekrutacja",
    "PT": "estágio recursos humanos", "RO": "internship resurse umane",
    "SE": "praktik rekrytering", "SI": "kadrovska praksa", "SK": "stáž personalistika",
}


def first_round(source):
    """One page per configured market, each consuming the ordinary shared budget."""
    for country in sorted(source["target_countries"]):
        payload = eures_criteria(keywords=[TERMS[country]])
        payload["locationCodes"] = ["el" if country == "GR" else country.lower()]
        yield country, payload


def preview_inventory(source, client):
    """Exercise the ordinary sequence in staging, sharing its original 330-request cap."""
    if source["id"] != "public-eu-eures" or client.max_requests > source["max_requests"]:
        raise ValueError("Expected the reviewed EURES source and its ordinary request limit")
    return eures_records(source, client, first_pages=first_round(source))


def compare():
    registry = json.loads(Path("data/sources.json").read_text())
    source = next(s for s in registry if s["id"] == "public-eu-eures")
    endpoint = EURES_API + "/jv-search/search"
    assert source["enabled"] and source["allowed_hosts"] == [urlsplit(endpoint).hostname]
    catalog = json.loads(Path("data/catalog.json").read_text())
    prior = {j["source_posting_id"] for j in catalog["jobs"] if j["source_id"] == source["id"]}
    client = BudgetClient(seconds=200, max_requests=12, delay=10)
    client.redirect_scope_allowed = lambda url: url in {endpoint, "https://europa.eu/robots.txt"}
    for country, geographic in first_round(source):
        if country not in {"PL", "IE", "CZ", "DK", "NL"}:
            continue
        for arm, payload in [("country", geographic), ("global", dict(geographic, locationCodes=[]))]:
            data = client.post_json(endpoint, payload)["jvs"]
            hits = {}
            local_rows = 0
            for jv in data:
                row = eures_record(source, jv)
                if not row or row["countries"] != [country]:
                    continue
                local_rows += 1
                role = classify_role(row["title"], row["text"], row["employment"])
                if role and role["internship_type"] == "internship":
                    hits.setdefault(eures_fingerprint(row), set()).add(row["external_id"])
            known = sorted({identifier for ids in hits.values() for identifier in ids if identifier in prior})
            print(json.dumps(dict(country=country, arm=arm, rows=len(data), local=local_rows,
                                  distinct=len(hits), new=sum(ids.isdisjoint(prior) for ids in hits.values()),
                                  known_ids=known)), flush=True)
    print(json.dumps(dict(requests=client.requests, bytes=client.bytes)))


if __name__ == "__main__":
    compare()
