import os
import json
import html
import struct
import zlib
from .parser import extract_all_entries
from .styles import SITE_CSS
from .app_js import APP_JS

LOGO_SVG = """<svg class="brand-logo-svg" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <defs>
    <linearGradient id="logo-bg-grad" x1="4" y1="4" x2="44" y2="44" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#1e3a8a" />
      <stop offset="55%" stop-color="#1d4ed8" />
      <stop offset="100%" stop-color="#b45309" />
    </linearGradient>
    <linearGradient id="logo-gold-grad" x1="16" y1="8" x2="32" y2="26" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#fef08a" />
      <stop offset="100%" stop-color="#f59e0b" />
    </linearGradient>
  </defs>
  <rect x="2" y="2" width="44" height="44" rx="12" fill="url(#logo-bg-grad)" />
  <rect x="3.5" y="3.5" width="41" height="41" rx="10.5" stroke="rgba(255,255,255,0.22)" stroke-width="1" />
  <!-- Radiant 4-point star / Liahona compass above open scripture pages -->
  <path d="M24 7.5L25.9 12.6L31 14.5L25.9 16.4L24 21.5L22.1 16.4L17 14.5L22.1 12.6L24 7.5Z" fill="url(#logo-gold-grad)" />
  <!-- Open Scripture Codex / Study Journal -->
  <path d="M24 22.5C20.5 20.3 15.6 19.6 11 20.4C10.4 20.5 10 21 10 21.6V34.8C10 35.5 10.6 36.1 11.3 36C15.8 35.3 20.4 36.1 24 38.4C27.6 36.1 32.2 35.3 36.7 36C37.4 36.1 38 35.5 38 34.8V21.6C38 21 37.6 20.5 37 20.4C32.4 19.6 27.5 20.3 24 22.5Z" fill="rgba(255,255,255,0.95)" />
  <!-- Spine & Verse Lines -->
  <path d="M24 22.5V38.2" stroke="#1e3a8a" stroke-width="1.8" stroke-linecap="round" />
  <path d="M13.5 25.2C16.5 24.8 19.2 25.2 21.2 26.2" stroke="#94a3b8" stroke-width="1.4" stroke-linecap="round" />
  <path d="M13.5 28.8C16.5 28.4 19.2 28.8 21.2 29.8" stroke="#94a3b8" stroke-width="1.4" stroke-linecap="round" />
  <path d="M13.5 32.4C16.5 32.0 19.2 32.4 21.2 33.4" stroke="#94a3b8" stroke-width="1.4" stroke-linecap="round" />
  <path d="M34.5 25.2C31.5 24.8 28.8 25.2 26.8 26.2" stroke="#94a3b8" stroke-width="1.4" stroke-linecap="round" />
  <path d="M34.5 28.8C31.5 28.4 28.8 28.8 26.8 29.8" stroke="#94a3b8" stroke-width="1.4" stroke-linecap="round" />
  <path d="M34.5 32.4C31.5 32.0 28.8 32.4 26.8 33.4" stroke="#94a3b8" stroke-width="1.4" stroke-linecap="round" />
  <!-- Golden Bookmark Ribbon -->
  <path d="M24 36.5L21.8 41.5L24 39.9L26.2 41.5L24 36.5Z" fill="#fbbf24" />
</svg>"""

FAVICON_SVG = """<svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="g" x1="4" y1="4" x2="44" y2="44" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#1e3a8a" />
      <stop offset="55%" stop-color="#1d4ed8" />
      <stop offset="100%" stop-color="#b45309" />
    </linearGradient>
  </defs>
  <rect x="2" y="2" width="44" height="44" rx="11" fill="url(#g)" />
  <path d="M24 7L26.1 12.4L31.5 14.5L26.1 16.6L24 22L21.9 16.6L16.5 14.5L21.9 12.4L24 7Z" fill="#fbbf24" />
  <path d="M24 22.5C20.5 20.3 15.6 19.6 11 20.4C10.4 20.5 10 21 10 21.6V34.8C10 35.5 10.6 36.1 11.3 36C15.8 35.3 20.4 36.1 24 38.4C27.6 36.1 32.2 35.3 36.7 36C37.4 36.1 38 35.5 38 34.8V21.6C38 21 37.6 20.5 37 20.4C32.4 19.6 27.5 20.3 24 22.5Z" fill="#ffffff" />
  <path d="M24 22.5V38.2" stroke="#1e3a8a" stroke-width="2" stroke-linecap="round" />
</svg>
"""


def generate_favicon_png(size=64):
    """Generates a crisp 64x64 RGBA PNG favicon with rounded navy-gold badge, star, and open book."""
    rows = []
    cx = cy = (size - 1) / 2.0
    r_outer = size * 0.44
    r_corner = size * 0.22

    for y in range(size):
        row = bytearray([0])  # filter type 0
        ny = y / float(size - 1)
        for x in range(size):
            nx = x / float(size - 1)
            # Rounded rectangle SDF
            dx = max(abs(x - cx) - (r_outer - r_corner), 0.0)
            dy = max(abs(y - cy) - (r_outer - r_corner), 0.0)
            dist = (dx * dx + dy * dy) ** 0.5 - r_corner

            if dist > 0.7:
                row.extend((0, 0, 0, 0))
                continue

            alpha = 255 if dist < -0.7 else int(255 * (0.7 - dist) / 1.4)

            # Background gradient (#1e3a8a -> #1d4ed8 -> #b45309)
            t = (nx + ny) * 0.5
            if t < 0.6:
                lt = t / 0.6
                r = int(30 * (1 - lt) + 29 * lt)
                g = int(58 * (1 - lt) + 78 * lt)
                b = int(138 * (1 - lt) + 216 * lt)
            else:
                lt = (t - 0.6) / 0.4
                r = int(29 * (1 - lt) + 180 * lt)
                g = int(78 * (1 - lt) + 83 * lt)
                b = int(216 * (1 - lt) + 9 * lt)

            # 4-point star around (0.5, 0.29)
            sx = abs(nx - 0.5) / 0.14
            sy = abs(ny - 0.29) / 0.14
            if (sx ** 0.65 + sy ** 0.65) <= 1.0:
                r, g, b = 251, 191, 36

            # Open book pages around x in [0.21, 0.79], y in [0.44, 0.76]
            if 0.21 <= nx <= 0.79:
                arch = 0.035 * (1.0 - ((abs(nx - 0.5) - 0.14) / 0.15) ** 2)
                top_y = 0.46 - arch
                bot_y = 0.76 - arch
                if top_y <= ny <= bot_y:
                    if abs(nx - 0.5) < 0.022:
                        r, g, b = 30, 58, 138
                    else:
                        r, g, b = 255, 255, 255

            row.extend((r, g, b, alpha))
        rows.append(bytes(row))

    raw = b"".join(rows)

    def chunk(tag, data):
        return (
            struct.pack("!I", len(data))
            + tag
            + data
            + struct.pack("!I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    ihdr = struct.pack("!IIBBBBB", size, size, 8, 6, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")


def build_index_html(entries, stats):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="color-scheme" content="light dark" />
  <title>Gospel Study Journal — Michael Garrett Russell</title>
  <meta name="description" content="A personal gospel study journal and scripture research library by Michael Garrett Russell featuring {stats['total_entries']} studies, {stats['total_scriptures']:,} scripture citations, and {stats['total_tags']} topics." />
  <link rel="icon" type="image/svg+xml" href="favicon.svg" />
  <link rel="icon" type="image/png" sizes="64x64" href="favicon.png" />
  <link rel="apple-touch-icon" href="favicon.png" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;0,6..72,700;1,6..72,400&family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="assets/style.css" />
</head>
<body>
  <header class="site-header">
    <div class="header-inner">
      <a href="#view/studies" class="brand-lockup">
        {LOGO_SVG}
        <div class="brand-titles">
          <span class="brand-title">Gospel Study Journal</span>
          <span class="brand-subtitle">Michael Garrett Russell • 2019–2025</span>
        </div>
      </a>

      <nav class="nav-tabs" aria-label="Primary Navigation">
        <button type="button" class="nav-tab active" data-view="studies">
          📚 Studies <span class="count-badge">{stats['total_entries']}</span>
        </button>
        <button type="button" class="nav-tab" data-view="insights">
          📊 Insights
        </button>
        <button type="button" class="nav-tab" data-view="scriptures">
          📖 Scriptures <span class="count-badge">{stats['total_books']}</span>
        </button>
        <button type="button" class="nav-tab" data-view="tags">
          🏷️ Topics <span class="count-badge">{stats['total_tags']}</span>
        </button>
        <button type="button" class="nav-tab" data-view="timeline">
          🗓️ Timeline
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
        Explore {stats['total_entries']} personal gospel studies, scripture commentary, chiasmus analyses, and theological reflections across the Standard Works.
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
        <span class="quick-stat"><strong>{stats['total_entries']}</strong> Studies</span>
        <span>•</span>
        <span class="quick-stat"><strong>{stats['total_words']:,}</strong> Words Written</span>
        <span>•</span>
        <span class="quick-stat"><strong>{stats['total_scriptures']:,}</strong> Scripture Citations</span>
        <span>•</span>
        <span class="quick-stat"><strong>{stats['total_tags']}</strong> #Tags</span>
        <span>•</span>
        <a href="#view/insights" class="quick-stat-link">📊 Explore Data Visualizations →</a>
      </div>
    </div>
  </section>

  <main class="main-container" id="main-content">
    <noscript>
      <p>Please enable JavaScript to use the interactive search, data visualizations, scripture browser, and topic filters.</p>
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

    fav_svg_path = os.path.join(out_dir, "favicon.svg")
    with open(fav_svg_path, "w", encoding="utf-8") as f:
        f.write(FAVICON_SVG.strip() + "\n")

    fav_png_path = os.path.join(out_dir, "favicon.png")
    with open(fav_png_path, "wb") as f:
        f.write(generate_favicon_png(64))

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
