#!/usr/bin/env python3
"""Download page PDFs from HebrewBooks pagefeed for Tzemach David.

Default source: HebrewBooks #21930 (Warsaw 1878, Part I).
Usage:
  python3 scripts/download_pages.py --start 1 --end 30
  python3 scripts/download_pages.py --pages 7,8,9,10
"""

from __future__ import annotations

import argparse
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "pages"
DEFAULT_HB_ID = 21930
PAGEFEED = "https://beta.hebrewbooks.org/pagefeed/hebrewbooks_org_{hb}_{page}.pdf"


def download_page(hb_id: int, page: int, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / f"p{page}.pdf"
    url = PAGEFEED.format(hb=hb_id, page=page)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (TzemachDavidPipeline/1.0)"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
    if len(data) < 2000:
        raise RuntimeError(f"Page {page}: response too small ({len(data)} bytes) — may be blocked")
    dest.write_bytes(data)
    return dest


def main() -> None:
    ap = argparse.ArgumentParser(description="Download HebrewBooks page PDFs")
    ap.add_argument("--hb", type=int, default=DEFAULT_HB_ID, help="HebrewBooks sefer id")
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--end", type=int, default=20)
    ap.add_argument("--pages", type=str, default="", help="Comma-separated page list (overrides start/end)")
    ap.add_argument("--sleep", type=float, default=0.35, help="Delay between requests")
    args = ap.parse_args()

    if args.pages:
        pages = [int(x.strip()) for x in args.pages.split(",") if x.strip()]
    else:
        pages = list(range(args.start, args.end + 1))

    print(f"Downloading HebrewBooks #{args.hb} pages: {pages[0]}…{pages[-1]} ({len(pages)} pages)")
    for p in pages:
        try:
            path = download_page(args.hb, p, OUT)
            print(f"  p{p}: {path.stat().st_size} bytes")
        except Exception as e:
            print(f"  p{p}: ERROR {e}")
        time.sleep(args.sleep)
    print(f"Done → {OUT}")


if __name__ == "__main__":
    main()
