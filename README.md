# Tzemach David · צמח דוד — English Chronicle Site

A **sederhadoros-style** digital edition of *Tzemach David* by **Rabbi David Gans** (Prague, 1592): year-by-year Jewish history, bilingual Hebrew/English, with clear machine-translation status labels.

**Live site:** https://yisroelmeir1.github.io/tzemach-david/

**Repo:** https://github.com/YisroelMeir1/tzemach-david

## Local development

```bash
cd tzemach-david
python3 scripts/build_site.py
cd site && python3 -m http.server 8080
```

For GitHub Pages path prefixes:

```bash
SITE_BASE=/tzemach-david python3 scripts/build_site.py
rm -rf docs && cp -R site docs && touch docs/.nojekyll
```

## Structure

| Path | Purpose |
|------|---------|
| `data/entries/` | Bilingual year entries (source of truth) |
| `scripts/build_site.py` | Static site generator |
| `docs/` | Published GitHub Pages site |
| `src/assets/style.css` | Styles |

Hebrew is public domain (Warsaw 1878 / HebrewBooks #21930). English is independent machine translation with review-pending labels.
