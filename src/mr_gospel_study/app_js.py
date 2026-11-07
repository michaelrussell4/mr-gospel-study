"""
Client-side interactive application for Michael Russell's Gospel Study Journal.
Supports instant search across 294 entries (190k+ words), 576 tags, and 1,226 scripture citations,
plus Data Science Visualizations (Insights), Scripture Explorer, Topic Directory, Timeline, and Reader view.
"""

APP_JS = r"""
(() => {
  const DATA = window.GOSPEL_STUDY_DATA || { entries: [], stats: {} };
  const entries = DATA.entries || [];
  const stats = DATA.stats || {};
  const entryById = new Map(entries.map((e, i) => [e.id, { ...e, index: i }]));

  const WORK_ORDER = [
    "Book of Mormon",
    "Doctrine & Covenants",
    "Pearl of Great Price",
    "New Testament",
    "Old Testament"
  ];

  const WORK_COLORS = {
    "Book of Mormon": "#1d4ed8",
    "New Testament": "#0f766e",
    "Old Testament": "#b45309",
    "Doctrine & Covenants": "#7e22ce",
    "Pearl of Great Price": "#be123c"
  };

  // Canonical books and chapter counts across all 5 Standard Works
  const CANONICAL_BOOKS = [
    // Book of Mormon (15)
    { book: "1 Nephi", work: "Book of Mormon", chapters: 22 },
    { book: "2 Nephi", work: "Book of Mormon", chapters: 33 },
    { book: "Jacob", work: "Book of Mormon", chapters: 7 },
    { book: "Enos", work: "Book of Mormon", chapters: 1 },
    { book: "Jarom", work: "Book of Mormon", chapters: 1 },
    { book: "Omni", work: "Book of Mormon", chapters: 1 },
    { book: "Words of Mormon", work: "Book of Mormon", chapters: 1 },
    { book: "Mosiah", work: "Book of Mormon", chapters: 29 },
    { book: "Alma", work: "Book of Mormon", chapters: 63 },
    { book: "Helaman", work: "Book of Mormon", chapters: 16 },
    { book: "3 Nephi", work: "Book of Mormon", chapters: 30 },
    { book: "4 Nephi", work: "Book of Mormon", chapters: 1 },
    { book: "Mormon", work: "Book of Mormon", chapters: 9 },
    { book: "Ether", work: "Book of Mormon", chapters: 15 },
    { book: "Moroni", work: "Book of Mormon", chapters: 10 },
    // Doctrine & Covenants (1)
    { book: "D&C", work: "Doctrine & Covenants", chapters: 138 },
    // Pearl of Great Price (5)
    { book: "Moses", work: "Pearl of Great Price", chapters: 8 },
    { book: "Abraham", work: "Pearl of Great Price", chapters: 5 },
    { book: "Joseph Smith—Matthew", work: "Pearl of Great Price", chapters: 1 },
    { book: "Joseph Smith—History", work: "Pearl of Great Price", chapters: 1 },
    { book: "Articles of Faith", work: "Pearl of Great Price", chapters: 1 },
    // New Testament (27)
    { book: "Matthew", work: "New Testament", chapters: 28 },
    { book: "Mark", work: "New Testament", chapters: 16 },
    { book: "Luke", work: "New Testament", chapters: 24 },
    { book: "John", work: "New Testament", chapters: 21 },
    { book: "Acts", work: "New Testament", chapters: 28 },
    { book: "Romans", work: "New Testament", chapters: 16 },
    { book: "1 Corinthians", work: "New Testament", chapters: 16 },
    { book: "2 Corinthians", work: "New Testament", chapters: 13 },
    { book: "Galatians", work: "New Testament", chapters: 6 },
    { book: "Ephesians", work: "New Testament", chapters: 6 },
    { book: "Philippians", work: "New Testament", chapters: 4 },
    { book: "Colossians", work: "New Testament", chapters: 4 },
    { book: "1 Thessalonians", work: "New Testament", chapters: 5 },
    { book: "2 Thessalonians", work: "New Testament", chapters: 3 },
    { book: "1 Timothy", work: "New Testament", chapters: 6 },
    { book: "2 Timothy", work: "New Testament", chapters: 4 },
    { book: "Titus", work: "New Testament", chapters: 3 },
    { book: "Philemon", work: "New Testament", chapters: 1 },
    { book: "Hebrews", work: "New Testament", chapters: 13 },
    { book: "James", work: "New Testament", chapters: 5 },
    { book: "1 Peter", work: "New Testament", chapters: 5 },
    { book: "2 Peter", work: "New Testament", chapters: 3 },
    { book: "1 John", work: "New Testament", chapters: 5 },
    { book: "2 John", work: "New Testament", chapters: 1 },
    { book: "3 John", work: "New Testament", chapters: 1 },
    { book: "Jude", work: "New Testament", chapters: 1 },
    { book: "Revelation", work: "New Testament", chapters: 22 },
    // Old Testament (39)
    { book: "Genesis", work: "Old Testament", chapters: 50 },
    { book: "Exodus", work: "Old Testament", chapters: 40 },
    { book: "Leviticus", work: "Old Testament", chapters: 27 },
    { book: "Numbers", work: "Old Testament", chapters: 36 },
    { book: "Deuteronomy", work: "Old Testament", chapters: 34 },
    { book: "Joshua", work: "Old Testament", chapters: 24 },
    { book: "Judges", work: "Old Testament", chapters: 21 },
    { book: "Ruth", work: "Old Testament", chapters: 4 },
    { book: "1 Samuel", work: "Old Testament", chapters: 31 },
    { book: "2 Samuel", work: "Old Testament", chapters: 24 },
    { book: "1 Kings", work: "Old Testament", chapters: 22 },
    { book: "2 Kings", work: "Old Testament", chapters: 25 },
    { book: "1 Chronicles", work: "Old Testament", chapters: 29 },
    { book: "2 Chronicles", work: "Old Testament", chapters: 36 },
    { book: "Ezra", work: "Old Testament", chapters: 10 },
    { book: "Nehemiah", work: "Old Testament", chapters: 13 },
    { book: "Esther", work: "Old Testament", chapters: 10 },
    { book: "Job", work: "Old Testament", chapters: 42 },
    { book: "Psalms", work: "Old Testament", chapters: 150 },
    { book: "Proverbs", work: "Old Testament", chapters: 31 },
    { book: "Ecclesiastes", work: "Old Testament", chapters: 12 },
    { book: "Song of Solomon", work: "Old Testament", chapters: 8 },
    { book: "Isaiah", work: "Old Testament", chapters: 66 },
    { book: "Jeremiah", work: "Old Testament", chapters: 52 },
    { book: "Lamentations", work: "Old Testament", chapters: 5 },
    { book: "Ezekiel", work: "Old Testament", chapters: 48 },
    { book: "Daniel", work: "Old Testament", chapters: 12 },
    { book: "Hosea", work: "Old Testament", chapters: 14 },
    { book: "Joel", work: "Old Testament", chapters: 3 },
    { book: "Amos", work: "Old Testament", chapters: 9 },
    { book: "Obadiah", work: "Old Testament", chapters: 1 },
    { book: "Jonah", work: "Old Testament", chapters: 4 },
    { book: "Micah", work: "Old Testament", chapters: 7 },
    { book: "Nahum", work: "Old Testament", chapters: 3 },
    { book: "Habakkuk", work: "Old Testament", chapters: 3 },
    { book: "Zephaniah", work: "Old Testament", chapters: 3 },
    { book: "Haggai", work: "Old Testament", chapters: 2 },
    { book: "Zechariah", work: "Old Testament", chapters: 14 },
    { book: "Malachi", work: "Old Testament", chapters: 4 }
  ];

  // Precompute Tag counts, Co-occurrences & Scripture Book -> Chapter -> Entry mappings
  const tagCounts = new Map();
  const tagWords = new Map();
  const tagLabels = new Map();
  const pairCounts = new Map();
  const workBooksMap = new Map();
  const bookLookupMap = new Map();
  const yearsSet = new Set();

  WORK_ORDER.forEach(w => workBooksMap.set(w, new Map()));

  function formatTagSpaced(tag) {
    if (tag === tag.toUpperCase()) return tag;
    return tag
      .replace(/([a-z0-9])([A-Z])/g, "$1 $2")
      .replace(/([A-Z]+)([A-Z][a-z])/g, "$1 $2");
  }

  entries.forEach(e => {
    yearsSet.add(e.year);
    const uniqueTags = Array.from(new Set(e.tags || []));
    uniqueTags.forEach(t => {
      tagCounts.set(t, (tagCounts.get(t) || 0) + 1);
      tagWords.set(t, (tagWords.get(t) || 0) + (e.word_count || 0));
      if (!tagLabels.has(t)) tagLabels.set(t, formatTagSpaced(t));
    });
    for (let i = 0; i < uniqueTags.length; i++) {
      for (let j = i + 1; j < uniqueTags.length; j++) {
        const [a, b] = uniqueTags[i] < uniqueTags[j]
          ? [uniqueTags[i], uniqueTags[j]]
          : [uniqueTags[j], uniqueTags[i]];
        const key = `${a}|||${b}`;
        pairCounts.set(key, (pairCounts.get(key) || 0) + 1);
      }
    }
    (e.scriptures || []).forEach(sc => {
      if (!workBooksMap.has(sc.work)) workBooksMap.set(sc.work, new Map());
      const bMap = workBooksMap.get(sc.work);
      if (!bMap.has(sc.book)) {
        const info = { book: sc.book, work: sc.work, entries: new Set(), chapters: new Map(), citations: 0 };
        bMap.set(sc.book, info);
        bookLookupMap.set(sc.book, info);
      }
      const bInfo = bMap.get(sc.book);
      bInfo.entries.add(e.id);
      bInfo.citations += 1;
      if (sc.chapter) {
        if (!bInfo.chapters.has(sc.chapter)) bInfo.chapters.set(sc.chapter, new Set());
        bInfo.chapters.get(sc.chapter).add(e.id);
      }
    });
  });

  const sortedTags = Array.from(tagCounts.entries())
    .map(([tag, count]) => ({
      tag,
      label: tagLabels.get(tag),
      count,
      words: tagWords.get(tag) || 0
    }))
    .sort((a, b) => b.count - a.count || a.tag.localeCompare(b.tag));

  const topTagPairs = Array.from(pairCounts.entries())
    .map(([key, count]) => {
      const [a, b] = key.split("|||");
      const union = (tagCounts.get(a) || 0) + (tagCounts.get(b) || 0) - count;
      const jaccard = union > 0 ? Math.round((count / union) * 100) : 0;
      return { a, b, count, jaccard };
    })
    .filter(p => p.count >= 3)
    .sort((x, y) => y.count - x.count || y.jaccard - x.jaccard)
    .slice(0, 16);

  const sortedYears = Array.from(yearsSet).sort((a, b) => b - a);
  const ascYears = [...sortedYears].sort((a, b) => a - b);

  // Word count statistics
  const wordCountsSorted = entries.map(e => e.word_count).sort((a, b) => a - b);
  const medianWords = wordCountsSorted.length
    ? wordCountsSorted[Math.floor(wordCountsSorted.length / 2)]
    : 0;
  const p90Words = wordCountsSorted.length
    ? wordCountsSorted[Math.floor(wordCountsSorted.length * 0.9)]
    : 0;
  const maxWordsEntry = entries.reduce((best, e) => (!best || e.word_count > best.word_count ? e : best), null);
  const meanWords = entries.length ? Math.round((stats.total_words || 0) / entries.length) : 0;
  const totalUniqueChaptersCited = Array.from(bookLookupMap.values()).reduce(
    (acc, b) => acc + b.chapters.size,
    0
  );

  // Application State
  const state = {
    view: "studies", // 'studies' | 'insights' | 'scriptures' | 'tags' | 'timeline' | 'entry'
    activeEntryId: null,
    query: "",
    selectedTag: "",
    selectedTag2: "",
    selectedWork: "",
    selectedBook: "",
    selectedChapter: null,
    selectedYear: "",
    selectedMonth: "", // 'YYYY-MM'
    selectedFeature: "", // '' | 'table' | 'chiasm' | 'figure'
    sortBy: "date-desc",
    layoutMode: "grid",
    expandedScriptureBook: "Alma",
    tagSearchQuery: "",
    tagSortMode: "popular",
    readerFont: localStorage.getItem("gsj_reader_font_v2") || "sans",
    // Insights view interactive state
    tsGranularity: "quarter", // 'year' | 'quarter' | 'month'
    tsMetric: "entries", // 'entries' | 'words' | 'avg_words'
    calMetric: "entries", // 'entries' | 'words'
    heatmapWork: "all", // 'all' | Standard Work name
    heatmapShowUncitedBooks: false,
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
    if (state.selectedTag2 && !(entry.tags || []).includes(state.selectedTag2)) {
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
    if (state.selectedMonth && entry.month !== state.selectedMonth) {
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
      state.selectedTag2 = "";
      state.view = "studies";
    } else if (rawHash.startsWith("scripture/")) {
      const parts = rawHash.slice(10).split("/");
      state.selectedBook = parts[0] || "";
      state.selectedChapter = parts[1] ? Number(parts[1]) : null;
      state.view = "studies";
    } else if (rawHash === "view/insights") {
      state.view = "insights";
    } else if (rawHash === "view/scriptures") {
      state.view = "scriptures";
    } else if (rawHash === "view/tags") {
      state.view = "tags";
    } else if (rawHash === "view/timeline") {
      state.view = "timeline";
    } else if (rawHash === "" || rawHash === "view/studies") {
      if (state.view === "entry") state.view = "studies";
      else if (rawHash === "view/studies") state.view = "studies";
    }
    render();
  }

  function getHeatClass(val, thresholds) {
    if (!val || val <= 0) return "heat-0";
    if (val <= thresholds[0]) return "heat-1";
    if (val <= thresholds[1]) return "heat-2";
    if (val <= thresholds[2]) return "heat-3";
    if (val <= thresholds[3]) return "heat-4";
    return "heat-5";
  }

  // ==========================================================================
  // Renderers
  // ==========================================================================
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

    const hasActiveFilter = Boolean(
      state.selectedTag ||
      state.selectedTag2 ||
      state.selectedBook ||
      state.selectedWork ||
      state.selectedYear ||
      state.selectedMonth ||
      state.selectedFeature ||
      state.query
    );

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
            ${state.selectedTag2 ? `<button type="button" class="active-filter-chip" id="clear-tag2-chip">#${escapeHtml(state.selectedTag2)} ✕</button>` : ""}
            ${state.selectedBook ? `<button type="button" class="active-filter-chip" id="clear-book-chip">📖 ${escapeHtml(state.selectedBook)}${state.selectedChapter ? " " + state.selectedChapter : ""} ✕</button>` : ""}
            ${state.selectedMonth ? `<button type="button" class="active-filter-chip" id="clear-month-chip">🗓️ ${escapeHtml(state.selectedMonth)} ✕</button>` : ""}
            ${hasActiveFilter ? `<button type="button" class="icon-btn" id="reset-all-filters">Reset All</button>` : ""}
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
              <span>Popular Study Topics</span>
              <button type="button" class="icon-btn" style="padding:0.15rem 0.45rem;font-size:0.7rem;" data-goto-view="tags">All ${sortedTags.length} →</button>
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

  // ==========================================================================
  // Insights & Data Visualizations View
  // ==========================================================================
  function buildTimeSeriesBuckets() {
    const map = new Map();
    if (state.tsGranularity === "year") {
      ascYears.forEach(y => map.set(String(y), { key: String(y), label: String(y), entries: 0, words: 0, filterType: "year", filterVal: String(y) }));
      entries.forEach(e => {
        const b = map.get(String(e.year));
        if (b) {
          b.entries += 1;
          b.words += e.word_count;
        }
      });
    } else if (state.tsGranularity === "quarter") {
      ascYears.forEach(y => {
        for (let q = 1; q <= 4; q++) {
          if (y === 2019 && q === 1) continue;
          const k = `${y}-Q${q}`;
          map.set(k, { key: k, label: `${String(y).slice(2)} Q${q}`, entries: 0, words: 0, filterType: "year", filterVal: String(y) });
        }
      });
      entries.forEach(e => {
        const q = Math.ceil((e.month_num || 1) / 3);
        const k = `${e.year}-Q${q}`;
        const b = map.get(k);
        if (b) {
          b.entries += 1;
          b.words += e.word_count;
        }
      });
    } else {
      // Monthly from 2019-06 to 2025-10
      for (let y = 2019; y <= 2025; y++) {
        for (let m = 1; m <= 12; m++) {
          if (y === 2019 && m < 6) continue;
          if (y === 2025 && m > 10) continue;
          const mm = String(m).padStart(2, "0");
          const k = `${y}-${mm}`;
          map.set(k, { key: k, label: k, entries: 0, words: 0, filterType: "month", filterVal: k });
        }
      }
      entries.forEach(e => {
        const b = map.get(e.month);
        if (b) {
          b.entries += 1;
          b.words += e.word_count;
        }
      });
    }

    return Array.from(map.values()).map(b => ({
      ...b,
      avg_words: b.entries > 0 ? Math.round(b.words / b.entries) : 0
    }));
  }

  function renderTimeSeriesSvg() {
    const buckets = buildTimeSeriesBuckets();
    const metric = state.tsMetric;
    const vals = buckets.map(b => b[metric]);
    const maxVal = Math.max(...vals, 1);
    const nonZeroVals = vals.filter(v => v > 0);
    const meanVal = nonZeroVals.length
      ? Math.round(nonZeroVals.reduce((a, b) => a + b, 0) / nonZeroVals.length)
      : 0;

    const svgW = 920;
    const svgH = 265;
    const padL = 52;
    const padR = 24;
    const padT = 24;
    const padB = 42;
    const plotW = svgW - padL - padR;
    const plotH = svgH - padT - padB;

    const stepX = plotW / Math.max(buckets.length, 1);
    const barW = Math.max(4, Math.min(48, stepX * 0.72));

    const yTicks = [0, 0.25, 0.5, 0.75, 1].map(t => ({
      val: Math.round(maxVal * t),
      y: padT + plotH * (1 - t)
    }));

    const meanY = padT + plotH * (1 - Math.min(meanVal / maxVal, 1));

    const formatVal = v => (metric === "entries" ? String(v) : v >= 1000 ? `${(v / 1000).toFixed(1)}k` : String(v));

    return `
      <div class="chart-svg-wrap">
        <svg class="bar-chart-svg" viewBox="0 0 ${svgW} ${svgH}" role="img" aria-label="Study cadence and volume bar chart over time">
          ${yTicks.map(t => `
            <line class="grid-line" x1="${padL}" y1="${t.y.toFixed(1)}" x2="${svgW - padR}" y2="${t.y.toFixed(1)}" />
            <text class="axis-label" x="${padL - 8}" y="${(t.y + 3.5).toFixed(1)}" text-anchor="end">${formatVal(t.val)}</text>
          `).join("")}

          ${meanVal > 0 ? `
            <line class="mean-line" x1="${padL}" y1="${meanY.toFixed(1)}" x2="${svgW - padR}" y2="${meanY.toFixed(1)}" />
            <text class="axis-label" x="${svgW - padR - 4}" y="${(meanY - 5).toFixed(1)}" text-anchor="end" style="fill:var(--brand-accent);font-weight:700;">
              Mean: ${meanVal.toLocaleString()}
            </text>
          ` : ""}

          ${buckets.map((b, idx) => {
            const v = b[metric];
            const bh = Math.max(v > 0 ? 3 : 0, (v / maxVal) * plotH);
            const x = padL + idx * stepX + (stepX - barW) / 2;
            const y = padT + plotH - bh;
            const showXLabel =
              state.tsGranularity === "year" ||
              (state.tsGranularity === "quarter" && (idx % 2 === 0 || buckets.length <= 16)) ||
              (state.tsGranularity === "month" && b.key.endsWith("-01"));
            const xLabelText = state.tsGranularity === "month" ? b.key.slice(0, 4) : b.label;
            const showBarVal = state.tsGranularity === "year" || (state.tsGranularity === "quarter" && v > 0);

            return `
              <g>
                <rect
                  class="chart-bar"
                  x="${x.toFixed(1)}"
                  y="${y.toFixed(1)}"
                  width="${barW.toFixed(1)}"
                  height="${bh.toFixed(1)}"
                  rx="3"
                  data-ts-filter-type="${b.filterType}"
                  data-ts-filter-val="${escapeHtml(b.filterVal)}"
                >
                  <title>${escapeHtml(b.key)}: ${b.entries} studies • ${b.words.toLocaleString()} words (avg ${b.avg_words.toLocaleString()} words/study)</title>
                </rect>
                ${showBarVal ? `
                  <text class="bar-val-label" x="${(x + barW / 2).toFixed(1)}" y="${(y - 5).toFixed(1)}" text-anchor="middle">
                    ${formatVal(v)}
                  </text>
                ` : ""}
                ${showXLabel ? `
                  <text class="axis-label" x="${(x + barW / 2).toFixed(1)}" y="${svgH - 14}" text-anchor="middle">
                    ${escapeHtml(xLabelText)}
                  </text>
                ` : ""}
              </g>
            `;
          }).join("")}
        </svg>
      </div>
    `;
  }

  function renderMonthlyCalendarHeatmap() {
    const monthsNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    const cellMap = new Map();
    entries.forEach(e => {
      const k = `${e.year}-${String(e.month_num).padStart(2, "0")}`;
      if (!cellMap.has(k)) cellMap.set(k, { entries: 0, words: 0, titles: [] });
      const c = cellMap.get(k);
      c.entries += 1;
      c.words += e.word_count;
      if (c.titles.length < 4) c.titles.push(e.title);
    });

    const isWords = state.calMetric === "words";
    const thresholds = isWords ? [1200, 3000, 6000, 10000] : [1, 3, 6, 10];

    return `
      <div class="calendar-heatmap-wrap">
        <table class="calendar-heatmap-table" aria-label="Monthly Study Activity Heatmap">
          <thead>
            <tr>
              <th style="text-align:start;">Year</th>
              ${monthsNames.map(m => `<th>${m}</th>`).join("")}
              <th>Total</th>
            </tr>
          </thead>
          <tbody>
            ${ascYears.map(y => {
              let yearEntries = 0;
              let yearWords = 0;
              const cellsHtml = monthsNames.map((mName, idx) => {
                const mm = String(idx + 1).padStart(2, "0");
                const k = `${y}-${mm}`;
                const data = cellMap.get(k) || { entries: 0, words: 0, titles: [] };
                yearEntries += data.entries;
                yearWords += data.words;
                const val = isWords ? data.words : data.entries;
                const hCls = getHeatClass(val, thresholds);
                const disp = val === 0 ? "·" : isWords ? `${(val / 1000).toFixed(1)}k` : String(val);
                const tip = data.entries > 0
                  ? `${mName} ${y}: ${data.entries} ${data.entries === 1 ? "study" : "studies"} (${data.words.toLocaleString()} words)\n• ${data.titles.join("\n• ")}`
                  : `${mName} ${y}: No studies`;
                return `
                  <td
                    class="cal-cell ${hCls}"
                    ${data.entries > 0 ? `data-filter-month="${k}"` : ""}
                    title="${escapeHtml(tip)}"
                  >${disp}</td>
                `;
              }).join("");

              const rowTot = isWords ? `${(yearWords / 1000).toFixed(1)}k` : String(yearEntries);
              return `
                <tr>
                  <td class="year-label">${y}</td>
                  ${cellsHtml}
                  <td style="text-align:center;font-weight:700;color:var(--text-secondary);padding-left:0.4rem;">${rowTot}</td>
                </tr>
              `;
            }).join("")}
          </tbody>
        </table>
      </div>
    `;
  }

  function renderScriptureCitationHeatmap() {
    let booksToRender = CANONICAL_BOOKS.filter(
      b => state.heatmapWork === "all" || b.work === state.heatmapWork
    );
    if (!state.heatmapShowUncitedBooks) {
      booksToRender = booksToRender.filter(b => bookLookupMap.has(b.book));
    }

    let html = `<div class="scripture-heatmap-list">`;
    let currentWork = "";

    booksToRender.forEach(bMeta => {
      if (state.heatmapWork === "all" && bMeta.work !== currentWork) {
        currentWork = bMeta.work;
        html += `<div class="sc-heat-work-divider"><span>${escapeHtml(currentWork)}</span></div>`;
      }
      const bInfo = bookLookupMap.get(bMeta.book);
      const totalBookStudies = bInfo ? bInfo.entries.size : 0;
      const citedChaptersCount = bInfo ? bInfo.chapters.size : 0;

      const cells = [];
      for (let ch = 1; ch <= bMeta.chapters; ch++) {
        const setIds = bInfo?.chapters.get(ch);
        const cnt = setIds ? setIds.size : 0;
        const hCls = getHeatClass(cnt, [1, 2, 4, 7]);
        let tip = `${bMeta.book} ${ch}: `;
        if (cnt > 0) {
          const sampleTitles = Array.from(setIds)
            .slice(0, 4)
            .map(id => entryById.get(id)?.title || id);
          tip += `${cnt} ${cnt === 1 ? "study" : "studies"}\n• ${sampleTitles.join("\n• ")}`;
        } else {
          tip += "Not yet cited";
        }
        cells.push(`
          <button
            type="button"
            class="sc-heat-cell ${hCls}"
            ${cnt > 0 ? `data-filter-book="${escapeHtml(bMeta.book)}" data-filter-ch="${ch}"` : "disabled"}
            title="${escapeHtml(tip)}"
          >${ch}</button>
        `);
      }

      html += `
        <div class="sc-heat-row">
          <button type="button" class="sc-heat-book-btn" data-filter-book="${escapeHtml(bMeta.book)}" data-filter-ch="" title="Filter by ${escapeHtml(bMeta.book)} (${totalBookStudies} studies)">
            ${escapeHtml(bMeta.book)}
          </button>
          <div class="sc-heat-cells">${cells.join("")}</div>
          <div class="sc-heat-stats" title="${citedChaptersCount} of ${bMeta.chapters} chapters cited across ${totalBookStudies} studies">
            <strong>${totalBookStudies}</strong> st • ${citedChaptersCount}/${bMeta.chapters}
          </div>
        </div>
      `;
    });

    html += `</div>`;
    return html;
  }

  function renderInsightsView() {
    // Standard works citation totals
    const workTotals = WORK_ORDER.map(w => {
      const bMap = workBooksMap.get(w);
      let citations = 0;
      const studySet = new Set();
      if (bMap) {
        bMap.forEach(b => {
          citations += b.citations;
          b.entries.forEach(id => studySet.add(id));
        });
      }
      return { work: w, citations, studies: studySet.size, color: WORK_COLORS[w] || "#3b82f6" };
    });
    const totalWorkCitations = Math.max(1, workTotals.reduce((a, b) => a + b.citations, 0));

    // Top 15 Books by study count
    const topBooks = Array.from(bookLookupMap.values())
      .sort((a, b) => b.entries.size - a.entries.size || b.chapters.size - a.chapters.size)
      .slice(0, 15);
    const maxBookStudies = Math.max(1, topBooks[0]?.entries.size || 1);

    // Top 15 Tags by study count
    const topTags = sortedTags.slice(0, 15);
    const maxTagStudies = Math.max(1, topTags[0]?.count || 1);

    // Word count distribution bins
    const bins = [
      { label: "< 200 words", min: 0, max: 199, count: 0 },
      { label: "200 – 399 words", min: 200, max: 399, count: 0 },
      { label: "400 – 599 words", min: 400, max: 599, count: 0 },
      { label: "600 – 899 words", min: 600, max: 899, count: 0 },
      { label: "900 – 1,299 words", min: 900, max: 1299, count: 0 },
      { label: "1,300 – 1,999 words", min: 1300, max: 1999, count: 0 },
      { label: "2,000+ words", min: 2000, max: Infinity, count: 0 }
    ];
    entries.forEach(e => {
      const b = bins.find(bin => e.word_count >= bin.min && e.word_count <= bin.max);
      if (b) b.count += 1;
    });
    const maxBinCount = Math.max(1, ...bins.map(b => b.count));

    const longestEntries = [...entries]
      .sort((a, b) => b.word_count - a.word_count)
      .slice(0, 8);

    return `
      <div style="margin-bottom:1.5rem;">
        <h2 style="font-family:var(--font-serif);font-size:1.85rem;margin:0 0 0.3rem;">Study Corpus Insights &amp; Data Visualizations</h2>
        <p style="color:var(--text-secondary);margin:0;">Interactive quantitative analysis across all <strong>${entries.length}</strong> gospel studies, <strong>${(stats.total_words || 0).toLocaleString()}</strong> words, <strong>${(stats.total_scriptures || 0).toLocaleString()}</strong> scripture citations, and <strong>${sortedTags.length}</strong> theological topics. Click any bar, chapter cell, or topic to filter studies.</p>
      </div>

      <!-- KPI Statistical Overview Cards -->
      <section class="insights-kpi-grid" aria-label="Corpus Statistical Summary">
        <div class="kpi-card">
          <span class="kpi-label">Total Study Articles</span>
          <span class="kpi-value">${entries.length}</span>
          <span class="kpi-sub">Jun 2019 – Oct 2025 (77 months)</span>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">Total Corpus Volume</span>
          <span class="kpi-value">${(stats.total_words || 0).toLocaleString()}</span>
          <span class="kpi-sub">~${Math.round((stats.total_words || 0) / 300)} book pages written</span>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">Study Length (Mean / Med)</span>
          <span class="kpi-value">${meanWords} <small style="font-size:0.95rem;color:var(--text-muted);font-weight:500;">/ ${medianWords}w</small></span>
          <span class="kpi-sub">90th pct: ${p90Words.toLocaleString()}w • Max: ${(maxWordsEntry?.word_count || 0).toLocaleString()}w</span>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">Scripture Citations</span>
          <span class="kpi-value">${(stats.total_scriptures || 0).toLocaleString()}</span>
          <span class="kpi-sub">${bookLookupMap.size} books • ${totalUniqueChaptersCited} unique chapters</span>
        </div>
        <div class="kpi-card">
          <span class="kpi-label">Theological Vocabulary</span>
          <span class="kpi-value">${sortedTags.length}</span>
          <span class="kpi-sub">Unique #tags (${(entries.reduce((a, e) => a + (e.tags?.length || 0), 0) / entries.length).toFixed(1)} tags/study avg)</span>
        </div>
      </section>

      <!-- Chart 1: Interactive Time-Series Bar Chart -->
      <section class="viz-card">
        <div class="viz-header">
          <div>
            <h3 class="viz-title">📈 Study Cadence &amp; Writing Volume Over Time (2019–2025)</h3>
            <p class="viz-subtitle">Click any bar to filter studies for that time period. Dashed line marks the corpus mean across active periods.</p>
          </div>
          <div class="viz-controls">
            <div class="pill-toggle-group" role="group" aria-label="Select metric">
              <button type="button" class="pill-toggle-btn ${state.tsMetric === "entries" ? "active" : ""}" data-ts-metric="entries">Articles</button>
              <button type="button" class="pill-toggle-btn ${state.tsMetric === "words" ? "active" : ""}" data-ts-metric="words">Total Words</button>
              <button type="button" class="pill-toggle-btn ${state.tsMetric === "avg_words" ? "active" : ""}" data-ts-metric="avg_words">Avg Words/Study</button>
            </div>
            <div class="pill-toggle-group" role="group" aria-label="Select time granularity">
              <button type="button" class="pill-toggle-btn ${state.tsGranularity === "year" ? "active" : ""}" data-ts-gran="year">Yearly</button>
              <button type="button" class="pill-toggle-btn ${state.tsGranularity === "quarter" ? "active" : ""}" data-ts-gran="quarter">Quarterly</button>
              <button type="button" class="pill-toggle-btn ${state.tsGranularity === "month" ? "active" : ""}" data-ts-gran="month">Monthly</button>
            </div>
          </div>
        </div>
        ${renderTimeSeriesSvg()}
      </section>

      <!-- Chart 2: Year x Month Activity Calendar Heatmap -->
      <section class="viz-card">
        <div class="viz-header">
          <div>
            <h3 class="viz-title">🗓️ Monthly Study Activity Heatmap (2019–2025)</h3>
            <p class="viz-subtitle">7-year × 12-month intensity matrix. Hover any cell to preview study titles or click a month to view its entries.</p>
          </div>
          <div class="viz-controls">
            <div class="heatmap-legend" style="margin-right:0.5rem;">
              <span>Less</span>
              <span class="heatmap-legend-swatch heat-0"></span>
              <span class="heatmap-legend-swatch heat-1"></span>
              <span class="heatmap-legend-swatch heat-2"></span>
              <span class="heatmap-legend-swatch heat-3"></span>
              <span class="heatmap-legend-swatch heat-4"></span>
              <span class="heatmap-legend-swatch heat-5"></span>
              <span>More</span>
            </div>
            <div class="pill-toggle-group">
              <button type="button" class="pill-toggle-btn ${state.calMetric === "entries" ? "active" : ""}" data-cal-metric="entries">Study Count</button>
              <button type="button" class="pill-toggle-btn ${state.calMetric === "words" ? "active" : ""}" data-cal-metric="words">Word Volume</button>
            </div>
          </div>
        </div>
        ${renderMonthlyCalendarHeatmap()}
      </section>

      <!-- Chart 3: Canonical Scripture Citation Heatmap (Book x Chapter Matrix) -->
      <section class="viz-card">
        <div class="viz-header">
          <div>
            <h3 class="viz-title">🔥 Canonical Scripture Citation Heatmap (Book × Chapter Matrix)</h3>
            <p class="viz-subtitle">Every square represents a specific canonical chapter (e.g. Alma 1–63, 2 Nephi 1–33, D&amp;C 1–138). Color intensity reflects how many studies cite that chapter. Click any chapter square to open its studies.</p>
          </div>
          <div class="viz-controls">
            <div class="pill-toggle-group">
              <button type="button" class="pill-toggle-btn ${state.heatmapWork === "all" ? "active" : ""}" data-hm-work="all">All Works</button>
              ${WORK_ORDER.map(w => `
                <button type="button" class="pill-toggle-btn ${state.heatmapWork === w ? "active" : ""}" data-hm-work="${escapeHtml(w)}">${escapeHtml(w)}</button>
              `).join("")}
            </div>
            <button type="button" class="icon-btn" id="toggle-uncited-books" style="font-size:0.75rem;padding:0.32rem 0.65rem;">
              ${state.heatmapShowUncitedBooks ? "Showing All 87 Canonical Books" : "Showing 64 Cited Books (Show All 87)"}
            </button>
          </div>
        </div>
        ${renderScriptureCitationHeatmap()}
      </section>

      <!-- Chart 4 & 5: Standard Works / Top Books + Article Depth Distribution -->
      <div class="viz-grid-two">
        <section class="viz-card">
          <div class="viz-header">
            <div>
              <h3 class="viz-title">📚 Standard Works Breakdown &amp; Top 15 Books</h3>
              <p class="viz-subtitle">Share of citations across the 5 Standard Works and most-studied books.</p>
            </div>
          </div>
          <div class="work-proportion-bar" role="img" aria-label="Standard Works citation share">
            ${workTotals.map(wt => {
              const pct = ((wt.citations / totalWorkCitations) * 100).toFixed(1);
              return `
                <div
                  class="work-prop-segment"
                  style="width:${pct}%;background:${wt.color};"
                  data-filter-work="${escapeHtml(wt.work)}"
                  title="${escapeHtml(wt.work)}: ${wt.citations} citations across ${wt.studies} studies (${pct}%)"
                >${Number(pct) >= 9 ? `${pct}%` : ""}</div>
              `;
            }).join("")}
          </div>
          <div class="work-legend-row">
            ${workTotals.map(wt => `
              <span style="display:inline-flex;align-items:center;gap:0.35rem;cursor:pointer;" data-filter-work="${escapeHtml(wt.work)}">
                <span style="width:10px;height:10px;border-radius:50%;background:${wt.color};display:inline-block;"></span>
                <strong>${escapeHtml(wt.work)}</strong> (${wt.studies} studies)
              </span>
            `).join("")}
          </div>

          <div class="horiz-bar-list">
            ${topBooks.map(b => {
              const pct = ((b.entries.size / maxBookStudies) * 100).toFixed(1);
              return `
                <div class="horiz-bar-row" data-filter-book="${escapeHtml(b.book)}" data-filter-ch="">
                  <span class="horiz-bar-label">📖 ${escapeHtml(b.book)}</span>
                  <div class="horiz-bar-track">
                    <div class="horiz-bar-fill" style="width:${pct}%;"></div>
                  </div>
                  <span class="horiz-bar-val"><strong>${b.entries.size}</strong> (${b.chapters.size} ch)</span>
                </div>
              `;
            }).join("")}
          </div>
        </section>

        <section class="viz-card">
          <div class="viz-header">
            <div>
              <h3 class="viz-title">📏 Study Depth Distribution &amp; Longest Essays</h3>
              <p class="viz-subtitle">Word-count histogram across all 294 studies plus the deepest scriptural analyses.</p>
            </div>
          </div>
          <div class="horiz-bar-list" style="margin-bottom:1.5rem;">
            ${bins.map(bin => {
              const pct = ((bin.count / maxBinCount) * 100).toFixed(1);
              const share = Math.round((bin.count / entries.length) * 100);
              return `
                <div class="horiz-bar-row" style="cursor:default;">
                  <span class="horiz-bar-label" style="font-family:var(--font-mono);font-size:0.76rem;">${escapeHtml(bin.label)}</span>
                  <div class="horiz-bar-track">
                    <div class="horiz-bar-fill" style="width:${pct}%;"></div>
                  </div>
                  <span class="horiz-bar-val"><strong>${bin.count}</strong> (${share}%)</span>
                </div>
              `;
            }).join("")}
          </div>

          <div class="sidebar-heading" style="margin-bottom:0.6rem;">
            <span>Top 8 Longest Deep-Dive Studies</span>
          </div>
          <div style="display:flex;flex-direction:column;gap:0.45rem;">
            ${longestEntries.map((e, i) => `
              <div style="display:flex;align-items:center;justify-content:space-between;gap:0.75rem;padding:0.45rem 0.65rem;background:var(--bg-elevated);border-radius:0.45rem;cursor:pointer;" data-entry-id="${escapeHtml(e.id)}">
                <div style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:0.84rem;">
                  <span style="font-family:var(--font-mono);color:var(--text-muted);margin-right:0.4rem;">#${i + 1}</span>
                  <strong>${escapeHtml(e.title)}</strong>
                </div>
                <span class="count-badge" style="flex-shrink:0;">${e.word_count.toLocaleString()} words</span>
              </div>
            `).join("")}
          </div>
        </section>
      </div>

      <!-- Chart 6: Top Theological Tags & Co-Occurrence Network -->
      <div class="viz-grid-two">
        <section class="viz-card">
          <div class="viz-header">
            <div>
              <h3 class="viz-title">🏷️ Top 15 Theological Topics (#Tags)</h3>
              <p class="viz-subtitle">Most frequently explored gospel themes ranked by study count and total words written.</p>
            </div>
          </div>
          <div class="horiz-bar-list">
            ${topTags.map(t => {
              const pct = ((t.count / maxTagStudies) * 100).toFixed(1);
              return `
                <div class="horiz-bar-row" data-filter-tag="${escapeHtml(t.tag)}">
                  <span class="horiz-bar-label">#${escapeHtml(t.tag)}</span>
                  <div class="horiz-bar-track">
                    <div class="horiz-bar-fill" style="width:${pct}%;"></div>
                  </div>
                  <span class="horiz-bar-val"><strong>${t.count}</strong> (${(t.words / 1000).toFixed(1)}k w)</span>
                </div>
              `;
            }).join("")}
          </div>
        </section>

        <section class="viz-card">
          <div class="viz-header">
            <div>
              <h3 class="viz-title">🔗 Concept Co-Occurrence Network (Tag Pairings)</h3>
              <p class="viz-subtitle">Pairs of theological tags that most frequently co-occur in the same study. Click any pair to view studies containing both topics.</p>
            </div>
          </div>
          <div class="cooccur-list">
            ${topTagPairs.map(p => `
              <div class="cooccur-card" data-tag-pair-a="${escapeHtml(p.a)}" data-tag-pair-b="${escapeHtml(p.b)}">
                <div class="cooccur-pair">
                  <span>#${escapeHtml(p.a)} ↔ #${escapeHtml(p.b)}</span>
                </div>
                <div class="cooccur-meta">
                  <strong>${p.count}</strong> shared studies • ${p.jaccard}% Jaccard similarity
                </div>
              </div>
            `).join("")}
          </div>
        </section>
      </div>
    `;
  }

  function renderScripturesView() {
    let html = `
      <div style="margin-bottom:1.5rem;display:flex;align-items:flex-end;justify-content:space-between;flex-wrap:wrap;gap:1rem;">
        <div>
          <h2 style="font-family:var(--font-serif);font-size:1.75rem;margin-bottom:0.35rem;">Scripture Index Explorer</h2>
          <p style="color:var(--text-secondary);margin:0;">Browse all <strong>${(stats.total_scriptures || 0).toLocaleString()}</strong> scripture citations across <strong>${bookLookupMap.size}</strong> books in the Standard Works. Click any book to inspect its chapters or filter studies.</p>
        </div>
        <button type="button" class="icon-btn" data-goto-view="insights">🔥 View Chapter Heatmap in Insights →</button>
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
          <h2 style="font-family:var(--font-serif);font-size:1.6rem;margin:0 0 0.2rem;">Topic &amp; Tag Directory</h2>
          <p style="color:var(--text-secondary);font-size:0.88rem;margin:0;">Explore all <strong>${sortedTags.length}</strong> unique study topics and tags across the collection.</p>
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
        <h2 style="font-family:var(--font-serif);font-size:1.75rem;margin-bottom:0.35rem;">Chronological Study Timeline (2019–2025)</h2>
        <p style="color:var(--text-secondary);margin:0;">All ${entries.length} gospel study entries organized chronologically from 2019 through 2025.</p>
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
                    <strong style="font-size:1.02rem;color:var(--text-primary);">${escapeHtml(e.title)}</strong>
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
      state.readerFont === "serif" ? "var(--font-serif)" : "var(--font-sans)"
    );

    return `
      <div class="reader-container ${hasSubheadings ? "" : "no-toc"}">
        <article class="article-card">
          <div class="reader-topbar">
            <button type="button" class="back-btn" id="reader-back-btn">← Back to Studies</button>
            <div class="reader-controls">
              <button type="button" class="icon-btn" id="toggle-reader-font" title="Switch Sans / Serif reading font">
                Aa ${state.readerFont === "sans" ? "Clean Sans" : "Book Serif"}
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
              <span>${entry.word_count.toLocaleString()} words (${entry.reading_mins} min read)</span>
            </div>
            <h1 class="article-title">${escapeHtml(entry.title)}</h1>

            ${entry.sources_html ? `
              <div class="article-sources-box">
                <strong>Study Sources &amp; Texts:</strong> ${entry.sources_html}
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
    dom.navTabs.forEach(tab => {
      const tabView = tab.getAttribute("data-view");
      tab.classList.toggle("active", tabView === state.view || (state.view === "entry" && tabView === "studies"));
    });

    if (dom.heroSection) {
      dom.heroSection.style.display = state.view === "entry" ? "none" : "block";
    }

    if (state.view === "entry") {
      dom.mainContent.innerHTML = renderArticleReaderView();
    } else if (state.view === "insights") {
      dom.mainContent.innerHTML = renderInsightsView();
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
        state.selectedTag2 = "";
        state.view = "studies";
        navigateToHash(state.selectedTag ? `#tag/${encodeURIComponent(state.selectedTag)}` : "#view/studies");
      });
    });

    // Tag co-occurrence pair clicks
    dom.mainContent.querySelectorAll("[data-tag-pair-a]").forEach(card => {
      card.addEventListener("click", () => {
        state.selectedTag = card.getAttribute("data-tag-pair-a") || "";
        state.selectedTag2 = card.getAttribute("data-tag-pair-b") || "";
        state.view = "studies";
        navigateToHash("#view/studies");
      });
    });

    // Scripture pill / book / heatmap chapter clicks
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

    // Standard Work segment clicks in Insights
    dom.mainContent.querySelectorAll("[data-filter-work]").forEach(el => {
      el.addEventListener("click", () => {
        state.selectedWork = el.getAttribute("data-filter-work") || "";
        state.view = "studies";
        navigateToHash("#view/studies");
      });
    });

    // Time-series bar clicks in Insights
    dom.mainContent.querySelectorAll("[data-ts-filter-type]").forEach(rect => {
      rect.addEventListener("click", () => {
        const fType = rect.getAttribute("data-ts-filter-type");
        const fVal = rect.getAttribute("data-ts-filter-val") || "";
        if (fType === "year") {
          state.selectedYear = fVal;
          state.selectedMonth = "";
        } else if (fType === "month") {
          state.selectedMonth = fVal;
          state.selectedYear = "";
        }
        state.view = "studies";
        navigateToHash("#view/studies");
      });
    });

    // Calendar month cell clicks in Insights
    dom.mainContent.querySelectorAll("[data-filter-month]").forEach(cell => {
      cell.addEventListener("click", () => {
        state.selectedMonth = cell.getAttribute("data-filter-month") || "";
        state.selectedYear = "";
        state.view = "studies";
        navigateToHash("#view/studies");
      });
    });

    // Insights interactive controls
    dom.mainContent.querySelectorAll("[data-ts-metric]").forEach(btn => {
      btn.addEventListener("click", () => {
        state.tsMetric = btn.getAttribute("data-ts-metric");
        render();
      });
    });
    dom.mainContent.querySelectorAll("[data-ts-gran]").forEach(btn => {
      btn.addEventListener("click", () => {
        state.tsGranularity = btn.getAttribute("data-ts-gran");
        render();
      });
    });
    dom.mainContent.querySelectorAll("[data-cal-metric]").forEach(btn => {
      btn.addEventListener("click", () => {
        state.calMetric = btn.getAttribute("data-cal-metric");
        render();
      });
    });
    dom.mainContent.querySelectorAll("[data-hm-work]").forEach(btn => {
      btn.addEventListener("click", () => {
        state.heatmapWork = btn.getAttribute("data-hm-work");
        render();
      });
    });
    const toggleUncitedBtn = document.getElementById("toggle-uncited-books");
    if (toggleUncitedBtn) {
      toggleUncitedBtn.addEventListener("click", () => {
        state.heatmapShowUncitedBooks = !state.heatmapShowUncitedBooks;
        render();
      });
    }

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
    const clearTag2 = document.getElementById("clear-tag2-chip");
    if (clearTag2) {
      clearTag2.addEventListener("click", () => {
        state.selectedTag2 = "";
        render();
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
    const clearMonth = document.getElementById("clear-month-chip");
    if (clearMonth) {
      clearMonth.addEventListener("click", () => {
        state.selectedMonth = "";
        render();
      });
    }
    const resetAll = document.getElementById("reset-all-filters") || document.getElementById("empty-reset-btn");
    if (resetAll) {
      resetAll.addEventListener("click", () => {
        state.query = "";
        state.selectedTag = "";
        state.selectedTag2 = "";
        state.selectedWork = "";
        state.selectedBook = "";
        state.selectedChapter = null;
        state.selectedYear = "";
        state.selectedMonth = "";
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
        state.readerFont = state.readerFont === "sans" ? "serif" : "sans";
        localStorage.setItem("gsj_reader_font_v2", state.readerFont);
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
