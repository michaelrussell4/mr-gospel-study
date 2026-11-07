import os
import json
import html
from .parser import extract_all_entries
from .styles import SITE_CSS
from .app_js import APP_JS

def build_index_html(entries, stats):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="color-scheme" content="light dark" />
  <title>Gospel Study Journal — Michael Garrett Russell</title>
  <meta name="description" content="A personal gospel study journal and scripture research library by Michael Garrett Russell featuring {stats['total_entries']} studies, {stats['total_scriptures']} scripture citations, and {stats['total_tags']} topics." />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Newsreader:ital,opsz,wght@0,6..72,500;0,6..72,600;0,6..72,700;1,6..72,400&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="assets/style.css" />
</head>
<body>
  <header class="site-header">
    <div class="header-inner">
      <a href="#view/studies" class="brand-lockup">
        <div class="brand-icon" aria-hidden="true">ΜΡ</div>
        <div class="brand-titles">
          <span class="brand-title">Gospel Study Journal</span>
          <span class="brand-subtitle">Michael Garrett Russell • 2019–2025</span>
        </div>
      </a>

      <nav class="nav-tabs" aria-label="Primary Navigation">
        <button type="button" class="nav-tab active" data-view="studies">
          📚 Studies <span class="count-badge">{stats['total_entries']}</span>
        </button>
        <button type="button" class="nav-tab" data-view="scriptures">
          📖 Scriptures <span class="count-badge">{stats['total_books']}</span>
        </button>
        <button type="button" class="nav-tab" data-view="tags">
          🏷️ Topics &amp; Tags <span class="count-badge">{stats['total_tags']}</span>
        </button>
        <button type="button" class="nav-tab" data-view="timeline">
          🗓️ Archive
        </button>
      </nav>

      <div class="header-actions">
        <button type="button" class="icon-btn" id="random-study-btn" title="Open a random gospel study entry">
          🎲 Random Study
        </button>
        <button type="button" class="icon-btn" id="theme-toggle" title="Toggle Light / Dark theme" aria-label="Toggle Light or Dark theme">
          🌗 Theme
        </button>
      </div>
    </div>
  </header>

  <section class="hero-banner" id="hero-section">
    <div class="hero-inner">
      <div class="hero-eyebrow">Scripture Exegesis • Theology • Literary Patterns</div>
      <h1 class="hero-title">Search the Scriptures &amp; Study Notes</h1>
      <p class="hero-desc">
        Explore six years of personal gospel study notes, scripture commentary, chiasmus analyses, and theological reflections across the Standard Works.
      </p>

      <div class="search-box-wrap">
        <div class="search-input-container">
          <span class="search-icon" aria-hidden="true">🔍</span>
          <input
            type="search"
            id="global-search"
            class="search-input"
            placeholder="Search by keyword, scripture (e.g. Alma 32, 2 Nephi 9), or #tag (e.g. #Atonement, #Chiasmus)…"
            autocomplete="off"
            aria-label="Search studies by keyword, scripture, or tag"
          />
          <button type="button" class="search-clear-btn" id="search-clear" title="Clear search" aria-label="Clear search">✕</button>
          <kbd class="search-kbd" aria-hidden="true">/</kbd>
        </div>
      </div>

      <div class="quick-stats-row">
        <span class="quick-stat"><strong>{stats['total_entries']}</strong> Study Articles</span>
        <span>•</span>
        <span class="quick-stat"><strong>{stats['total_words']:,}</strong> Words Written</span>
        <span>•</span>
        <span class="quick-stat"><strong>{stats['total_scriptures']:,}</strong> Scripture Citations</span>
        <span>•</span>
        <span class="quick-stat"><strong>{stats['total_tags']}</strong> #Tags</span>
      </div>
    </div>
  </section>

  <main class="main-container" id="main-content">
    <noscript>
      <p>Please enable JavaScript to use the interactive search, scripture browser, and tag filters.</p>
    </noscript>
  </main>

  <div class="lightbox-backdrop" id="lightbox" hidden>
    <img id="lightbox-img" src="" alt="" />
  </div>

  <script src="assets/entries-data.js"></script>
  <script src="assets/app.js"></script>
</body>
</html>
"""

def build_site(
    archive_path="raw/Gospel Study Journal ARCHIVE.rtf",
    current_path="raw/Gospel Study Journal_ Michael Russell.rtf",
    out_dir="dist"
):
    assets_dir = os.path.join(out_dir, "assets")
    img_dir = os.path.join(assets_dir, "images")
    os.makedirs(img_dir, exist_ok=True)

    print("Extracting entries from RTF journals...")
    entries = extract_all_entries(archive_path, current_path, img_dir)

    all_tags = {t for e in entries for t in e["tags"]}
    all_books = {b for e in entries for b in e["scripture_books"]}
    all_refs = {s["ref"] for e in entries for s in e["scriptures"]}
    total_words = sum(e["word_count"] for e in entries)

    stats = {
        "total_entries": len(entries),
        "total_tags": len(all_tags),
        "total_books": len(all_books),
        "total_scriptures": len(all_refs),
        "total_words": total_words,
    }

    payload = {
        "stats": stats,
        "entries": entries,
    }

    json_path = os.path.join(assets_dir, "entries.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    js_data_path = os.path.join(assets_dir, "entries-data.js")
    with open(js_data_path, "w", encoding="utf-8") as f:
        f.write("window.GOSPEL_STUDY_DATA = ")
        json.dump(payload, f, ensure_ascii=False)
        f.write(";\n")

    css_path = os.path.join(assets_dir, "style.css")
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(SITE_CSS.strip() + "\n")

    app_js_path = os.path.join(assets_dir, "app.js")
    with open(app_js_path, "w", encoding="utf-8") as f:
        f.write(APP_JS.strip() + "\n")

    index_path = os.path.join(out_dir, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(build_index_html(entries, stats))

    nojekyll_path = os.path.join(out_dir, ".nojekyll")
    with open(nojekyll_path, "w", encoding="utf-8") as f:
        f.write("")

    print(
        f"Built static site in '{out_dir}/': "
        f"{stats['total_entries']} entries, {stats['total_words']:,} words, "
        f"{stats['total_tags']} tags, {stats['total_scriptures']:,} scripture citations."
    )
    return stats
