"""Read-only EU pilot for known official-page ATS observations.

Run: python3 scripts/ats_discovery_pilot.py --countries DE FR BE IE --per-country 6
No network, crawler, registration or catalog writes. Output JSON to stdout.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from collector.ats_channel_discovery import PILOT_COUNTRIES, pilot


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--countries", nargs="+", default=list(PILOT_COUNTRIES))
    parser.add_argument("--per-country", type=int, default=6)
    parser.add_argument("--output", type=Path, help="Optional report path; default stdout only")
    args = parser.parse_args(argv)
    def read(path):
        return json.loads((ROOT / path).read_text(encoding="utf-8"))
    result = pilot(read("data/companies.json"), read("data/sources.json"),
                   read("docs/career-channel-scan.json"), args.countries, args.per_country)
    payload = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(payload, end="")
    else:
        args.output.write_text(payload, encoding="utf-8")
    return result


if __name__ == "__main__":
    main()
