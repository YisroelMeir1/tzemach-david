# Tzemach David · צמח דוד — English Chronicle Site

A **sederhadoros-style** digital edition of *Tzemach David* by **Rabbi David Gans** (Prague, 1592): year-by-year Jewish history, bilingual Hebrew/English, with clear machine-translation status labels.

Project path: `~/tzemach-david`

---

## What you asked for (all three)

| Layer | What it is | Where it lives |
|-------|------------|----------------|
| **1. One-off / pilot** | Sample years + preface translated now, so you can judge quality | `data/entries/*.json` |
| **2. Full-book workflow** | Download → OCR → segment → translate → rebuild | `scripts/` |
| **3. Site like sederhadoros** | Home, TOC by era, year pages, continuous read, badges | `site/` (built) |

---

## Quick start (view the site)

```bash
cd ~/tzemach-david
python3 scripts/build_site.py
cd site && python3 -m http.server 8080
```

Open **http://localhost:8080**

Try:

- Home → sample years  
- **Contents** → eras + year chips  
- **Year 395** → same chronological node as sederhadoros.com/view/almanac/395  
- **Workflow** → how to expand to the whole sefer  

---

## The sefer

*Tzemach David* (“Shoot of David”) is a Hebrew world chronicle by **David ben Shlomo Gans** (1541–1613), student of the Rema and the Maharal of Prague.

- **Part I** — Jewish history from Creation to Gans’s day, year by year  
- **Part II** — general world history (four kingdoms of Daniel), with a famous defense of studying secular history  

First printed **Prague 1592** — often called the first history book printed in Hebrew. Later printers added continuations after the author’s death.

**Hebrew source used here:** public-domain Warsaw 1878 scan, HebrewBooks **#21930**.

**English on this site:** independent machine translation with review-pending labels. It is **not** derived from other modern copyrighted English editions (some of which are licensed NC-ND / no-derivatives).

---

## One-off vs full-book workflow

### One-off translation
You translate **one year / one page** and (optionally) drop it into the site:

```bash
python3 scripts/add_entry.py \
  --year 2884 \
  --title-en "David reigns in Hebron" \
  --title-he "דוד מלך בחברון" \
  --hebrew "..." \
  --english "..." \
  --write

python3 scripts/build_site.py
```

Fast. Good for pilots and spot-checks. No factory required.

### Full-book workflow
You run a **pipeline** so the whole sefer can become structured data + website:

```bash
# 1) Fetch more scan pages
python3 scripts/download_pages.py --start 1 --end 40

# 2) OCR (needs tesseract + ~/tessdata/heb.traineddata)
python3 scripts/ocr_pages.py --start 1 --end 40

# 3) Propose year stubs from OCR anchors (never overwrites curated entries)
python3 scripts/segment_years.py          # dry run
python3 scripts/segment_years.py --write  # create missing stubs only

# 4) Fill hebrew + english on each JSON (chat, API, or by hand)
# 5) Rebuild
python3 scripts/build_site.py
```

| | One-off | Full-book |
|--|---------|-----------|
| Output | English for a passage | Corpus + site |
| Structure | Informal | Year JSON + eras + status |
| Scale | Manual per entry | Scripts + rebuild loop |
| Quality | Ad hoc | Per-entry `machine` / `reviewed` |

This repo already includes **both**: a pilot set of entries **and** the workflow scripts.

---

## Data model

Each entry is one JSON file in `data/entries/`:

```json
{
  "id": "year-0395",
  "type": "almanac",
  "part": "part1",
  "year": 395,
  "hebrew_gematria": "שצ״ה",
  "era": "creation",
  "title_he": "מהללאל",
  "title_en": "Mahalalel",
  "status": "machine",
  "source_pages": [7],
  "hebrew": "…",
  "english": "…",
  "notes": "…"
}
```

`status` values:

- `machine` → badge: **Machine translation · Review pending**
- `reviewed` → badge: **Human reviewed**
- `draft` → stub not ready to feature

---

## Pilot entries included

Preface + early chronology (Creation block and key later nodes):

| Year (AM) | Topic |
|-----------|--------|
| — | Author’s preface (הקדמה) |
| 1 | Creation / Adam |
| 130–930 | Seth → death of Adam |
| 1056 | Noah |
| 1656 | The Flood |
| 1948 | Abram |
| 2048 | Isaac |
| 2448 | Exodus |

Compare **Year 395** here with [sederhadoros.com/view/almanac/395](https://sederhadoros.com/view/almanac/395): same chronological “address,” different sefer (Gans is usually briefer than Heilprin’s *Seder HaDoros*).

---

## Project layout

```
tzemach-david/
  data/
    book.json          # metadata
    eras.json          # chronological eras for TOC
    entries/           # one JSON per entry (source of truth)
    raw/
      pages/           # HebrewBooks page PDFs
      images/          # rendered page images
      ocr/             # tesseract output
  scripts/
    download_pages.py
    ocr_pages.py
    segment_years.py
    add_entry.py       # one-off helper
    build_site.py      # JSON → static site
  src/assets/style.css
  site/                # generated — serve this folder
  README.md
```

---

## OCR notes

Scanned Rashi / 19th-century Hebrew type is hard for OCR. Expect:

- Good hits on front matter (preface)  
- Noisier body text → **human cleanup** of `hebrew` fields  

You already have sample OCR under `data/raw/ocr/` from the pilot run.

Hebrew tessdata (if needed again):

```bash
mkdir -p ~/tessdata
curl -L -o ~/tessdata/heb.traineddata \
  https://github.com/tesseract-ocr/tessdata_best/raw/main/heb.traineddata
```

---

## Legal / quality

- **Hebrew text of Gans (1592 / public-domain reprints):** public domain  
- **This site’s English:** independent machine translations; review pending unless marked reviewed  
- **Not** a critical scholarly edition — for any consequential citation, check a printed Hebrew text (e.g. Breuer 1983 critical edition for study)  
- Do **not** paste in NC-ND third-party English translations  

---

## Next steps (when you want to expand)

1. Download & OCR more of Part I (pages 7–100+).  
2. Curate Hebrew year-by-year (clean OCR or type from the page images).  
3. Batch-translate remaining years (same style as the pilot).  
4. Add Part II world-history section.  
5. Optional: print CSS / PDF ranges (like sederhadoros print mode).  
6. Deploy `site/` to any static host (Netlify, GitHub Pages, Cloudflare Pages).  

---

Built as a local project for browsing and expanding *Tzemach David* the same way sederhadoros.com presents *Seder HaDoros*.
