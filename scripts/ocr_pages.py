#!/usr/bin/env python3
"""Render HebrewBooks page PDFs and OCR with Tesseract (Hebrew).

Requires:
  - pymupdf (pip install pymupdf)
  - tesseract with heb.traineddata
    Place heb.traineddata in ~/tessdata (or pass --tessdata)

Usage:
  python3 scripts/ocr_pages.py --pages 4,7,8
  python3 scripts/ocr_pages.py --start 1 --end 20
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "data" / "raw" / "pages"
IMAGES = ROOT / "data" / "raw" / "images"
OCR = ROOT / "data" / "raw" / "ocr"


def ensure_tessdata(tessdata: Path) -> Path:
    tessdata.mkdir(parents=True, exist_ok=True)
    eng_src = Path("/usr/local/share/tessdata/eng.traineddata")
    if eng_src.exists() and not (tessdata / "eng.traineddata").exists():
        shutil.copy(eng_src, tessdata / "eng.traineddata")
    if not (tessdata / "heb.traineddata").exists():
        raise SystemExit(
            f"Missing {tessdata / 'heb.traineddata'}.\n"
            "Download from https://github.com/tesseract-ocr/tessdata_best/raw/main/heb.traineddata"
        )
    return tessdata


def ocr_page(page: int, tessdata: Path, scale: float = 2.5, psm: int = 6) -> Path:
    pdf = PAGES / f"p{page}.pdf"
    if not pdf.exists():
        raise FileNotFoundError(pdf)
    IMAGES.mkdir(parents=True, exist_ok=True)
    OCR.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf)
    pix = doc[0].get_pixmap(matrix=fitz.Matrix(scale, scale))
    img = IMAGES / f"p{page}.png"
    pix.save(str(img))
    doc.close()

    out_base = OCR / f"p{page}"
    cmd = [
        "tesseract",
        str(img),
        str(out_base),
        "-l",
        "heb+eng",
        "--tessdata-dir",
        str(tessdata),
        "--psm",
        str(psm),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr or r.stdout)
    return Path(str(out_base) + ".txt")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--end", type=int, default=20)
    ap.add_argument("--pages", type=str, default="")
    ap.add_argument("--tessdata", type=str, default=str(Path.home() / "tessdata"))
    ap.add_argument("--scale", type=float, default=2.5)
    ap.add_argument("--psm", type=int, default=6)
    args = ap.parse_args()

    tessdata = ensure_tessdata(Path(args.tessdata))
    pages = (
        [int(x.strip()) for x in args.pages.split(",") if x.strip()]
        if args.pages
        else list(range(args.start, args.end + 1))
    )

    for p in pages:
        try:
            path = ocr_page(p, tessdata, scale=args.scale, psm=args.psm)
            print(f"p{p}: {path.stat().st_size} chars → {path}")
        except Exception as e:
            print(f"p{p}: ERROR {e}")


if __name__ == "__main__":
    main()
