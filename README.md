# Gospel Study Journal — Michael Garrett Russell

A static study site and scripture exploration library generated from the Google Docs RTF exports in `raw/` (`Gospel Study Journal ARCHIVE.rtf` and `Gospel Study Journal_ Michael Russell.rtf`).

## Features

- **294 Study Articles (2019–2025)** across 190,000+ words of scripture commentary, theological notes, and literary analyses.
- **Nuanced RTF Extraction (`src/mr_gospel_study/parser.py`)**:
  - Handles multi-entry dates, mis-styled title/subtitle headers (`s0`/`s1`/`s2`/`s16`), multi-line `s16` metadata headers, and multi-pipe source strings.
  - Preserves comparison tables, nested ordered/unordered lists, footnotes, hyperlinks, semantic text/highlight colors (`\cfN` & `\chcbpatN` mapped per-file color table for both Light and Dark themes), and multi-level step indentations for scripture quotes and **Chiasmus** structures.
  - Extracts embedded PNG charts/figures losslessly and converts inline equation bitmaps into crisp HTML math markup.
- **Interactive Search & Exploration (`src/mr_gospel_study/app_js.py`)**:
  - **Unified Instant Search (`/` or `⌘K`)** across titles, full article text, `#tags`, and scripture references with live context snippets.
  - **Scripture Index Explorer**: Browse all **1,226** scripture citations across **64** books in the 5 Standard Works (`Book of Mormon`, `Doctrine & Covenants`, `Pearl of Great Price`, `New Testament`, `Old Testament`) down to specific chapters and verses.
  - **Topic & Tag Directory**: Browse and filter across all **576** `#tags`.
  - **Chronological Archive**: Year-by-year timeline from 2019 to 2025 plus a **Random Study** button.

## Building Locally

```bash
uv run mr-gospel-study
```

This generates the complete static site in `dist/` (which can be opened directly or served with `python -m http.server -d dist`).

## Deployment

Pushes to `main` automatically build and publish `dist/` to **GitHub Pages** via [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml).
