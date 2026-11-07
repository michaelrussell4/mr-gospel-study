"""
Modern CSS stylesheet following modern-web-guidance best practices:
- :root { color-scheme: light dark; } + <meta name="color-scheme" content="light dark">
- light-dark() with @media (prefers-color-scheme: dark) fallbacks
- Unitless line-height, rem/clamp() typography, max-width: 75ch on reading blocks
- text-wrap: balance on headings, text-wrap: pretty on body paragraphs/lists/quotes
"""

SITE_CSS = r"""
:root {
  /* Light mode tokens */
  --bg-canvas-light: #faf8f5;
  --bg-surface-light: #ffffff;
  --bg-elevated-light: #f3efe9;
  --bg-subtle-light: #ebe5dc;
  --text-primary-light: #1c1917;
  --text-secondary-light: #57534e;
  --text-muted-light: #78716c;
  --border-subtle-light: #e5dec9;
  --border-strong-light: #d4cbb8;
  --brand-primary-light: #1e40af;
  --brand-accent-light: #b45309;
  --brand-soft-light: #dbeafe;
  --accent-soft-light: #fef3c7;
  --scripture-pill-bg-light: #f0fdf4;
  --scripture-pill-text-light: #166534;
  --scripture-pill-border-light: #bbf7d0;
  --tag-pill-bg-light: #f1f5f9;
  --tag-pill-text-light: #334155;
  --tag-pill-border-light: #e2e8f0;

  /* Dark mode tokens */
  --bg-canvas-dark: #0f1115;
  --bg-surface-dark: #171a21;
  --bg-elevated-dark: #1f242d;
  --bg-subtle-dark: #262c36;
  --text-primary-dark: #f3f4f6;
  --text-secondary-dark: #9ca3af;
  --text-muted-dark: #6b7280;
  --border-subtle-dark: #2a303c;
  --border-strong-dark: #3b4252;
  --brand-primary-dark: #60a5fa;
  --brand-accent-dark: #fbbf24;
  --brand-soft-dark: #1e293b;
  --accent-soft-dark: #2d2310;
  --scripture-pill-bg-dark: #0f291e;
  --scripture-pill-text-dark: #86efac;
  --scripture-pill-border-dark: #14532d;
  --tag-pill-bg-dark: #1e2430;
  --tag-pill-text-dark: #cbd5e1;
  --tag-pill-border-dark: #334155;

  /* Default (light) assignments for fallback */
  --bg-canvas: var(--bg-canvas-light);
  --bg-surface: var(--bg-surface-light);
  --bg-elevated: var(--bg-elevated-light);
  --bg-subtle: var(--bg-subtle-light);
  --text-primary: var(--text-primary-light);
  --text-secondary: var(--text-secondary-light);
  --text-muted: var(--text-muted-light);
  --border-subtle: var(--border-subtle-light);
  --border-strong: var(--border-strong-light);
  --brand-primary: var(--brand-primary-light);
  --brand-accent: var(--brand-accent-light);
  --brand-soft: var(--brand-soft-light);
  --accent-soft: var(--accent-soft-light);
  --scripture-pill-bg: var(--scripture-pill-bg-light);
  --scripture-pill-text: var(--scripture-pill-text-light);
  --scripture-pill-border: var(--scripture-pill-border-light);
  --tag-pill-bg: var(--tag-pill-bg-light);
  --tag-pill-text: var(--tag-pill-text-light);
  --tag-pill-border: var(--tag-pill-border-light);
  --shadow-sm: 0 1px 2px rgba(28, 25, 23, 0.05);
  --shadow-md: 0 4px 14px rgba(28, 25, 23, 0.07);
  --shadow-lg: 0 12px 32px rgba(28, 25, 23, 0.12);

  /* Fonts */
  --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-serif: 'Newsreader', Georgia, 'Times New Roman', serif;
  --font-mono: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
  --article-font: var(--font-serif);
  --article-size: 1.125rem;

  @media (prefers-color-scheme: dark) {
    --bg-canvas: var(--bg-canvas-dark);
    --bg-surface: var(--bg-surface-dark);
    --bg-elevated: var(--bg-elevated-dark);
    --bg-subtle: var(--bg-subtle-dark);
    --text-primary: var(--text-primary-dark);
    --text-secondary: var(--text-secondary-dark);
    --text-muted: var(--text-muted-dark);
    --border-subtle: var(--border-subtle-dark);
    --border-strong: var(--border-strong-dark);
    --brand-primary: var(--brand-primary-dark);
    --brand-accent: var(--brand-accent-dark);
    --brand-soft: var(--brand-soft-dark);
    --accent-soft: var(--accent-soft-dark);
    --scripture-pill-bg: var(--scripture-pill-bg-dark);
    --scripture-pill-text: var(--scripture-pill-text-dark);
    --scripture-pill-border: var(--scripture-pill-border-dark);
    --tag-pill-bg: var(--tag-pill-bg-dark);
    --tag-pill-text: var(--tag-pill-text-dark);
    --tag-pill-border: var(--tag-pill-border-dark);
    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
    --shadow-md: 0 4px 14px rgba(0, 0, 0, 0.4);
    --shadow-lg: 0 12px 32px rgba(0, 0, 0, 0.55);
  }

  @supports (color: light-dark(white, black)) {
    --bg-canvas: light-dark(var(--bg-canvas-light), var(--bg-canvas-dark));
    --bg-surface: light-dark(var(--bg-surface-light), var(--bg-surface-dark));
    --bg-elevated: light-dark(var(--bg-elevated-light), var(--bg-elevated-dark));
    --bg-subtle: light-dark(var(--bg-subtle-light), var(--bg-subtle-dark));
    --text-primary: light-dark(var(--text-primary-light), var(--text-primary-dark));
    --text-secondary: light-dark(var(--text-secondary-light), var(--text-secondary-dark));
    --text-muted: light-dark(var(--text-muted-light), var(--text-muted-dark));
    --border-subtle: light-dark(var(--border-subtle-light), var(--border-subtle-dark));
    --border-strong: light-dark(var(--border-strong-light), var(--border-strong-dark));
    --brand-primary: light-dark(var(--brand-primary-light), var(--brand-primary-dark));
    --brand-accent: light-dark(var(--brand-accent-light), var(--brand-accent-dark));
    --brand-soft: light-dark(var(--brand-soft-light), var(--brand-soft-dark));
    --accent-soft: light-dark(var(--accent-soft-light), var(--accent-soft-dark));
    --scripture-pill-bg: light-dark(var(--scripture-pill-bg-light), var(--scripture-pill-bg-dark));
    --scripture-pill-text: light-dark(var(--scripture-pill-text-light), var(--scripture-pill-text-dark));
    --scripture-pill-border: light-dark(var(--scripture-pill-border-light), var(--scripture-pill-border-dark));
    --tag-pill-bg: light-dark(var(--tag-pill-bg-light), var(--tag-pill-bg-dark));
    --tag-pill-text: light-dark(var(--tag-pill-text-light), var(--tag-pill-text-dark));
    --tag-pill-border: light-dark(var(--tag-pill-border-light), var(--tag-pill-border-dark));
  }

  color-scheme: light dark;
  accent-color: var(--brand-primary);
}

html[data-theme="light"] {
  color-scheme: light;
  --bg-canvas: var(--bg-canvas-light);
  --bg-surface: var(--bg-surface-light);
  --bg-elevated: var(--bg-elevated-light);
  --bg-subtle: var(--bg-subtle-light);
  --text-primary: var(--text-primary-light);
  --text-secondary: var(--text-secondary-light);
  --text-muted: var(--text-muted-light);
  --border-subtle: var(--border-subtle-light);
  --border-strong: var(--border-strong-light);
  --brand-primary: var(--brand-primary-light);
  --brand-accent: var(--brand-accent-light);
  --brand-soft: var(--brand-soft-light);
  --accent-soft: var(--accent-soft-light);
  --scripture-pill-bg: var(--scripture-pill-bg-light);
  --scripture-pill-text: var(--scripture-pill-text-light);
  --scripture-pill-border: var(--scripture-pill-border-light);
  --tag-pill-bg: var(--tag-pill-bg-light);
  --tag-pill-text: var(--tag-pill-text-light);
  --tag-pill-border: var(--tag-pill-border-light);
}

html[data-theme="dark"] {
  color-scheme: dark;
  --bg-canvas: var(--bg-canvas-dark);
  --bg-surface: var(--bg-surface-dark);
  --bg-elevated: var(--bg-elevated-dark);
  --bg-subtle: var(--bg-subtle-dark);
  --text-primary: var(--text-primary-dark);
  --text-secondary: var(--text-secondary-dark);
  --text-muted: var(--text-muted-dark);
  --border-subtle: var(--border-subtle-dark);
  --border-strong: var(--border-strong-dark);
  --brand-primary: var(--brand-primary-dark);
  --brand-accent: var(--brand-accent-dark);
  --brand-soft: var(--brand-soft-dark);
  --accent-soft: var(--accent-soft-dark);
  --scripture-pill-bg: var(--scripture-pill-bg-dark);
  --scripture-pill-text: var(--scripture-pill-text-dark);
  --scripture-pill-border: var(--scripture-pill-border-dark);
  --tag-pill-bg: var(--tag-pill-bg-dark);
  --tag-pill-text: var(--tag-pill-text-dark);
  --tag-pill-border: var(--tag-pill-border-dark);
}

*, *::before, *::after {
  box-sizing: border-box;
}

body {
  margin: 0;
  background-color: var(--bg-canvas);
  color: var(--text-primary);
  font-family: var(--font-sans);
  line-height: 1.55;
  text-align: start;
  overflow-wrap: break-word;
  -webkit-font-smoothing: antialiased;
}

h1, h2, h3, h4, h5, h6 {
  text-wrap: balance;
  margin-top: 0;
  line-height: 1.25;
  color: var(--text-primary);
}

p, blockquote, li {
  text-wrap: pretty;
}

a {
  color: var(--brand-primary);
  text-decoration-thickness: 1px;
  text-underline-offset: 0.18em;
  transition: color 0.15s ease;
}

a:hover {
  color: var(--brand-accent);
}

/* Header & Navigation */
.site-header {
  position: sticky;
  top: 0;
  z-index: 40;
  background: color-mix(in srgb, var(--bg-surface) 88%, transparent);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-subtle);
}

.header-inner {
  max-width: 1360px;
  margin: 0 auto;
  padding: 0.75rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.brand-lockup {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
  color: var(--text-primary);
}

.brand-icon {
  width: 2.35rem;
  height: 2.35rem;
  border-radius: 0.65rem;
  background: linear-gradient(135deg, var(--brand-primary), var(--brand-accent));
  color: #fff;
  display: grid;
  place-items: center;
  font-family: var(--font-serif);
  font-weight: 700;
  font-size: 1.2rem;
  box-shadow: var(--shadow-sm);
}

.brand-titles {
  display: flex;
  flex-direction: column;
}

.brand-title {
  font-family: var(--font-serif);
  font-weight: 700;
  font-size: 1.2rem;
  letter-spacing: -0.01em;
}

.brand-subtitle {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-weight: 500;
}

.nav-tabs {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  background: var(--bg-elevated);
  padding: 0.25rem;
  border-radius: 0.65rem;
  border: 1px solid var(--border-subtle);
}

.nav-tab {
  appearance: none;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-family: var(--font-sans);
  font-size: 0.875rem;
  font-weight: 600;
  padding: 0.45rem 0.85rem;
  border-radius: 0.45rem;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  transition: all 0.15s ease;
}

.nav-tab:hover {
  color: var(--text-primary);
}

.nav-tab.active {
  background: var(--bg-surface);
  color: var(--brand-primary);
  box-shadow: var(--shadow-sm);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.icon-btn {
  appearance: none;
  border: 1px solid var(--border-subtle);
  background: var(--bg-surface);
  color: var(--text-secondary);
  padding: 0.45rem 0.75rem;
  border-radius: 0.5rem;
  font-family: var(--font-sans);
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  transition: all 0.15s ease;
}

.icon-btn:hover {
  border-color: var(--border-strong);
  color: var(--text-primary);
  background: var(--bg-elevated);
}

/* Hero & Search Bar */
.hero-banner {
  background: radial-gradient(circle at 85% 15%, var(--brand-soft), transparent 48%),
              radial-gradient(circle at 15% 85%, var(--accent-soft), transparent 48%),
              var(--bg-surface);
  border-bottom: 1px solid var(--border-subtle);
  padding: 2.25rem 1.5rem 2rem;
}

.hero-inner {
  max-width: 1000px;
  margin: 0 auto;
  text-align: center;
}

.hero-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--brand-accent);
  background: var(--accent-soft);
  padding: 0.3rem 0.75rem;
  border-radius: 999px;
  margin-bottom: 0.85rem;
}

.hero-title {
  font-family: var(--font-serif);
  font-size: clamp(1.85rem, 1.3rem + 2.2vw, 3rem);
  font-weight: 700;
  margin-bottom: 0.5rem;
  letter-spacing: -0.02em;
}

.hero-desc {
  color: var(--text-secondary);
  font-size: 1.025rem;
  max-width: 62ch;
  margin: 0 auto 1.5rem;
}

.search-box-wrap {
  position: relative;
  max-width: 740px;
  margin: 0 auto;
}

.search-input-container {
  display: flex;
  align-items: center;
  background: var(--bg-canvas);
  border: 2px solid var(--border-strong);
  border-radius: 0.85rem;
  padding: 0.35rem 0.65rem 0.35rem 1rem;
  box-shadow: var(--shadow-md);
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.search-input-container:focus-within {
  border-color: var(--brand-primary);
  box-shadow: 0 0 0 4px var(--brand-soft);
}

.search-icon {
  color: var(--text-muted);
  flex-shrink: 0;
  margin-right: 0.65rem;
}

.search-input {
  width: 100%;
  border: none;
  background: transparent;
  color: var(--text-primary);
  font-family: var(--font-sans);
  font-size: 1rem;
  padding: 0.45rem 0;
  outline: none;
}

.search-input::placeholder {
  color: var(--text-muted);
}

.search-kbd {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--text-muted);
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  padding: 0.2rem 0.45rem;
  border-radius: 0.35rem;
  margin-left: 0.5rem;
  flex-shrink: 0;
}

.search-clear-btn {
  appearance: none;
  border: none;
  background: var(--bg-subtle);
  color: var(--text-secondary);
  border-radius: 999px;
  width: 1.65rem;
  height: 1.65rem;
  cursor: pointer;
  font-size: 0.85rem;
  display: inline-grid;
  place-items: center;
  margin-left: 0.35rem;
}

.quick-stats-row {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  flex-wrap: wrap;
  margin-top: 1.15rem;
  font-size: 0.8125rem;
  color: var(--text-muted);
}

.quick-stat strong {
  color: var(--text-primary);
  font-weight: 700;
}

/* Main Workspace Container */
.main-container {
  max-width: 1360px;
  margin: 0 auto;
  padding: 1.75rem 1.5rem 4rem;
}

/* Active Filter Bar */
.filter-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1.25rem;
  padding: 0.85rem 1.1rem;
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: 0.75rem;
  box-shadow: var(--shadow-sm);
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.filter-select {
  appearance: none;
  background-color: var(--bg-elevated);
  color: var(--text-primary);
  border: 1px solid var(--border-subtle);
  border-radius: 0.5rem;
  padding: 0.45rem 2rem 0.45rem 0.75rem;
  font-family: var(--font-sans);
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  background-image: linear-gradient(45deg, transparent 50%, var(--text-muted) 50%),
                    linear-gradient(135deg, var(--text-muted) 50%, transparent 50%);
  background-position: calc(100% - 14px) 50%, calc(100% - 9px) 50%;
  background-size: 5px 5px, 5px 5px;
  background-repeat: no-repeat;
}

.active-chips {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  flex-wrap: wrap;
}

.active-filter-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: var(--brand-soft);
  color: var(--brand-primary);
  border: 1px solid var(--brand-primary);
  padding: 0.25rem 0.65rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
}

.results-summary {
  font-size: 0.85rem;
  color: var(--text-secondary);
  font-weight: 500;
}

/* Layout Grid: Sidebar + Feed */
.explore-grid {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 1.75rem;
  align-items: start;
}

@media (max-width: 980px) {
  .explore-grid {
    grid-template-columns: 1fr;
  }
  .explore-sidebar {
    order: 2;
  }
}

.sidebar-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: 0.85rem;
  padding: 1.15rem;
  margin-bottom: 1.25rem;
  box-shadow: var(--shadow-sm);
}

.sidebar-heading {
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted);
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sidebar-list {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  max-height: 340px;
  overflow-y: auto;
  padding-right: 0.25rem;
}

.sidebar-item-btn {
  appearance: none;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-family: var(--font-sans);
  font-size: 0.83rem;
  padding: 0.4rem 0.55rem;
  border-radius: 0.45rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  text-align: start;
  transition: background 0.12s ease, color 0.12s ease;
}

.sidebar-item-btn:hover {
  background: var(--bg-elevated);
  color: var(--text-primary);
}

.sidebar-item-btn.active {
  background: var(--brand-soft);
  color: var(--brand-primary);
  font-weight: 600;
}

.count-badge {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  background: var(--bg-elevated);
  color: var(--text-muted);
  padding: 0.1rem 0.45rem;
  border-radius: 999px;
}

/* Entry Cards Grid & List */
.entries-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 1.15rem;
}

.entries-grid.list-mode {
  grid-template-columns: 1fr;
  gap: 0.75rem;
}

.entry-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: 0.85rem;
  padding: 1.35rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 0.9rem;
  box-shadow: var(--shadow-sm);
  transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
  cursor: pointer;
  position: relative;
}

.entry-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--border-strong);
}

.card-meta-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  font-size: 0.775rem;
  color: var(--text-muted);
}

.card-date {
  font-family: var(--font-mono);
  font-weight: 500;
}

.card-badges {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.feature-badge {
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 0.12rem 0.45rem;
  border-radius: 0.3rem;
  background: var(--accent-soft);
  color: var(--brand-accent);
}

.card-title {
  font-family: var(--font-serif);
  font-size: 1.25rem;
  font-weight: 700;
  line-height: 1.3;
  margin: 0.25rem 0 0.4rem;
  color: var(--text-primary);
}

.entry-card:hover .card-title {
  color: var(--brand-primary);
}

.card-excerpt {
  font-size: 0.9rem;
  color: var(--text-secondary);
  line-height: 1.55;
  margin: 0;
}

.search-match-snippet {
  margin-top: 0.5rem;
  padding: 0.55rem 0.75rem;
  background: var(--bg-elevated);
  border-left: 3px solid var(--brand-accent);
  border-radius: 0.35rem;
  font-size: 0.82rem;
  color: var(--text-secondary);
}

.card-footer {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding-top: 0.65rem;
  border-top: 1px solid var(--border-subtle);
}

.pill-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.scripture-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-family: var(--font-mono);
  font-size: 0.72rem;
  font-weight: 600;
  background: var(--scripture-pill-bg);
  color: var(--scripture-pill-text);
  border: 1px solid var(--scripture-pill-border);
  padding: 0.15rem 0.5rem;
  border-radius: 0.35rem;
  text-decoration: none;
  cursor: pointer;
  transition: filter 0.12s ease;
}

.scripture-pill:hover {
  filter: brightness(0.95);
  color: var(--scripture-pill-text);
}

.tag-pill {
  display: inline-flex;
  align-items: center;
  font-size: 0.73rem;
  font-weight: 600;
  background: var(--tag-pill-bg);
  color: var(--tag-pill-text);
  border: 1px solid var(--tag-pill-border);
  padding: 0.15rem 0.52rem;
  border-radius: 999px;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.12s ease;
}

.tag-pill:hover {
  border-color: var(--brand-primary);
  color: var(--brand-primary);
}

/* Article Reader View */
.reader-container {
  max-width: 1120px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 260px;
  gap: 2.25rem;
  align-items: start;
}

.reader-container.no-toc {
  grid-template-columns: 1fr;
  max-width: 840px;
}

@media (max-width: 960px) {
  .reader-container {
    grid-template-columns: 1fr;
  }
  .reader-sidebar {
    display: none;
  }
}

.article-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: 1rem;
  padding: clamp(1.5rem, 3vw, 3rem);
  box-shadow: var(--shadow-md);
}

.reader-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-subtle);
}

.back-btn {
  appearance: none;
  border: 1px solid var(--border-subtle);
  background: var(--bg-elevated);
  color: var(--text-primary);
  padding: 0.45rem 0.9rem;
  border-radius: 0.5rem;
  font-family: var(--font-sans);
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

.back-btn:hover {
  border-color: var(--brand-primary);
  color: var(--brand-primary);
}

.reader-controls {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.article-header {
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 2px solid var(--border-subtle);
}

.article-meta-line {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-bottom: 0.75rem;
}

.article-date {
  font-family: var(--font-mono);
  font-weight: 600;
  color: var(--brand-accent);
}

.article-title {
  font-family: var(--font-serif);
  font-size: clamp(1.75rem, 1.3rem + 1.8vw, 2.55rem);
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 1rem;
}

.article-sources-box {
  background: var(--bg-elevated);
  border-left: 3px solid var(--brand-primary);
  padding: 0.75rem 1rem;
  border-radius: 0.45rem;
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-bottom: 1rem;
}

.article-sources-box strong {
  color: var(--text-primary);
}

/* Rich Article Content Body */
.article-body {
  font-family: var(--article-font);
  font-size: var(--article-size);
  line-height: 1.72;
  color: var(--text-primary);
  max-width: 75ch;
}

.article-body p {
  margin: 0 0 1.2em;
}

.article-body .entry-subheading {
  font-family: var(--font-sans);
  margin: 1.85em 0 0.65em;
  padding-bottom: 0.3em;
  border-bottom: 1px solid var(--border-subtle);
}

.article-body h3.entry-subheading {
  font-size: 1.3rem;
  font-weight: 700;
}

.article-body h4.entry-subheading {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-secondary);
  border-bottom: none;
  margin-bottom: 0.4em;
}

.scripture-heading-link {
  color: inherit;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.scripture-heading-link::after {
  content: "↗";
  font-size: 0.75em;
  color: var(--brand-primary);
  opacity: 0.75;
}

.scripture-heading-link:hover {
  color: var(--brand-primary);
}

/* Indented Scripture Quotes & Chiasmus Structures */
.study-quote-group,
.study-chiasm-group {
  margin: 1.35em 0;
  padding: 0.9rem 1.15rem;
  background: var(--bg-elevated);
  border-left: 3px solid var(--brand-accent);
  border-radius: 0 0.6rem 0.6rem 0;
}

.study-chiasm-group {
  border-left-color: var(--brand-primary);
  overflow-x: auto;
}

.study-indent {
  padding-left: calc((var(--indent-steps, 2) - 2) * 0.85rem);
  margin: 0.35em 0;
}

/* Tables inside entries */
.table-wrap {
  margin: 1.5em 0;
  overflow-x: auto;
  border: 1px solid var(--border-strong);
  border-radius: 0.65rem;
  background: var(--bg-surface);
}

.study-table {
  width: 100%;
  border-collapse: collapse;
  font-family: var(--font-sans);
  font-size: 0.92rem;
  line-height: 1.55;
}

.study-table th,
.study-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border-subtle);
  border-right: 1px solid var(--border-subtle);
  vertical-align: top;
  text-align: start;
}

.study-table th:last-child,
.study-table td:last-child {
  border-right: none;
}

.study-table tr:last-child td {
  border-bottom: none;
}

.study-table th {
  background: var(--bg-elevated);
  font-weight: 700;
  color: var(--text-primary);
  text-wrap: balance;
}

.study-table td p {
  margin: 0 0 0.6em;
}

.study-table td p:last-child {
  margin-bottom: 0;
}

/* Figures & Math Blocks */
.study-figure {
  margin: 1.75em 0;
  padding: 1rem;
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: 0.75rem;
  text-align: center;
}

.study-figure img {
  max-width: 100%;
  height: auto;
  border-radius: 0.45rem;
  cursor: zoom-in;
}

.study-figure figcaption {
  margin-top: 0.6rem;
  font-family: var(--font-sans);
  font-size: 0.82rem;
  color: var(--text-muted);
}

.math-block {
  margin: 1.25em 0;
  padding: 0.85rem 1.25rem;
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: 0.55rem;
  font-family: var(--font-mono);
  font-size: 1.15rem;
  text-align: center;
}

.math-inline {
  font-family: var(--font-mono);
  font-size: 0.92em;
  background: var(--bg-elevated);
  padding: 0.12em 0.4em;
  border-radius: 0.3rem;
}

/* Footnotes */
.footnote-ref a {
  font-family: var(--font-mono);
  font-size: 0.75em;
  font-weight: 700;
  text-decoration: none;
  padding: 0.1em 0.3em;
  background: var(--brand-soft);
  color: var(--brand-primary);
  border-radius: 0.25rem;
}

.entry-footnotes {
  margin-top: 2.5rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--border-subtle);
  font-family: var(--font-sans);
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.entry-footnotes h4 {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
}

/* Semantic Highlight Colors (Light & Dark Adaptive) */
mark {
  padding: 0.08em 0.25em;
  border-radius: 0.22em;
  color: inherit;
}

mark.hl-yellow, mark.search-hl {
  background-color: light-dark(#fef08a, rgba(234, 179, 8, 0.32));
}
mark.hl-amber {
  background-color: light-dark(#fde68a, rgba(245, 158, 11, 0.28));
}
mark.hl-green {
  background-color: light-dark(#bbf7d0, rgba(34, 197, 94, 0.28));
}
mark.hl-cyan {
  background-color: light-dark(#a5f3fc, rgba(6, 182, 212, 0.28));
}
mark.hl-red, mark.hl-rose {
  background-color: light-dark(#fecdd3, rgba(244, 63, 94, 0.28));
}
mark.hl-orange {
  background-color: light-dark(#fed7aa, rgba(249, 115, 22, 0.28));
}
mark.hl-magenta, mark.hl-purple, mark.hl-lavender {
  background-color: light-dark(#e9d5ff, rgba(168, 85, 247, 0.28));
}
mark.hl-blue {
  background-color: light-dark(#bfdbfe, rgba(59, 130, 246, 0.28));
}
mark.hl-gray {
  background-color: light-dark(#e5e7eb, rgba(156, 163, 175, 0.25));
}

.tc-red { color: light-dark(#b91c1c, #f87171); }
.tc-green { color: light-dark(#15803d, #4ade80); }
.tc-purple { color: light-dark(#7e22ce, #c084fc); }
.tc-blue { color: light-dark(#1d4ed8, #60a5fa); }

/* Reader TOC & Related Entries */
.reader-sidebar {
  position: sticky;
  top: 5rem;
}

.related-section {
  margin-top: 2.5rem;
  padding-top: 1.75rem;
  border-top: 2px solid var(--border-subtle);
}

.prev-next-nav {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-top: 1.75rem;
}

.prev-next-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: 0.75rem;
  padding: 1rem;
  cursor: pointer;
  transition: border-color 0.15s ease;
}

.prev-next-card:hover {
  border-color: var(--brand-primary);
}

/* Scripture Explorer View */
.scripture-work-section {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: 0.9rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: var(--shadow-sm);
}

.books-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 0.75rem;
  margin-top: 1rem;
}

.book-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: 0.65rem;
  padding: 0.85rem 1rem;
  cursor: pointer;
  transition: all 0.15s ease;
}

.book-card:hover, .book-card.active {
  border-color: var(--brand-primary);
  background: var(--brand-soft);
}

.book-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 700;
  font-size: 0.95rem;
}

.chapter-pills-drawer {
  margin-top: 1rem;
  padding: 1rem;
  background: var(--bg-elevated);
  border-radius: 0.65rem;
  border: 1px solid var(--border-strong);
}

/* Tags Directory View */
.tags-cloud-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
}

.tag-directory-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  padding: 0.45rem 0.85rem;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.14s ease;
}

.tag-directory-pill:hover {
  border-color: var(--brand-primary);
  color: var(--brand-primary);
  transform: translateY(-1px);
}

/* Lightbox Modal */
.lightbox-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.82);
  display: grid;
  place-items: center;
  z-index: 100;
  padding: 2rem;
}

.lightbox-backdrop[hidden] {
  display: none;
}

.lightbox-backdrop img {
  max-width: 92vw;
  max-height: 88vh;
  border-radius: 0.5rem;
  background: #fff;
  padding: 0.5rem;
}
"""
