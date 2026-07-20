# Tzemach David · צמח דוד — English Chronicle Site

A **sederhadoros-style** digital edition of *Tzemach David* by **Rabbi David Gans** (Prague, 1592): year-by-year Jewish history, bilingual Hebrew/English, with clear machine-translation status labels.

**Live site (GitHub Pages):** https://yisroelmeir1.github.io/tzemach-david/

**Repo:** https://github.com/YisroelMeir1/tzemach-david

---

## What's included

| Layer | What it is |
|-------|------------|
| **Pilot translations** | Sample years + preface |
| **Full-book workflow** | Download → OCR → segment → translate → rebuild |
| **Site** | Home, TOC by era, year pages, continuous read |

## Local development

```bash
cd tzemach-david
python3 scripts/build_site.py
# For GitHub Pages path:
SITE_BASE=/tzemach-david python3 scripts/build_site.py
# Copy site to docs/ for Pages:
rm -rf docs && cp -R site docs && touch docs/.nojekyll
```

## Structure

- `data/entries/` — bilingual year entries (source of truth)
- `scripts/build_site.py` — static site generator
- `docs/` — published GitHub Pages site
- `src/assets/style.css` — styles

Hebrew is public domain (Warsaw 1878 / HebrewBooks #21930). English is independent machine translation with review-pending labels.
