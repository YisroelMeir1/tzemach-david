#!/usr/bin/env python3
"""Starter segmenter: find year-like anchors in OCR text and draft entry stubs.

Hebrew Rashi-script OCR is noisy; this script is a *helper*, not a finished parser.
It writes draft JSON under data/entries/ only when --write is passed and the file
does not already exist (never overwrites curated pilot entries).

Usage:
  python3 scripts/segment_years.py
  python3 scripts/segment_years.py --write
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OCR_DIR = ROOT / "data" / "raw" / "ocr"
ENTRIES = ROOT / "data" / "entries"

# Hebrew gematria letters commonly used as year markers in chronicles
# This is deliberately loose: OCR garble means we only propose candidates.
YEAR_HINT = re.compile(
    r"(?P<label>(?:^|\s)(?:[אבגדהוזחטיכלמנסעפצקרשת״\"']{1,8}))\s+"
    r"(?P<body>.{10,200})",
    re.MULTILINE,
)

# Map common clean gematria forms → decimal (pilot helpers)
GEM_MAP = {
    "א": 1,
    "קל": 130,
    "ק״ל": 130,
    'ק"ל': 130,
    "רלה": 235,
    "רל״ה": 235,
    "שכה": 325,
    "שכ״ה": 325,
    "שצה": 395,
    "שצ״ה": 395,
    "תס": 460,
    "ת״ס": 460,
    "תרכב": 622,
    "תרכ״ב": 622,
    "תרפז": 687,
    "תרפ״ז": 687,
    "תתעד": 874,
    "תתע״ד": 874,
    "תתקל": 930,
    "תתק״ל": 930,
}


def normalize_gem(s: str) -> str:
    return (
        s.strip()
        .replace('"', "״")
        .replace("'", "׳")
        .replace(" ", "")
    )


def load_ocr() -> str:
    chunks = []
    for path in sorted(OCR_DIR.glob("p*.txt")):
        chunks.append(f"\n\n/* {path.name} */\n")
        chunks.append(path.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(chunks)


def propose_from_known() -> list[dict]:
    """Emit draft stubs for the standard Creation-block years if missing."""
    proposals = []
    for gem, year in sorted(set((k, v) for k, v in GEM_MAP.items()), key=lambda x: x[1]):
        # only keep one gem form per year
        if any(p["year"] == year for p in proposals):
            continue
        proposals.append(
            {
                "id": f"year-{year:04d}",
                "type": "almanac",
                "part": "part1",
                "year": year,
                "hebrew_gematria": gem if "״" in gem or "׳" in gem else gem,
                "era": "creation" if year <= 930 else "antediluvian",
                "title_he": "",
                "title_en": "",
                "status": "machine",
                "source_pages": [],
                "hebrew": "",
                "english": "",
                "notes": "Draft stub from segment_years.py — fill hebrew/english before publishing.",
            }
        )
    return proposals


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="Write missing draft stubs")
    args = ap.parse_args()

    text = load_ocr() if OCR_DIR.exists() else ""
    print(f"OCR corpus: {len(text)} characters")

    # Scan for known gematria tokens in OCR (signal that page is chronological)
    found = []
    for gem, year in GEM_MAP.items():
        if gem in text or gem.replace("״", '"') in text:
            found.append((year, gem))
    found = sorted(set(found))
    print(f"Known year anchors detected in OCR: {len(found)}")
    for year, gem in found[:30]:
        print(f"  AM {year} ({gem})")

    proposals = propose_from_known()
    existing = {p.stem for p in ENTRIES.glob("*.json")} if ENTRIES.exists() else set()
    missing = [p for p in proposals if p["id"] not in existing]

    print(f"Existing entries: {len(existing)}")
    print(f"Draft stubs that would be created: {len(missing)}")

    if args.write:
        ENTRIES.mkdir(parents=True, exist_ok=True)
        for p in missing:
            path = ENTRIES / f"{p['id']}.json"
            path.write_text(json.dumps(p, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"  wrote {path.name}")
        print("Done. Fill hebrew/english, then rebuild the site.")
    else:
        print("Dry run only. Pass --write to create missing stubs (never overwrites).")


if __name__ == "__main__":
    main()
