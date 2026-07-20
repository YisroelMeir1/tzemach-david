#!/usr/bin/env python3
"""Interactively add (or print a template for) one almanac entry — the one-off path.

Usage:
  python3 scripts/add_entry.py --year 2884 --title-en "David in Hebron" --title-he "דוד בחברון"
  python3 scripts/add_entry.py --year 2884 --hebrew "..." --english "..." --write
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRIES = ROOT / "data" / "entries"
ERAS = json.loads((ROOT / "data" / "eras.json").read_text(encoding="utf-8"))


def era_for(year: int) -> str:
    for era in ERAS:
        if era["year_start"] <= year <= era["year_end"]:
            return era["id"]
    return "unknown"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, required=True)
    ap.add_argument("--title-en", default="")
    ap.add_argument("--title-he", default="")
    ap.add_argument("--hebrew", default="")
    ap.add_argument("--english", default="")
    ap.add_argument("--gematria", default="")
    ap.add_argument("--status", default="machine", choices=["machine", "reviewed", "draft"])
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    entry = {
        "id": f"year-{args.year:04d}",
        "type": "almanac",
        "part": "part1",
        "year": args.year,
        "hebrew_gematria": args.gematria,
        "era": era_for(args.year),
        "title_he": args.title_he,
        "title_en": args.title_en,
        "status": args.status,
        "source_pages": [],
        "hebrew": args.hebrew,
        "english": args.english,
        "notes": "Added via add_entry.py (one-off path). Machine translation · review pending unless status=reviewed.",
    }

    text = json.dumps(entry, ensure_ascii=False, indent=2) + "\n"
    path = ENTRIES / f"{entry['id']}.json"

    if args.write:
        if path.exists():
            raise SystemExit(f"Refusing to overwrite existing {path}")
        ENTRIES.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"Wrote {path}")
        print("Run: python3 scripts/build_site.py")
    else:
        print(text)
        print(f"# Dry run. Would write to {path}. Pass --write to save.")


if __name__ == "__main__":
    main()
