import argparse
import json

try:
    from chunker_db import ChunkerDatabase
except ImportError:
    raise SystemExit("Failed to import ChunkerDatabase; ensure chunker_db.py is in the PYTHONPATH.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Enterprise Chunker analytics CLI")
    parser.add_argument("--days", type=int, default=1, help="Number of days of analytics to fetch")
    parser.add_argument("--db", default="chunker_tracking.db", help="Path to the tracking database")
    args = parser.parse_args()

    db = ChunkerDatabase(db_path=args.db, timeout=60.0)
    data = db.get_analytics(days=args.days)
    print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

