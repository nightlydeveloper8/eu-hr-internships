"""Compact offline provincial summary, workflow checkpoint and untrusted handoff."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from collector.provincial_factory import checkpoint, compact, import_handoff, snapshot

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('summary', 'checkpoint', 'handoff'))
    parser.add_argument('province')
    parser.add_argument('--at', help='Timezone-aware evaluation timestamp (default UTC now)')
    parser.add_argument('--source', help='Bounded source detail for summary')
    parser.add_argument('--resume', action='store_true', help='Validate workflow checkpoint; never runs a crawler')
    parser.add_argument('--input', type=Path, help='Untrusted handoff JSON file')
    args = parser.parse_args()
    at = args.at or datetime.now(timezone.utc).isoformat()
    try:
        if args.command == 'summary':
            print(compact(snapshot(ROOT, args.province, at), args.source), end='')
        elif args.command == 'checkpoint':
            result, action = checkpoint(ROOT, args.province, at, args.resume)
            print(f"Workflow checkpoint {action}; created_at={result['created_at']}; evaluated_at={at}")
            print(f"File: .staging/factory/{args.province}/checkpoint.json")
            print('Next: ' + result['next_command'])
            print('Crawler mid-run resume: unsupported by this command')
        else:
            if not args.input:
                parser.error('handoff requires --input')
            count = import_handoff(ROOT, args.province, args.input, at)
            print(f'{count} unverified candidates retained in .staging/factory/{args.province}/handoff.json; catalog unchanged')
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(2, f'Factory error: {str(exc)[:200]}\n')


if __name__ == '__main__':
    main()
