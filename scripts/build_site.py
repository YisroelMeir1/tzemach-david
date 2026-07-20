#!/usr/bin/env python3
"""Build the static Tzemach David site from data/entries/*.json."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ENTRIES_DIR = DATA / "entries"
SITE = ROOT / "site"
ASSETS = ROOT / "src" / "assets"

# Public hosts often serve from a subpath (e.g. GitHub Pages /repo-name/).
# Local: SITE_BASE=""  →  /css/style.css
# GitHub project pages: SITE_BASE="/tzemach-david"
BASE = os.environ.get("SITE_BASE", "").rstrip("/")


def u(path: str) -> str:
    """Prefix site-absolute path with optional BASE."""
    path = path.lstrip("/")
    if BASE:
        return f"{BASE}/{path}"
    return f"/{path}"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def status_label(status: str) -> str:
    if status == "reviewed":
        return "Human reviewed"
    if status == "draft":
        return "Draft"
    return "Machine translation · Review pending"


def nl2br(s: str) -> str:
    return s.replace("\n", "<br />\n")


def year_url(year: int) -> str:
    return f"view/almanac/{year}.html"


def nav_html(active: str = "") -> str:
    links = [
        ("index.html", "Home", "home"),
        ("contents.html", "Contents", "contents"),
        ("read.html", "Read", "read"),
        ("about.html", "About", "about"),
        ("workflow.html", "Workflow", "workflow"),
    ]
    items = []
    for href, label, key in links:
        cls = ' class="active"' if key == active else ""
        items.append(f'<a href="{u(href)}"{cls}>{label}</a>')
    return "\n      ".join(items)


def page_shell(
    title: str,
    body: str,
    active: str = "",
    description: str = "Tzemach David — English edition of Rabbi David Gans's chronicle",
    extra_head: str = "",
) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title} · Tzemach David</title>
  <meta name="description" content="{description}" />
  <link rel="stylesheet" href="{u('css/style.css')}" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=Frank+Ruhl+Libre:wght@400;500;700&family=Source+Sans+3:wght@400;500;600&display=swap" rel="stylesheet" />
  {extra_head}
</head>
<body>
  <header class="site-header">
    <div class="header-inner">
      <a class="brand" href="{u('index.html')}">
        <span class="brand-he" lang="he" dir="rtl">צמח דוד</span>
        <span class="brand-en">Tzemach David</span>
      </a>
      <nav class="nav">
      {nav_html(active)}
      </nav>
    </div>
  </header>
  <main>
{body}
  </main>
  <footer class="site-footer">
    <div class="footer-inner">
      <p><strong>Tzemach David</strong> · Rabbi David Gans (1541–1613) · Prague 1592</p>
      <p class="muted">Independent English machine translation from public-domain Hebrew. Not a scholarly critical edition — check the original for any passage of consequence.</p>
    </div>
  </footer>
</body>
</html>
"""


def build_home(book: dict, entries: list[dict], eras: list[dict]) -> str:
    almanac = [e for e in entries if e.get("type") == "almanac"]
    almanac_sorted = sorted(almanac, key=lambda e: e["year"])
    first_year = almanac_sorted[0]["year"] if almanac_sorted else 1
    n = len(almanac)
    n_machine = sum(1 for e in almanac if e.get("status") == "machine")
    n_reviewed = sum(1 for e in almanac if e.get("status") == "reviewed")

    sample_cards = []
    for e in almanac_sorted[:4]:
        sample_cards.append(
            f"""
        <a class="card year-card" href="{u(year_url(e['year']))}">
          <div class="year-num">Year {e['year']}</div>
          <div class="year-title">{e.get('title_en') or e.get('title_he', '')}</div>
          <p class="card-excerpt">{e['english'][:160]}{'…' if len(e['english']) > 160 else ''}</p>
          <span class="badge">{status_label(e.get('status', 'machine'))}</span>
        </a>"""
        )

    era_preview = []
    for era in eras[:6]:
        count = sum(
            1
            for e in almanac
            if era["year_start"] <= e["year"] <= era["year_end"]
        )
        era_preview.append(
            f"""
        <a class="era-chip" href="{u('contents.html')}#{era['id']}">
          <span class="era-he" lang="he" dir="rtl">{era['title_he']}</span>
          <span class="era-en">{era['title_en']}</span>
          <span class="era-range">AM {era['year_start']}–{era['year_end']}</span>
          <span class="era-count">{count} pilot entr{'y' if count == 1 else 'ies'}</span>
        </a>"""
        )

    body = f"""
    <section class="hero">
      <div class="hero-inner">
        <p class="eyebrow">סדר הדורות · English Chronicle Edition</p>
        <h1 lang="he" dir="rtl" class="hero-he">צמח דוד</h1>
        <h2 class="hero-en">Tzemach David</h2>
        <p class="hero-sub">Order of the Generations — the first history book printed in Hebrew</p>
        <p class="hero-desc">{book['description_en']}</p>
        <div class="hero-actions">
          <a class="btn primary" href="{u(year_url(first_year))}">Begin Reading →</a>
          <a class="btn ghost" href="{u('contents.html')}">Table of Contents</a>
          <a class="btn ghost" href="{u('view/introduction.html')}">Author's Preface</a>
        </div>
        <div class="stats">
          <div class="stat"><div class="stat-num">{n}</div><div class="stat-label">Pilot entries</div></div>
          <div class="stat"><div class="stat-num">{n_machine}</div><div class="stat-label">Machine · pending review</div></div>
          <div class="stat"><div class="stat-num">{n_reviewed}</div><div class="stat-label">Human reviewed</div></div>
          <div class="stat"><div class="stat-num">2</div><div class="stat-label">Parts (Jewish · World)</div></div>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="section-inner">
        <h3>Three things this project does</h3>
        <div class="grid-3">
          <div class="card">
            <h4>1 · Pilot translations</h4>
            <p>Sample years and the preface, translated independently from public-domain Hebrew, so you can judge style and quality before scaling up.</p>
          </div>
          <div class="card">
            <h4>2 · Full-book workflow</h4>
            <p>Scripts to download HebrewBooks pages, OCR Hebrew, segment by year, store structured JSON, and rebuild the site — the factory behind the product.</p>
          </div>
          <div class="card">
            <h4>3 · Seder-HaDoros-style site</h4>
            <p>Year pages, eras, continuous reading, bilingual text, and clear “machine translation · review pending” labels — modeled on sederhadoros.com.</p>
          </div>
        </div>
      </div>
    </section>

    <section class="section muted-bg">
      <div class="section-inner">
        <div class="section-head">
          <h3>Sample years</h3>
          <a href="{u('contents.html')}">View all →</a>
        </div>
        <div class="grid-2">
          {''.join(sample_cards)}
        </div>
      </div>
    </section>

    <section class="section">
      <div class="section-inner">
        <h3>Chronological eras</h3>
        <p class="lede">Part I is a year-by-year almanac. Eras below match the natural blocks of Jewish historical chronology (more entries fill in as the workflow runs).</p>
        <div class="era-grid">
          {''.join(era_preview)}
        </div>
      </div>
    </section>

    <section class="section muted-bg">
      <div class="section-inner about-box">
        <h3>About this edition</h3>
        <p>Content is sourced from the public-domain Hebrew of <em>Tzemach David</em> (Warsaw 1878 scan via HebrewBooks #{book['source']['hebrewbooks_id']}). English is produced with AI assistance and labeled by review status. The Hebrew original is always shown alongside.</p>
        <p class="muted small">This project’s English is an <strong>independent</strong> translation. It is not derived from other modern copyrighted English editions (some of which are licensed NC-ND).</p>
        <a class="btn primary" href="{u('workflow.html')}">See the full workflow →</a>
      </div>
    </section>
"""
    return page_shell("Home", body, active="home")


def build_contents(entries: list[dict], eras: list[dict]) -> str:
    almanac = sorted(
        [e for e in entries if e.get("type") == "almanac"],
        key=lambda e: e["year"],
    )
    by_year = {e["year"]: e for e in almanac}

    blocks = []
    for era in eras:
        years_in_era = [
            e
            for e in almanac
            if era["year_start"] <= e["year"] <= era["year_end"]
        ]
        chips = []
        for e in years_in_era:
            chips.append(
                f'<a class="year-link" href="{u(year_url(e["year"]))}">{e["year"]}</a>'
            )
        if not chips:
            chips_html = '<span class="muted small">No pilot entries yet in this era</span>'
        else:
            chips_html = "\n          ".join(chips)

        blocks.append(
            f"""
      <section class="era-block" id="{era['id']}">
        <div class="era-block-head">
          <div>
            <h3>{era['title_en']}</h3>
            <p class="era-he" lang="he" dir="rtl">{era['title_he']}</p>
          </div>
          <div class="era-meta">AM {era['year_start']}–{era['year_end']} · {len(years_in_era)} entries</div>
        </div>
        <div class="year-links">
          {chips_html}
        </div>
      </section>"""
        )

    intro_link = ""
    if any(e.get("type") == "introduction" for e in entries):
        intro_link = """
      <a class="card intro-card" href="{u('view/introduction.html')}">
        <span class="eyebrow">הקדמה</span>
        <h3>Author's Preface</h3>
        <p>Why Gans wrote the book, his sources (Seder Olam, Yuchasin, Shalshelet HaKabbalah…), and his method.</p>
      </a>"""

    body = f"""
    <section class="page-head">
      <div class="section-inner">
        <p class="eyebrow">Table of Contents</p>
        <h1>Chronological Timeline</h1>
        <p class="lede">Browse by era, or jump to any year that has been translated so far.</p>
        {intro_link}
      </div>
    </section>
    <div class="section-inner contents-list">
      {''.join(blocks)}
    </div>
"""
    return page_shell("Contents", body, active="contents")


def build_entry_page(entry: dict, neighbors: dict) -> str:
    status = status_label(entry.get("status", "machine"))
    year = entry.get("year")
    title_en = entry.get("title_en") or (f"Year {year}" if year else entry.get("title_he", ""))
    title_he = entry.get("title_he") or ""
    gem = entry.get("hebrew_gematria") or ""
    en_html = nl2br(entry["english"])
    he_html = nl2br(entry["hebrew"])
    notes_html = (
        f'<p class="notes"><strong>Note:</strong> {entry["notes"]}</p>'
        if entry.get("notes")
        else ""
    )
    am_line = f" · AM {year}" if year else ""
    year_big = f'<span class="year-big">{year}</span>' if year else ""
    he_title = (
        f'<span class="he" lang="he" dir="rtl">{title_he}</span>' if title_he else ""
    )
    gem_html = f'<span class="gem" lang="he" dir="rtl">{gem}</span>' if gem else ""

    prev_html = ""
    next_html = ""
    if neighbors.get("prev"):
        p = neighbors["prev"]
        prev_html = f'<a class="pager-link prev" href="{u(year_url(p["year"]))}">← Year {p["year"]}</a>'
    if neighbors.get("next"):
        n = neighbors["next"]
        next_html = f'<a class="pager-link next" href="{u(year_url(n["year"]))}">Year {n["year"]} →</a>'

    body = f"""
    <article class="entry">
      <div class="entry-inner">
        <div class="entry-meta-bar">
          <a href="{u('contents.html')}">Table of Contents</a>
          <span class="badge">{status}</span>
        </div>
        <header class="entry-header">
          <p class="eyebrow">Part I · Almanac{am_line}</p>
          <h1>
            {year_big}
            <span class="entry-titles">
              <span class="en">{title_en}</span>
              {he_title}
              {gem_html}
            </span>
          </h1>
        </header>

        <div class="bilingual">
          <section class="col en-col">
            <h2>English</h2>
            <div class="prose">{en_html}</div>
          </section>
          <section class="col he-col" lang="he" dir="rtl">
            <h2>עברית</h2>
            <div class="prose he-prose">{he_html}</div>
          </section>
        </div>

        {notes_html}

        <nav class="pager">
          {prev_html}
          <a class="pager-link mid" href="{u('read.html')}">Continuous reading</a>
          {next_html}
        </nav>
      </div>
    </article>
"""
    page_title = f"Year {year}" if year else title_en
    return page_shell(page_title, body, active="")


def build_intro_page(entry: dict) -> str:
    status = status_label(entry.get("status", "machine"))
    en_html = nl2br(entry["english"])
    he_html = nl2br(entry["hebrew"])
    notes_html = (
        f'<p class="notes"><strong>Note:</strong> {entry["notes"]}</p>'
        if entry.get("notes")
        else ""
    )
    body = f"""
    <article class="entry">
      <div class="entry-inner">
        <div class="entry-meta-bar">
          <a href="{u('contents.html')}">Table of Contents</a>
          <span class="badge">{status}</span>
        </div>
        <header class="entry-header">
          <p class="eyebrow">הקדמה · Front Matter</p>
          <h1>
            <span class="entry-titles">
              <span class="en">{entry['title_en']}</span>
              <span class="he" lang="he" dir="rtl">{entry['title_he']}</span>
            </span>
          </h1>
        </header>
        <div class="bilingual">
          <section class="col en-col">
            <h2>English</h2>
            <div class="prose">{en_html}</div>
          </section>
          <section class="col he-col" lang="he" dir="rtl">
            <h2>עברית</h2>
            <div class="prose he-prose">{he_html}</div>
          </section>
        </div>
        {notes_html}
        <nav class="pager">
          <a class="pager-link next" href="{u('view/almanac/1.html')}">Begin Year 1 →</a>
        </nav>
      </div>
    </article>
"""
    return page_shell(entry["title_en"], body)


def build_read(entries: list[dict]) -> str:
    almanac = sorted(
        [e for e in entries if e.get("type") == "almanac"],
        key=lambda e: e["year"],
    )
    blocks = []
    for e in almanac:
        en_html = nl2br(e["english"])
        he_html = nl2br(e["hebrew"])
        blocks.append(
            f"""
      <article class="read-entry" id="y{e['year']}">
        <header>
          <a href="{u(year_url(e['year']))}"><h2>Year {e['year']} · {e.get('title_en', '')}</h2></a>
          <span class="badge">{status_label(e.get('status', 'machine'))}</span>
        </header>
        <div class="bilingual compact">
          <div class="col en-col"><div class="prose">{en_html}</div></div>
          <div class="col he-col" lang="he" dir="rtl"><div class="prose he-prose">{he_html}</div></div>
        </div>
      </article>"""
        )
    body = f"""
    <section class="page-head">
      <div class="section-inner">
        <p class="eyebrow">Continuous Reading</p>
        <h1>Scroll the almanac</h1>
        <p class="lede">All pilot entries in order. New years appear here as the workflow expands the corpus.</p>
      </div>
    </section>
    <div class="section-inner read-stream">
      {''.join(blocks)}
    </div>
"""
    return page_shell("Read", body, active="read")


def build_about(book: dict) -> str:
    body = f"""
    <section class="page-head">
      <div class="section-inner narrow">
        <p class="eyebrow">About</p>
        <h1>Tzemach David</h1>
        <p class="lede">{book['description_en']}</p>

        <h3>The author</h3>
        <p><strong>{book['author']['name_en']}</strong> ({book['author']['name_he']}, {book['author']['years']}) lived in {book['author']['place']}. He studied under the Rema and the Maharal, and wrote on history, astronomy, and mathematics. <em>Tzemach David</em> (Prague {book['first_printed']['year_ce']}) is his best-known work.</p>

        <h3>Structure</h3>
        <ul>
          <li><strong>Part I</strong> — Jewish history, year by year from Creation to Gans’s generation.</li>
          <li><strong>Part II</strong> — World history (the four kingdoms of Daniel), with a famous preface on why Jews may study secular chronicles.</li>
        </ul>

        <h3>This digital edition</h3>
        <p>{book['source']['note']}</p>
        <p>Source edition: {book['source']['edition']}.</p>

        <h3>Quality labels</h3>
        <ul>
          <li><strong>Machine translation · Review pending</strong> — AI English, not yet human-checked.</li>
          <li><strong>Human reviewed</strong> — checked against the Hebrew for accuracy.</li>
        </ul>
      </div>
    </section>
"""
    return page_shell("About", body, active="about")


def build_workflow() -> str:
    body = """
    <section class="page-head">
      <div class="section-inner narrow">
        <p class="eyebrow">Full-book workflow</p>
        <h1>How the factory works</h1>
        <p class="lede">One-off translation is a chat paste. This project is the full pipeline: source → OCR → segment → translate → site.</p>

        <ol class="workflow-steps">
          <li>
            <h3>1. Acquire source</h3>
            <p>Download page images from HebrewBooks (public-domain scans). Script: <code>scripts/download_pages.py</code>.</p>
          </li>
          <li>
            <h3>2. OCR Hebrew</h3>
            <p>Render PDFs and run Tesseract with a Hebrew model. Script: <code>scripts/ocr_pages.py</code>. Output lands in <code>data/raw/ocr/</code>.</p>
          </li>
          <li>
            <h3>3. Segment by year</h3>
            <p>Split continuous OCR into almanac entries keyed by Anno Mundi year. Script: <code>scripts/segment_years.py</code> (starter heuristics; human cleanup expected).</p>
          </li>
          <li>
            <h3>4. Translate</h3>
            <p>Fill <code>english</code> on each JSON entry (manually, via API, or in chat). Always keep <code>hebrew</code> and set <code>status</code> to <code>machine</code> until reviewed.</p>
          </li>
          <li>
            <h3>5. Build the site</h3>
            <p>Run <code>python3 scripts/build_site.py</code>. Static HTML is written to <code>site/</code>.</p>
          </li>
          <li>
            <h3>6. Review</h3>
            <p>Flip <code>status</code> from <code>machine</code> → <code>reviewed</code> entry by entry. Rebuild to update badges.</p>
          </li>
        </ol>

        <h3>One-off vs full-book (recap)</h3>
        <table class="simple-table">
          <thead><tr><th></th><th>One-off</th><th>Full-book workflow</th></tr></thead>
          <tbody>
            <tr><td>Output</td><td>A passage of English</td><td>Structured corpus + website</td></tr>
            <tr><td>Scope</td><td>One year / page</td><td>Whole sefer (or a full part)</td></tr>
            <tr><td>Reuse</td><td>Copy-paste</td><td>JSON the site reads</td></tr>
            <tr><td>This repo</td><td>Pilot entries in <code>data/entries/</code></td><td>Scripts + rebuild loop</td></tr>
          </tbody>
        </table>

        <h3>Quick start</h3>
        <pre class="code-block">cd tzemach-david
python3 scripts/build_site.py
cd site && python3 -m http.server 8080
# open http://localhost:8080</pre>
      </div>
    </section>
"""
    return page_shell("Workflow", body, active="workflow")


def main() -> None:
    book = load_json(DATA / "book.json")
    eras = load_json(DATA / "eras.json")
    entries = []
    for path in sorted(ENTRIES_DIR.glob("*.json")):
        entries.append(load_json(path))

    almanac = sorted(
        [e for e in entries if e.get("type") == "almanac"],
        key=lambda e: e["year"],
    )
    book["stats"]["pilot_entries"] = len(almanac)
    (DATA / "book.json").write_text(
        json.dumps(book, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    # index for client use
    index = {
        "book": {
            "title_en": book["title_en"],
            "title_he": book["title_he"],
            "author": book["author"]["name_en"],
        },
        "years": [e["year"] for e in almanac],
        "entries": [
            {
                "id": e["id"],
                "type": e["type"],
                "year": e.get("year"),
                "title_en": e.get("title_en"),
                "title_he": e.get("title_he"),
                "status": e.get("status"),
                "era": e.get("era"),
            }
            for e in entries
        ],
    }

    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir(parents=True)
    (SITE / "css").mkdir()
    (SITE / "js").mkdir()
    (SITE / "data").mkdir()
    (SITE / "view" / "almanac").mkdir(parents=True)
    (SITE / "view").mkdir(exist_ok=True)

    # copy assets
    css_src = ASSETS / "style.css"
    if css_src.exists():
        shutil.copy(css_src, SITE / "css" / "style.css")

    (SITE / "data" / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (SITE / "data" / "entries.json").write_text(
        json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    (SITE / "index.html").write_text(build_home(book, entries, eras), encoding="utf-8")
    (SITE / "contents.html").write_text(build_contents(entries, eras), encoding="utf-8")
    (SITE / "read.html").write_text(build_read(entries), encoding="utf-8")
    (SITE / "about.html").write_text(build_about(book), encoding="utf-8")
    (SITE / "workflow.html").write_text(build_workflow(), encoding="utf-8")

    intro = next((e for e in entries if e.get("type") == "introduction"), None)
    if intro:
        (SITE / "view" / "introduction.html").write_text(
            build_intro_page(intro), encoding="utf-8"
        )

    for i, e in enumerate(almanac):
        neighbors = {
            "prev": almanac[i - 1] if i > 0 else None,
            "next": almanac[i + 1] if i < len(almanac) - 1 else None,
        }
        path = SITE / "view" / "almanac" / f"{e['year']}.html"
        path.write_text(build_entry_page(e, neighbors), encoding="utf-8")

    print(f"Built site → {SITE}")
    print(f"  {len(almanac)} almanac years, {len(entries)} total entries")
    print("  Serve with:  cd site && python3 -m http.server 8080")


if __name__ == "__main__":
    main()
