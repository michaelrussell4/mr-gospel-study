# Gospel Study Journal — Michael Garrett Russell

A static gospel study library and interactive scripture analytics site generated from the Google Docs RTF exports in `raw/`.

## Features

- **294 Unified Study Articles (2019–2025)** across 190,000+ words of scripture commentary, theological notes, and literary analyses.
- **Clean, Readable Formatting & Nuanced RTF Extraction ([`parser.py`](src/mr_gospel_study/parser.py))**:
  - Upright, high-legibility typography (`Inter` / `Plus Jakarta Sans` default with optional `Newsreader` book serif toggle).
  - Semantic `<blockquote class="study-blockquote">` blocks with solid left accent bars for indented scripture quotes, multi-level **Chiasmus** structures, verse-numbered passages, and full-paragraph quotations.
  - Left-bordered scripture subheadings (`.scripture-subheading`) and inline scripture reference badges (`.inline-scripture-ref`).
  - Responsive comparison tables, nested ordered/unordered lists, footnotes, semantic text/highlight colors (`\cfN` & `\chcbpatN`), lossless PNG figures, and HTML math markup.
- **Interactive Data Science & Visualizations ([`app_js.py`](src/mr_gospel_study/app_js.py))**:
  - **📊 Insights Dashboard**:
    - **Study Cadence & Writing Volume Over Time**: Interactive SVG bar chart toggleable between *Articles*, *Total Words*, and *Avg Words/Study* across *Yearly*, *Quarterly*, and *Monthly* granularities.
    - **Monthly Study Activity Heatmap**: 7-year × 12-month calendar matrix (`2019–2025`) with hover previews and click-to-filter.
    - **Canonical Scripture Citation Heatmap**: Book × Chapter intensity matrix across all 87 books of the 5 Standard Works (`Book of Mormon`, `Doctrine & Covenants`, `Pearl of Great Price`, `New Testament`, `Old Testament`).
    - **Standard Works Proportion & Top 15 Books**: Citation share and chapter coverage analysis.
    - **Study Depth Histogram & Deep-Dive Leaderboard**: Word-count distribution across 7 bins plus the longest essays.
    - **Theological Topic Co-Occurrence Network**: Ranked `#tags` and strongest tag pairings by shared study count and Jaccard similarity.
- **Unified Search & Exploration**:
  - **Instant Search (`/` or `⌘K`)** across titles, full article text, `#tags`, and scripture references with highlighted context snippets.
  - **Scripture Index Explorer**, **Topic & Tag Directory**, and **Chronological Timeline**.

## Building Locally

```bash
uv run mr-gospel-study
```

This generates the complete static site in `dist/` (including `favicon.svg` and `favicon.png`).

## Deployment

Pushes to `main` automatically build and publish `dist/` to **GitHub Pages** via [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml).
