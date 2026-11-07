"""
Client-side interactive application for Michael Russell's Gospel Study Journal.
Supports instant search across 294 entries (190k+ words), 576 tags, and 1,158 scripture citations,
plus deep-link routing, Scripture Explorer, Tag Directory, Timeline, and Reader view.
"""

APP_JS = r"""
(() => {
  const DATA = window.GOSPEL_STUDY_DATA || { entries: [], booksOrder: [] };
  const entries = DATA.entries || [];
  const entryById = new Map(entries.map((e, i) => [e.id, { ...e, index: i }]));

  // Precompute Tag counts & Scripture Book -> Chapter -> Entry mappings
  const tagCounts = new Map();
  const tagLabels = new Map();
  const workBooksMap = new Map(); // work -> Map(book -> { count, entries: Set, chapters: Map(ch -> Set(entry)) })
  const yearsSet = new Set();

  const WORK_ORDER = [
    "Book of Mormon",
    "Doctrine & Covenants",
    "Pearl of Great Price",
    "New Testament",
    "Old Testament"
  ];
  WORK_ORDER.forEach(w => workBooksMap.set(w, new Map()));

  function formatTagSpaced(tag) {
    if (tag === tag.toUpperCase()) return tag;
    return tag
      .replace(/([a-z0-9])([A-Z])/g, "$1 $2")
      .replace(/([A-Z]+)([A-Z][a-z])/g, "$1 $2");
  }

  entries.forEach(e => {
    yearsSet.add(e.year);
    (e.tags || []).forEach(t => {
      tagCounts.set(t, (tagCounts.get(t) || 0) + 1);
      if (!tagLabels.has(t)) tagLabels.set(t, formatTagSpaced(t));
    });
    (e.scriptures || []).forEach(sc => {
      if (!workBooksMap.has(sc.work)) workBooksMap.set(sc.work, new Map());
      const bMap = workBooksMap.get(sc.work);
      if (!bMap.has(sc.book)) {
        bMap.set(sc.book, { book: sc.book, work: sc.work, entries: new Set(), chapters: new Map() });
      }
      const bInfo = bMap.get(sc.book);
      bInfo.entries.add(e.id);
      if (sc.chapter) {
        if (!bInfo.chapters.has(sc.chapter)) bInfo.chapters.set(sc.chapter, new Set());
        bInfo.chapters.get(sc.chapter).add(e.id);
      }
    });
  });

  const sortedTags = Array.from(tagCounts.entries())
    .map(([tag, count]) => ({ tag, label: tagLabels.get(tag), count }))
    .sort((a, b) => b.count - a.count || a.tag.localeCompare(b.tag));

  const sortedYears = Array.from(yearsSet).sort((a, b) => b - a);

  // Application State
  const state = {
    view: "studies", // 'studies' | 'scriptures' | 'tags' | 'timeline' | 'entry'
    activeEntryId: null,
    query: "",
    selectedTag: "",
    selectedWork: "",
    selectedBook: "",
    selectedChapter: null,
    selectedYear: "",
    selectedFeature: "", // '' | 'table' | 'chiasm' | 'figure'
    sortBy: "date-desc", // 'date-desc' | 'date-asc' | 'words-desc' | 'scriptures-desc'
    layoutMode: "grid", // 'grid' | 'list'
    expandedScriptureBook: "Alma",
    tagSearchQuery: "",
    tagSortMode: "popular", // 'popular' | 'alpha'
    readerFont: localStorage.getItem("gsj_font") || "serif",
  };

  // DOM Elements
  const dom = {
    searchInput: document.getElementById("global-search"),
    searchClear: document.getElementById("search-clear"),
    heroSection: document.getElementById("hero-section"),
    mainContent: document.getElementById("main-content"),
    navTabs: document.querySelectorAll(".nav-tab"),
    themeToggle: document.getElementById("theme-toggle"),
    randomBtn: document.getElementById("random-study-btn"),
    lightbox: document.getElementById("lightbox"),
    lightboxImg: document.getElementById("lightbox-img"),
  };

  function escapeHtml(str) {
    return String(str || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function highlightText(text, query) {
    if (!query || query.trim().length < 2) return escapeHtml(text);
    const terms = query
      .trim()
      .split(/\s+/)
      .filter(t => t.length >= 2)
      .map(t => t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
    if (!terms.length) return escapeHtml(text);
    const re = new RegExp(`(${terms.join("|")})`, "gi");
    return escapeHtml(text).replace(re, '<mark class="search-hl">$1</mark>');
  }

  function getSearchSnippet(entry, query) {
    if (!query || query.trim().length < 2) return "";
    const qClean = query.trim().toLowerCase().replace(/^#/, "");
    const terms = qClean.split(/\s+/).filter(Boolean);
    const body = entry.body_plain || "";
    const lowerBody = body.toLowerCase();
    let bestPos = -1;
    for (const t of terms) {
      const idx = lowerBody.indexOf(t);
      if (idx !== -1) {
        bestPos = idx;
        break;
      }
    }
    if (bestPos === -1) return "";
    const start = Math.max(0, bestPos - 70);
    const end = Math.min(body.length, bestPos + 150);
    let snippet = body.slice(start, end).replace(/\s+/g, " ").trim();
    if (start > 0) snippet = "…" + snippet;
    if (end < body.length) snippet = snippet + "…";
    return highlightText(snippet, query.replace(/^#/, ""));
  }

  function matchesEntry(entry) {
    if (state.selectedTag && !(entry.tags || []).includes(state.selectedTag)) {
      return false;
    }
    if (state.selectedWork && !(entry.scripture_works || []).includes(state.selectedWork)) {
      return false;
    }
    if (state.selectedBook) {
      if (state.selectedChapter) {
        const hasCh = (entry.scriptures || []).some(
          s => s.book === state.selectedBook && s.chapter === Number(state.selectedChapter)
        );
        if (!hasCh) return false;
      } else if (!(entry.scripture_books || []).includes(state.selectedBook)) {
        return false;
      }
    }
    if (state.selectedYear && String(entry.year) !== String(state.selectedYear)) {
      return false;
    }
    if (state.selectedFeature === "table" && !entry.has_table) return false;
    if (state.selectedFeature === "chiasm" && !entry.has_chiasm) return false;
    if (state.selectedFeature === "figure" && !entry.has_figure) return false;

    if (state.query && state.query.trim()) {
      const q = state.query.trim().toLowerCase();
      if (q.startsWith("#")) {
        const tagQuery = q.slice(1);
        return (entry.tags || []).some(
          t => t.toLowerCase().includes(tagQuery) || formatTagSpaced(t).toLowerCase().includes(tagQuery)
        );
      }
      const terms = q.split(/\s+/).filter(Boolean);
      const haystack = (
        entry.title + " " +
        entry.sources_raw + " " +
        (entry.tags || []).map(t => t + " " + formatTagSpaced(t)).join(" ") + " " +
        (entry.scriptures || []).map(s => s.ref).join(" ") + " " +
        entry.body_plain
      ).toLowerCase();
      return terms.every(term => haystack.includes(term));
    }
    return true;
  }

  function getFilteredEntries() {
    const list = entries.filter(matchesEntry);
    list.sort((a, b) => {
      if (state.sortBy === "date-asc") return a.date.localeCompare(b.date);
      if (state.sortBy === "words-desc") return b.word_count - a.word_count;
      if (state.sortBy === "scriptures-desc") return (b.scriptures?.length || 0) - (a.scriptures?.length || 0);
      return b.date.localeCompare(a.date);
    });
    return list;
  }

  // Routing
  function navigateToHash(hash) {
    if (window.location.hash !== hash) {
      window.location.hash = hash;
    } else {
      handleHashChange();
    }
  }

  function handleHashChange() {
    const rawHash = decodeURIComponent(window.location.hash.slice(1));
    if (rawHash.startsWith("entry/")) {
      const id = rawHash.slice(6);
      if (entryById.has(id)) {
        state.view = "entry";
        state.activeEntryId = id;
        render();
        window.scrollTo({ top: 0, behavior: "instant" });
        return;
      }
    } else if (rawHash.startsWith("tag/")) {
      state.selectedTag = rawHash.slice(4);
      state.view = "studies";
    } else if (rawHash.startsWith("scripture/")) {
      const parts = rawHash.slice(10).split("/");
      state.selectedBook = parts[0] || "";
      state.selectedChapter = parts[1] ? Number(parts[1]) : null;
      state.view = "studies";
    } else if (rawHash === "view/scriptures") {
      state.view = "scriptures";
    } else if (rawHash === "view/tags") {
      state.view = "tags";
    } else if (rawHash === "view/timeline") {
      state.view = "timeline";
    } else if (rawHash === "" || rawHash === "view/studies") {
      if (state.view === "entry") state.view = "studies";
    }
    render();
  }

  // Renderers
  function renderEntryCard(entry) {
    const primaryScriptures = (entry.scriptures || []).filter(s => s.is_primary).slice(0, 4);
    const displayScriptures = primaryScriptures.length
      ? primaryScriptures
      : (entry.scriptures || []).slice(0, 3);
    const snippet = state.query ? getSearchSnippet(entry, state.query) : "";

    return `
      <article class="entry-card" data-entry-id="${escapeHtml(entry.id)}">
        <div>
          <div class="card-meta-top">
            <span class="card-date">${escapeHtml(entry.display_date)}</span>
            <div class="card-badges">
              ${entry.has_chiasm ? '<span class="feature-badge">Chiasmus</span>' : ""}
              ${entry.has_table ? '<span class="feature-badge">Table</span>' : ""}
              ${entry.has_figure ? '<span class="feature-badge">Chart</span>' : ""}
              <span>${entry.reading_mins} min read</span>
            </div>
          </div>
          <h2 class="card-title">${highlightText(entry.title, state.query)}</h2>
          <p class="card-excerpt">${highlightText(entry.excerpt, state.query)}</p>
          ${snippet ? `<div class="search-match-snippet">${snippet}</div>` : ""}
        </div>
        <div class="card-footer">
          ${displayScriptures.length ? `
            <div class="pill-row">
              ${displayScriptures.map(sc => `
                <button type="button" class="scripture-pill" data-filter-book="${escapeHtml(sc.book)}" data-filter-ch="${sc.chapter || ""}" title="Filter by ${escapeHtml(sc.ref)}">
                  📖 ${escapeHtml(sc.ref)}
                </button>
              `).join("")}
              ${(entry.scriptures?.length || 0) > displayScriptures.length
                ? `<span class="count-badge">+${entry.scriptures.length - displayScriptures.length} more</span>`
                : ""}
            </div>
          ` : ""}
          <div class="pill-row">
            ${(entry.tags || []).slice(0, 5).map(t => `
              <button type="button" class="tag-pill" data-filter-tag="${escapeHtml(t)}">#${escapeHtml(t)}</button>
            `).join("")}
          </div>
        </div>
      </article>
    `;
  }

  function renderStudiesView() {
    const filtered = getFilteredEntries();
    const topBooks = Array.from(workBooksMap.values())
      .flatMap(m => Array.from(m.values()))
      .sort((a, b) => b.entries.size - a.entries.size)
      .slice(0, 18);

    return `
      <div class="filter-toolbar">
        <div class="filter-group">
          <select class="filter-select" id="filter-work" aria-label="Filter by Standard Work">
            <option value="">All Standard Works</option>
            ${WORK_ORDER.map(w => `<option value="${escapeHtml(w)}" ${state.selectedWork === w ? "selected" : ""}>${escapeHtml(w)}</option>`).join("")}
          </select>
          <select class="filter-select" id="filter-year" aria-label="Filter by Year">
            <option value="">All Years (2019–2025)</option>
            ${sortedYears.map(y => `<option value="${y}" ${String(state.selectedYear) === String(y) ? "selected" : ""}>${y}</option>`).join("")}
          </select>
          <select class="filter-select" id="filter-feature" aria-label="Filter by Feature">
            <option value="">All Study Types</option>
            <option value="table" ${state.selectedFeature === "table" ? "selected" : ""}>📊 Comparison Tables (30)</option>
            <option value="chiasm" ${state.selectedFeature === "chiasm" ? "selected" : ""}>🏛️ Chiasmus & Parallelism</option>
            <option value="figure" ${state.selectedFeature === "figure" ? "selected" : ""}>📈 Charts & Diagrams</option>
          </select>
          <select class="filter-select" id="filter-sort" aria-label="Sort Studies">
            <option value="date-desc" ${state.sortBy === "date-desc" ? "selected" : ""}>Newest First</option>
            <option value="date-asc" ${state.sortBy === "date-asc" ? "selected" : ""}>Oldest First</option>
            <option value="words-desc" ${state.sortBy === "words-desc" ? "selected" : ""}>Longest Deep-Dives</option>
            <option value="scriptures-desc" ${state.sortBy === "scriptures-desc" ? "selected" : ""}>Most Scripture Citations</option>
          </select>
        </div>

        <div class="filter-group">
          <div class="active-chips">
            ${state.selectedTag ? `<button type="button" class="active-filter-chip" id="clear-tag-chip">#${escapeHtml(state.selectedTag)} ✕</button>` : ""}
            ${state.selectedBook ? `<button type="button" class="active-filter-chip" id="clear-book-chip">📖 ${escapeHtml(state.selectedBook)}${state.selectedChapter ? " " + state.selectedChapter : ""} ✕</button>` : ""}
            ${(state.selectedTag || state.selectedBook || state.selectedWork || state.selectedYear || state.selectedFeature || state.query)
              ? `<button type="button" class="icon-btn" id="reset-all-filters">Reset All</button>`
              : ""}
          </div>
          <span class="results-summary">Showing <strong>${filtered.length}</strong> of ${entries.length} studies</span>
          <button type="button" class="icon-btn" id="toggle-layout-btn" title="Switch Grid/List view">
            ${state.layoutMode === "grid" ? "☰ List" : "⊞ Grid"}
          </button>
        </div>
      </div>

      <div class="explore-grid">
        <aside class="explore-sidebar">
          <div class="sidebar-card">
            <div class="sidebar-heading">
              <span>Top Scripture Books</span>
              <button type="button" class="icon-btn" style="padding:0.15rem 0.45rem;font-size:0.7rem;" data-goto-view="scriptures">All 64 →</button>
            </div>
            <div class="sidebar-list">
              ${topBooks.map(b => `
                <button type="button" class="sidebar-item-btn ${state.selectedBook === b.book ? "active" : ""}" data-sidebar-book="${escapeHtml(b.book)}">
                  <span>📖 ${escapeHtml(b.book)}</span>
                  <span class="count-badge">${b.entries.size}</span>
                </button>
              `).join("")}
            </div>
          </div>

          <div class="sidebar-card">
            <div class="sidebar-heading">
              <span>Popular Study Tags</span>
              <button type="button" class="icon-btn" style="padding:0.15rem 0.45rem;font-size:0.7rem;" data-goto-view="tags">All 576 →</button>
            </div>
            <div class="sidebar-list">
              ${sortedTags.slice(0, 25).map(t => `
                <button type="button" class="sidebar-item-btn ${state.selectedTag === t.tag ? "active" : ""}" data-sidebar-tag="${escapeHtml(t.tag)}">
                  <span>#${escapeHtml(t.tag)}</span>
                  <span class="count-badge">${t.count}</span>
                </button>
              `).join("")}
            </div>
          </div>
        </aside>

        <section>
          ${filtered.length === 0 ? `
            <div class="article-card" style="text-align:center;padding:3rem 1.5rem;">
              <h3>No matching gospel study entries found</h3>
              <p style="color:var(--text-secondary);">Try clearing one of your active filters or searching for a broader keyword, tag, or scripture book.</p>
              <button type="button" class="icon-btn" id="empty-reset-btn" style="margin-top:0.75rem;">Reset All Filters</button>
            </div>
          ` : `
            <div class="entries-grid ${state.layoutMode === "list" ? "list-mode" : ""}">
              ${filtered.map(renderEntryCard).join("")}
            </div>
          `}
        </section>
      </div>
    `;
  }

  function renderScripturesView() {
    let html = `
      <div style="margin-bottom:1.5rem;">
        <h2 style="font-family:var(--font-serif);font-size:1.75rem;margin-bottom:0.35rem;">Scripture Index Explorer</h2>
        <p style="color:var(--text-secondary);margin:0;">Browse all <strong>1,158</strong> scripture citations across <strong>64</strong> books in the Standard Works. Click any book to inspect its chapters or filter studies.</p>
      </div>
    `;

    WORK_ORDER.forEach(workName => {
      const bMap = workBooksMap.get(workName);
      if (!bMap || bMap.size === 0) return;
      const booksList = Array.from(bMap.values());

      const activeBookInWork = booksList.find(b => b.book === state.expandedScriptureBook);

      html += `
        <section class="scripture-work-section">
          <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:0.5rem;">
            <h3 style="font-family:var(--font-serif);font-size:1.35rem;margin:0;">${escapeHtml(workName)}</h3>
            <span class="count-badge">${booksList.length} books cited</span>
          </div>
          <div class="books-grid">
            ${booksList.map(b => `
              <div class="book-card ${state.expandedScriptureBook === b.book ? "active" : ""}" data-expand-book="${escapeHtml(b.book)}">
                <div class="book-card-header">
                  <span>📖 ${escapeHtml(b.book)}</span>
                  <span class="count-badge">${b.entries.size} ${b.entries.size === 1 ? "study" : "studies"}</span>
                </div>
                <div style="font-size:0.76rem;color:var(--text-muted);margin-top:0.35rem;">
                  ${b.chapters.size} ${b.chapters.size === 1 ? "chapter" : "chapters"} cited
                </div>
              </div>
            `).join("")}
          </div>

          ${activeBookInWork ? `
            <div class="chapter-pills-drawer">
              <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:0.75rem;margin-bottom:0.85rem;">
                <div>
                  <strong style="font-size:1.05rem;">${escapeHtml(activeBookInWork.book)}</strong>
                  <span style="color:var(--text-secondary);font-size:0.85rem;margin-left:0.5rem;">Select a chapter to view studies or view all ${activeBookInWork.entries.size} entries citing ${escapeHtml(activeBookInWork.book)}:</span>
                </div>
                <button type="button" class="icon-btn" data-filter-book="${escapeHtml(activeBookInWork.book)}" data-filter-ch="">
                  View All ${activeBookInWork.entries.size} Studies in ${escapeHtml(activeBookInWork.book)} →
                </button>
              </div>
              <div class="pill-row">
                ${Array.from(activeBookInWork.chapters.entries())
                  .sort((a, b) => a[0] - b[0])
                  .map(([ch, setIds]) => `
                    <button type="button" class="scripture-pill" data-filter-book="${escapeHtml(activeBookInWork.book)}" data-filter-ch="${ch}">
                      ${escapeHtml(activeBookInWork.book)} ${ch} <span style="opacity:0.75;">(${setIds.size})</span>
                    </button>
                  `).join("")}
              </div>
            </div>
          ` : ""}
        </section>
      `;
    });
    return html;
  }

  function renderTagsView() {
    const q = state.tagSearchQuery.trim().toLowerCase();
    let list = sortedTags.filter(
      t => !q || t.tag.toLowerCase().includes(q) || t.label.toLowerCase().includes(q)
    );
    if (state.tagSortMode === "alpha") {
      list = [...list].sort((a, b) => a.tag.localeCompare(b.tag));
    }

    return `
      <div class="filter-toolbar" style="margin-bottom:1.5rem;">
        <div>
          <h2 style="font-family:var(--font-serif);font-size:1.6rem;margin:0 0 0.2rem;">Topic & Tag Directory</h2>
          <p style="color:var(--text-secondary);font-size:0.88rem;margin:0;">Explore all <strong>${sortedTags.length}</strong> unique study tags across both journals.</p>
        </div>
        <div class="filter-group">
          <input type="search" id="tag-dir-search" class="filter-select" style="background-image:none;padding-right:0.75rem;min-width:220px;" placeholder="Filter tags (e.g. Atonement, Nephi)…" value="${escapeHtml(state.tagSearchQuery)}" />
          <button type="button" class="icon-btn ${state.tagSortMode === "popular" ? "active" : ""}" id="tag-sort-pop">Most Used</button>
          <button type="button" class="icon-btn ${state.tagSortMode === "alpha" ? "active" : ""}" id="tag-sort-alpha">A–Z</button>
        </div>
      </div>
      <div class="tags-cloud-grid">
        ${list.map(t => `
          <button type="button" class="tag-directory-pill" data-filter-tag="${escapeHtml(t.tag)}" title="${escapeHtml(t.label)} (${t.count} studies)">
            <span>#${escapeHtml(t.tag)}</span>
            <span class="count-badge">${t.count}</span>
          </button>
        `).join("")}
      </div>
    `;
  }

  function renderTimelineView() {
    const byYear = new Map();
    sortedYears.forEach(y => byYear.set(y, []));
    entries.forEach(e => {
      if (!byYear.has(e.year)) byYear.set(e.year, []);
      byYear.get(e.year).push(e);
    });

    return `
      <div style="margin-bottom:1.5rem;">
        <h2 style="font-family:var(--font-serif);font-size:1.75rem;margin-bottom:0.35rem;">Chronological Study Archive (2019–2025)</h2>
        <p style="color:var(--text-secondary);margin:0;">All 294 gospel study entries organized chronologically from the Archive and Current journals.</p>
      </div>
      ${sortedYears.map(year => {
        const yEntries = (byYear.get(year) || []).slice().sort((a, b) => b.date.localeCompare(a.date));
        const totalWords = yEntries.reduce((acc, e) => acc + e.word_count, 0);
        return `
          <section class="scripture-work-section">
            <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:0.5rem;margin-bottom:1rem;padding-bottom:0.75rem;border-bottom:1px solid var(--border-subtle);">
              <h3 style="font-family:var(--font-serif);font-size:1.5rem;margin:0;">${year}</h3>
              <div style="display:flex;gap:0.75rem;align-items:center;">
                <span class="count-badge">${yEntries.length} entries</span>
                <span class="count-badge">${totalWords.toLocaleString()} words</span>
              </div>
            </div>
            <div style="display:flex;flex-direction:column;gap:0.55rem;">
              ${yEntries.map(e => `
                <div style="display:flex;align-items:baseline;justify-content:space-between;gap:1rem;padding:0.5rem 0.65rem;border-radius:0.5rem;cursor:pointer;background:var(--bg-elevated);" data-entry-id="${escapeHtml(e.id)}">
                  <div style="display:flex;align-items:baseline;gap:0.85rem;flex-wrap:wrap;">
                    <span style="font-family:var(--font-mono);font-size:0.8rem;color:var(--text-muted);min-width:92px;">${escapeHtml(e.date)}</span>
                    <strong style="font-family:var(--font-serif);font-size:1.05rem;color:var(--text-primary);">${escapeHtml(e.title)}</strong>
                    ${(e.tags || []).slice(0, 3).map(t => `<span style="font-size:0.75rem;color:var(--text-muted);">#${escapeHtml(t)}</span>`).join("")}
                  </div>
                  <span style="font-size:0.78rem;color:var(--text-muted);white-space:nowrap;">${e.reading_mins} min</span>
                </div>
              `).join("")}
            </div>
          </section>
        `;
      }).join("")}
    `;
  }

  function renderArticleReaderView() {
    const entry = entryById.get(state.activeEntryId);
    if (!entry) return "";

    // Find related entries based on shared tags + scripture books
    const related = entries
      .filter(other => other.id !== entry.id)
      .map(other => {
        let score = 0;
        (other.tags || []).forEach(t => {
          if ((entry.tags || []).includes(t)) score += 3;
        });
        (other.scripture_books || []).forEach(b => {
          if ((entry.scripture_books || []).includes(b)) score += 1;
        });
        return { entry: other, score };
      })
      .filter(item => item.score > 0)
      .sort((a, b) => b.score - a.score || b.entry.date.localeCompare(a.entry.date))
      .slice(0, 4)
      .map(item => item.entry);

    const prevEntry = entry.index > 0 ? entries[entry.index - 1] : null;
    const nextEntry = entry.index < entries.length - 1 ? entries[entry.index + 1] : null;

    const hasSubheadings = (entry.subheadings || []).length > 1;
    document.documentElement.style.setProperty(
      "--article-font",
      state.readerFont === "sans" ? "var(--font-sans)" : "var(--font-serif)"
    );

    return `
      <div class="reader-container ${hasSubheadings ? "" : "no-toc"}">
        <article class="article-card">
          <div class="reader-topbar">
            <button type="button" class="back-btn" id="reader-back-btn">← Back to Studies</button>
            <div class="reader-controls">
              <button type="button" class="icon-btn" id="toggle-reader-font" title="Switch Serif / Sans reading font">
                Aa ${state.readerFont === "serif" ? "Serif" : "Sans"}
              </button>
              <button type="button" class="icon-btn" id="copy-entry-link" title="Copy direct link to this study">
                🔗 Share Link
              </button>
            </div>
          </div>

          <header class="article-header">
            <div class="article-meta-line">
              <span class="article-date">${escapeHtml(entry.display_date)}</span>
              <span>•</span>
              <span>${escapeHtml(entry.journal)}</span>
              <span>•</span>
              <span>${entry.word_count.toLocaleString()} words (${entry.reading_mins} min read)</span>
            </div>
            <h1 class="article-title">${escapeHtml(entry.title)}</h1>

            ${entry.sources_html ? `
              <div class="article-sources-box">
                <strong>Study Sources & Texts:</strong> ${entry.sources_html}
              </div>
            ` : ""}

            ${(entry.scriptures || []).length ? `
              <div class="pill-row" style="margin-bottom:0.65rem;">
                ${entry.scriptures.map(sc => `
                  <span style="display:inline-flex;align-items:center;gap:0.15rem;">
                    <button type="button" class="scripture-pill" data-filter-book="${escapeHtml(sc.book)}" data-filter-ch="${sc.chapter || ""}" title="See all studies on ${escapeHtml(sc.ref)}">
                      📖 ${escapeHtml(sc.ref)}
                    </button>
                  </span>
                `).join("")}
              </div>
            ` : ""}

            ${(entry.tags || []).length ? `
              <div class="pill-row">
                ${entry.tags.map(t => `
                  <button type="button" class="tag-pill" data-filter-tag="${escapeHtml(t)}">#${escapeHtml(t)}</button>
                `).join("")}
              </div>
            ` : ""}
          </header>

          <div class="article-body" id="reader-article-body">
            ${entry.body_html}
          </div>

          <div class="prev-next-nav">
            ${prevEntry ? `
              <div class="prev-next-card" data-entry-id="${escapeHtml(prevEntry.id)}">
                <div style="font-size:0.75rem;color:var(--text-muted);margin-bottom:0.25rem;">← Earlier Study (${escapeHtml(prevEntry.display_date)})</div>
                <strong style="font-family:var(--font-serif);font-size:1.05rem;">${escapeHtml(prevEntry.title)}</strong>
              </div>
            ` : `<div></div>`}
            ${nextEntry ? `
              <div class="prev-next-card" style="text-align:end;" data-entry-id="${escapeHtml(nextEntry.id)}">
                <div style="font-size:0.75rem;color:var(--text-muted);margin-bottom:0.25rem;">Later Study (${escapeHtml(nextEntry.display_date)}) →</div>
                <strong style="font-family:var(--font-serif);font-size:1.05rem;">${escapeHtml(nextEntry.title)}</strong>
              </div>
            ` : `<div></div>`}
          </div>

          ${related.length ? `
            <section class="related-section">
              <h3 style="font-family:var(--font-serif);font-size:1.35rem;margin-bottom:1rem;">Related Gospel Studies</h3>
              <div class="entries-grid">
                ${related.map(renderEntryCard).join("")}
              </div>
            </section>
          ` : ""}
        </article>

        ${hasSubheadings ? `
          <aside class="reader-sidebar">
            <div class="sidebar-card">
              <div class="sidebar-heading">On This Page</div>
              <div class="sidebar-list">
                ${entry.subheadings.map((sh, idx) => `
                  <button type="button" class="sidebar-item-btn" data-scroll-heading="${idx}">
                    <span>${escapeHtml(sh)}</span>
                  </button>
                `).join("")}
              </div>
            </div>
          </aside>
        ` : ""}
      </div>
    `;
  }

  function render() {
    // Update active nav tab
    dom.navTabs.forEach(tab => {
      const tabView = tab.getAttribute("data-view");
      tab.classList.toggle("active", tabView === state.view || (state.view === "entry" && tabView === "studies"));
    });

    // Show/hide hero banner on reader view for distraction-free reading
    if (dom.heroSection) {
      dom.heroSection.style.display = state.view === "entry" ? "none" : "block";
    }

    if (state.view === "entry") {
      dom.mainContent.innerHTML = renderArticleReaderView();
    } else if (state.view === "scriptures") {
      dom.mainContent.innerHTML = renderScripturesView();
    } else if (state.view === "tags") {
      dom.mainContent.innerHTML = renderTagsView();
    } else if (state.view === "timeline") {
      dom.mainContent.innerHTML = renderTimelineView();
    } else {
      dom.mainContent.innerHTML = renderStudiesView();
    }

    bindDynamicEvents();
  }

  function bindDynamicEvents() {
    // Entry card clicks
    dom.mainContent.querySelectorAll("[data-entry-id]").forEach(el => {
      el.addEventListener("click", ev => {
        if (ev.target.closest("button, a")) return;
        const id = el.getAttribute("data-entry-id");
        navigateToHash(`#entry/${encodeURIComponent(id)}`);
      });
    });

    // Tag pill clicks
    dom.mainContent.querySelectorAll("[data-filter-tag], [data-sidebar-tag]").forEach(btn => {
      btn.addEventListener("click", ev => {
        ev.stopPropagation();
        const tag = btn.getAttribute("data-filter-tag") || btn.getAttribute("data-sidebar-tag");
        state.selectedTag = state.selectedTag === tag ? "" : tag;
        state.view = "studies";
        navigateToHash(state.selectedTag ? `#tag/${encodeURIComponent(state.selectedTag)}` : "#view/studies");
      });
    });

    // Scripture pill / book clicks
    dom.mainContent.querySelectorAll("[data-filter-book], [data-sidebar-book]").forEach(btn => {
      btn.addEventListener("click", ev => {
        ev.stopPropagation();
        const book = btn.getAttribute("data-filter-book") || btn.getAttribute("data-sidebar-book");
        const ch = btn.getAttribute("data-filter-ch");
        if (btn.hasAttribute("data-sidebar-book") && state.selectedBook === book && !state.selectedChapter) {
          state.selectedBook = "";
          state.selectedChapter = null;
          navigateToHash("#view/studies");
        } else {
          state.selectedBook = book;
          state.selectedChapter = ch ? Number(ch) : null;
          state.view = "studies";
          const hash = state.selectedChapter
            ? `#scripture/${encodeURIComponent(book)}/${state.selectedChapter}`
            : `#scripture/${encodeURIComponent(book)}`;
          navigateToHash(hash);
        }
      });
    });

    // Expand book in Scripture Explorer
    dom.mainContent.querySelectorAll("[data-expand-book]").forEach(card => {
      card.addEventListener("click", () => {
        const b = card.getAttribute("data-expand-book");
        state.expandedScriptureBook = state.expandedScriptureBook === b ? "" : b;
        render();
      });
    });

    // Goto view buttons
    dom.mainContent.querySelectorAll("[data-goto-view]").forEach(btn => {
      btn.addEventListener("click", () => {
        const v = btn.getAttribute("data-goto-view");
        navigateToHash(`#view/${v}`);
      });
    });

    // Filter selects
    const workSel = document.getElementById("filter-work");
    if (workSel) {
      workSel.addEventListener("change", () => {
        state.selectedWork = workSel.value;
        render();
      });
    }
    const yearSel = document.getElementById("filter-year");
    if (yearSel) {
      yearSel.addEventListener("change", () => {
        state.selectedYear = yearSel.value;
        render();
      });
    }
    const featSel = document.getElementById("filter-feature");
    if (featSel) {
      featSel.addEventListener("change", () => {
        state.selectedFeature = featSel.value;
        render();
      });
    }
    const sortSel = document.getElementById("filter-sort");
    if (sortSel) {
      sortSel.addEventListener("change", () => {
        state.sortBy = sortSel.value;
        render();
      });
    }

    // Active chip clears
    const clearTag = document.getElementById("clear-tag-chip");
    if (clearTag) {
      clearTag.addEventListener("click", () => {
        state.selectedTag = "";
        navigateToHash("#view/studies");
      });
    }
    const clearBook = document.getElementById("clear-book-chip");
    if (clearBook) {
      clearBook.addEventListener("click", () => {
        state.selectedBook = "";
        state.selectedChapter = null;
        navigateToHash("#view/studies");
      });
    }
    const resetAll = document.getElementById("reset-all-filters") || document.getElementById("empty-reset-btn");
    if (resetAll) {
      resetAll.addEventListener("click", () => {
        state.query = "";
        state.selectedTag = "";
        state.selectedWork = "";
        state.selectedBook = "";
        state.selectedChapter = null;
        state.selectedYear = "";
        state.selectedFeature = "";
        if (dom.searchInput) dom.searchInput.value = "";
        navigateToHash("#view/studies");
      });
    }

    const toggleLayout = document.getElementById("toggle-layout-btn");
    if (toggleLayout) {
      toggleLayout.addEventListener("click", () => {
        state.layoutMode = state.layoutMode === "grid" ? "list" : "grid";
        render();
      });
    }

    // Tag directory search & sort
    const tagSearch = document.getElementById("tag-dir-search");
    if (tagSearch) {
      tagSearch.addEventListener("input", () => {
        state.tagSearchQuery = tagSearch.value;
        const pos = tagSearch.selectionStart;
        render();
        const newInput = document.getElementById("tag-dir-search");
        if (newInput) {
          newInput.focus();
          newInput.setSelectionRange(pos, pos);
        }
      });
    }
    const tagSortPop = document.getElementById("tag-sort-pop");
    if (tagSortPop) {
      tagSortPop.addEventListener("click", () => {
        state.tagSortMode = "popular";
        render();
      });
    }
    const tagSortAlpha = document.getElementById("tag-sort-alpha");
    if (tagSortAlpha) {
      tagSortAlpha.addEventListener("click", () => {
        state.tagSortMode = "alpha";
        render();
      });
    }

    // Reader controls
    const backBtn = document.getElementById("reader-back-btn");
    if (backBtn) {
      backBtn.addEventListener("click", () => {
        state.view = "studies";
        navigateToHash("#view/studies");
      });
    }
    const fontBtn = document.getElementById("toggle-reader-font");
    if (fontBtn) {
      fontBtn.addEventListener("click", () => {
        state.readerFont = state.readerFont === "serif" ? "sans" : "serif";
        localStorage.setItem("gsj_font", state.readerFont);
        render();
      });
    }
    const copyBtn = document.getElementById("copy-entry-link");
    if (copyBtn) {
      copyBtn.addEventListener("click", () => {
        navigator.clipboard?.writeText(window.location.href);
        copyBtn.textContent = "✓ Copied!";
        setTimeout(() => { copyBtn.textContent = "🔗 Share Link"; }, 1800);
      });
    }

    // TOC heading scroll
    dom.mainContent.querySelectorAll("[data-scroll-heading]").forEach(btn => {
      btn.addEventListener("click", () => {
        const idx = Number(btn.getAttribute("data-scroll-heading"));
        const headings = document.querySelectorAll("#reader-article-body .entry-subheading");
        if (headings[idx]) {
          headings[idx].scrollIntoView({ behavior: "smooth", block: "start" });
        }
      });
    });

    // Lightbox for study figures
    dom.mainContent.querySelectorAll(".study-figure img").forEach(img => {
      img.addEventListener("click", () => {
        if (dom.lightbox && dom.lightboxImg) {
          dom.lightboxImg.src = img.src;
          dom.lightboxImg.alt = img.alt;
          dom.lightbox.hidden = false;
        }
      });
    });
  }

  // Global Listeners
  if (dom.searchInput) {
    dom.searchInput.addEventListener("input", () => {
      state.query = dom.searchInput.value;
      if (state.view !== "studies") state.view = "studies";
      render();
    });
  }
  if (dom.searchClear) {
    dom.searchClear.addEventListener("click", () => {
      state.query = "";
      if (dom.searchInput) {
        dom.searchInput.value = "";
        dom.searchInput.focus();
      }
      render();
    });
  }

  dom.navTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      const v = tab.getAttribute("data-view");
      state.view = v;
      navigateToHash(`#view/${v}`);
    });
  });

  if (dom.randomBtn) {
    dom.randomBtn.addEventListener("click", () => {
      const rand = entries[Math.floor(Math.random() * entries.length)];
      if (rand) navigateToHash(`#entry/${encodeURIComponent(rand.id)}`);
    });
  }

  if (dom.themeToggle) {
    const savedTheme = localStorage.getItem("gsj_theme");
    if (savedTheme) document.documentElement.setAttribute("data-theme", savedTheme);
    dom.themeToggle.addEventListener("click", () => {
      const cur = document.documentElement.getAttribute("data-theme");
      const isDark = cur
        ? cur === "dark"
        : window.matchMedia("(prefers-color-scheme: dark)").matches;
      const next = isDark ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      localStorage.setItem("gsj_theme", next);
    });
  }

  if (dom.lightbox) {
    dom.lightbox.addEventListener("click", () => {
      dom.lightbox.hidden = true;
    });
  }

  window.addEventListener("keydown", ev => {
    if ((ev.metaKey || ev.ctrlKey) && ev.key.toLowerCase() === "k") {
      ev.preventDefault();
      if (state.view === "entry") {
        state.view = "studies";
        render();
      }
      dom.searchInput?.focus();
    } else if (ev.key === "/" && document.activeElement !== dom.searchInput && !["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement?.tagName)) {
      ev.preventDefault();
      if (state.view === "entry") {
        state.view = "studies";
        render();
      }
      dom.searchInput?.focus();
    } else if (ev.key === "Escape" && dom.lightbox && !dom.lightbox.hidden) {
      dom.lightbox.hidden = true;
    }
  });

  window.addEventListener("hashchange", handleHashChange);
  handleHashChange();
})();
"""
