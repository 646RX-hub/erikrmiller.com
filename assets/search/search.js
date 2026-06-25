/* ============================================================
   Cmd+K Search — Erik R. Miller
   - Loads MiniSearch from CDN (~7KB gzipped)
   - Fetches /assets/search/search-index.json once, caches in memory
   - Modal lifecycle: Cmd/Ctrl+K, "/", or trigger click to open
   - GA4 full-funnel: view_search_results, search_no_results,
     search_result_click — all gated on gtag being present
   - Accessibility: role=dialog, focus trap, aria-live result count,
     arrow-key navigation, Esc to close
   - URL handler: /?q=foo on the homepage auto-opens with that query
     (matches the SearchAction JSON-LD target in index.html)
   ============================================================ */
(function () {
  'use strict';

  // ---- Stylesheet guard --------------------------------------------------
  // The search trigger + modal depend on search.css. A few self-contained
  // page templates include search.js without linking that stylesheet, which
  // leaves the trigger as an unstyled <button>: its inline SVG (viewBox, no
  // width/height) balloons to the 300x150 replaced-element default, producing
  // a large white box with the label crammed beneath. Guarantee the stylesheet
  // is present so the component styles itself on every page it loads on.
  (function ensureStylesheet() {
    try {
      var links = document.querySelectorAll('link[rel="stylesheet"]');
      for (var i = 0; i < links.length; i++) {
        if ((links[i].getAttribute('href') || '').indexOf('assets/search/search.css') !== -1) return;
      }
      var link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = '/assets/search/search.css';
      (document.head || document.documentElement).appendChild(link);
    } catch (e) { /* noop */ }
  })();

  // ---- Config -----------------------------------------------------------
  const INDEX_URL = '/assets/search/search-index.json';
  const MINISEARCH_CDN = 'https://cdn.jsdelivr.net/npm/minisearch@7.1.0/dist/umd/index.min.js';
  const DEBOUNCE_MS = 140;
  const RECENT_KEY = 'erm.search.recent';
  const MAX_RECENT = 5;
  const FALLBACK_POPULAR = [
    { url: '/blog/ai-agents-for-marketing-teams/', label: 'AI Agents for Marketing' },
    { url: '/icp/', label: 'ICP Development Guide' },
    { url: '/blog/the-mql-is-dead/', label: 'The MQL Is Dead' },
    { url: '/blog/why-most-abm-programs-fail/', label: 'Why ABM Programs Fail' },
  ];
  const TYPE_LABEL = {
    post: 'Article',
    guide: 'Guide',
    section: 'Section',
    page: 'Page',
  };

  // ---- State ------------------------------------------------------------
  let miniSearch = null;
  let documentsById = new Map();
  let loaded = false;
  let loadPromise = null;
  let modalEl = null;
  let inputEl = null;
  let resultsEl = null;
  let liveEl = null;
  let activeIndex = -1;
  let currentResults = [];
  let lastQueryFired = '';
  let openerEl = null; // for focus return

  // ---- Utilities --------------------------------------------------------
  function debounce(fn, ms) {
    let t;
    return function () {
      clearTimeout(t);
      const args = arguments, self = this;
      t = setTimeout(() => fn.apply(self, args), ms);
    };
  }

  function gaEvent(name, params) {
    // Safe-no-op if gtag isn't on the page.
    if (typeof window.gtag === 'function') {
      try { window.gtag('event', name, params || {}); } catch (e) { /* noop */ }
    }
    // Also push to dataLayer if present (for GTM-style setups).
    if (window.dataLayer && typeof window.dataLayer.push === 'function') {
      try { window.dataLayer.push(Object.assign({ event: name }, params || {})); } catch (e) {}
    }
  }

  function loadScript(src) {
    return new Promise((resolve, reject) => {
      const s = document.createElement('script');
      s.src = src;
      s.async = true;
      s.onload = resolve;
      s.onerror = () => reject(new Error('Failed to load ' + src));
      document.head.appendChild(s);
    });
  }

  function escapeHtml(s) {
    return String(s || '').replace(/[&<>"']/g, (c) => ({
      '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
    }[c]));
  }

  function highlight(text, terms) {
    if (!text) return '';
    const safe = escapeHtml(text);
    if (!terms || !terms.length) return safe;
    const escaped = terms
      .filter(Boolean)
      .map(t => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
      .filter(t => t.length >= 2);
    if (!escaped.length) return safe;
    const re = new RegExp('(' + escaped.join('|') + ')', 'gi');
    return safe.replace(re, '<mark>$1</mark>');
  }

  function snippetFor(doc, terms) {
    const body = doc.body || doc.description || '';
    if (!terms || !terms.length || !body) return body.slice(0, 180) + (body.length > 180 ? '…' : '');
    const lc = body.toLowerCase();
    let hitIdx = -1;
    for (const t of terms) {
      const i = lc.indexOf(t.toLowerCase());
      if (i >= 0 && (hitIdx < 0 || i < hitIdx)) hitIdx = i;
    }
    if (hitIdx < 0) return body.slice(0, 180) + (body.length > 180 ? '…' : '');
    const start = Math.max(0, hitIdx - 60);
    const end = Math.min(body.length, hitIdx + 140);
    return (start > 0 ? '…' : '') + body.slice(start, end) + (end < body.length ? '…' : '');
  }

  // ---- Recent searches --------------------------------------------------
  function getRecent() {
    try {
      const raw = localStorage.getItem(RECENT_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch (e) { return []; }
  }
  function pushRecent(q) {
    q = (q || '').trim();
    if (!q) return;
    try {
      const cur = getRecent().filter(x => x.toLowerCase() !== q.toLowerCase());
      cur.unshift(q);
      localStorage.setItem(RECENT_KEY, JSON.stringify(cur.slice(0, MAX_RECENT)));
    } catch (e) {}
  }

  // ---- Index load -------------------------------------------------------
  async function ensureLoaded() {
    if (loaded) return;
    if (loadPromise) return loadPromise;
    loadPromise = (async () => {
      if (typeof window.MiniSearch === 'undefined') {
        await loadScript(MINISEARCH_CDN);
      }
      const res = await fetch(INDEX_URL, { credentials: 'same-origin' });
      if (!res.ok) throw new Error('Could not load search index');
      const payload = await res.json();
      const docs = payload.documents || [];
      miniSearch = new window.MiniSearch({
        idField: 'id',
        fields: ['title', 'description', 'tags', 'headings', 'body'],
        storeFields: ['id', 'url', 'type', 'title', 'description', 'tags', 'body', 'date'],
        searchOptions: {
          boost: { title: 4, description: 2, tags: 2, headings: 1.5 },
          prefix: true,
          fuzzy: 0.18,
          combineWith: 'AND',
        },
      });
      docs.forEach(d => documentsById.set(d.id, d));
      miniSearch.addAll(docs);
      loaded = true;
    })();
    return loadPromise;
  }

  // ---- Search execution -------------------------------------------------
  function runQuery(q) {
    q = (q || '').trim();
    if (!q || !miniSearch) return [];
    const hits = miniSearch.search(q).slice(0, 12);
    return hits.map(h => {
      const doc = documentsById.get(h.id) || {};
      return Object.assign({}, doc, { _terms: h.terms || [], _score: h.score });
    });
  }

  // ---- Rendering --------------------------------------------------------
  function renderEmpty(q) {
    const recent = getRecent();
    const hasRecent = recent.length > 0;
    const lead = q
      ? `<strong>No results for "${escapeHtml(q)}"</strong>Try a broader term, or pick from below.`
      : (hasRecent
          ? `<strong>What are you looking for?</strong>Or pick up where you left off.`
          : `<strong>Search the library</strong>14 articles, the ICP guide, and the homepage are all fair game.`);
    const items = hasRecent && !q
      ? recent.map(r => `<a href="#" data-recent="${escapeHtml(r)}">${escapeHtml(r)}</a>`).join('')
      : FALLBACK_POPULAR.map(p => `<a href="${escapeHtml(p.url)}" data-suggest="${escapeHtml(p.url)}">${escapeHtml(p.label)}</a>`).join('');
    return `<div class="erm-search-empty">${lead}<div class="suggest">${items}</div></div>`;
  }

  function renderResults(results, terms, q) {
    if (!results.length) return renderEmpty(q);
    // Group by type, preserving order: post, guide, section, page
    const order = ['post', 'guide', 'section', 'page'];
    const groups = {};
    results.forEach(r => {
      (groups[r.type] = groups[r.type] || []).push(r);
    });
    let html = '';
    let runningIndex = 0;
    order.forEach(t => {
      const items = groups[t];
      if (!items || !items.length) return;
      html += `<div class="erm-search-group-label">${t === 'post' ? 'Articles' : (t === 'guide' ? 'Guides' : (t === 'section' ? 'On this site' : 'Pages'))}</div>`;
      items.forEach(doc => {
        const idx = runningIndex++;
        const title = highlight(doc.title, terms);
        const snippet = doc.type === 'section'
          ? highlight(doc.description || '', terms)
          : highlight(snippetFor(doc, terms), terms);
        const tags = doc.tags ? `<span>${escapeHtml(doc.tags)}</span>` : '';
        html += `<a class="erm-search-result" href="${escapeHtml(doc.url)}" data-idx="${idx}" data-url="${escapeHtml(doc.url)}">
          <div class="erm-search-result-meta"><span class="type-badge">${TYPE_LABEL[doc.type] || 'Result'}</span>${tags ? '· ' + tags : ''}</div>
          <div class="erm-search-result-title">${title}</div>
          ${snippet ? `<div class="erm-search-result-snippet">${snippet}</div>` : ''}
        </a>`;
      });
    });
    return html;
  }

  function updateActive(delta) {
    if (!currentResults.length) return;
    const items = resultsEl.querySelectorAll('.erm-search-result');
    if (!items.length) return;
    activeIndex = (activeIndex + delta + items.length) % items.length;
    items.forEach((el, i) => el.setAttribute('data-active', i === activeIndex ? 'true' : 'false'));
    const active = items[activeIndex];
    if (active) active.scrollIntoView({ block: 'nearest' });
  }

  // ---- Search lifecycle -------------------------------------------------
  const fireResultsEvent = debounce(function (q, count) {
    if (!q || q === lastQueryFired) return;
    lastQueryFired = q;
    pushRecent(q);
    if (count === 0) {
      gaEvent('search_no_results', { search_term: q });
    } else {
      gaEvent('view_search_results', { search_term: q, results_count: count });
    }
  }, 600);

  function doSearch(q) {
    if (!loaded) {
      resultsEl.innerHTML = `<div class="erm-search-empty"><strong>Loading…</strong>One moment while we fetch the library.</div>`;
      return;
    }
    activeIndex = -1;
    currentResults = runQuery(q);
    const terms = currentResults[0]?._terms || (q ? q.split(/\s+/) : []);
    resultsEl.innerHTML = renderResults(currentResults, terms, q);
    liveEl.textContent = q
      ? (currentResults.length
          ? `${currentResults.length} result${currentResults.length === 1 ? '' : 's'} for ${q}`
          : `No results for ${q}`)
      : '';
    if (q) fireResultsEvent(q, currentResults.length);
  }

  const debouncedSearch = debounce(doSearch, DEBOUNCE_MS);

  // ---- Modal mount + open/close ----------------------------------------
  function ensureModal() {
    if (modalEl) return;
    modalEl = document.createElement('div');
    modalEl.className = 'erm-search-backdrop';
    modalEl.setAttribute('role', 'presentation');
    modalEl.innerHTML = `
      <div class="erm-search-dialog" role="dialog" aria-modal="true" aria-label="Search">
        <div class="erm-search-input-row">
          <svg class="icon" viewBox="0 0 24 24" fill="none" stroke-width="1.8" aria-hidden="true">
            <circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>
          </svg>
          <input type="search" class="erm-search-input"
                 placeholder="Search articles, frameworks, sections…"
                 autocomplete="off" autocorrect="off" spellcheck="false"
                 aria-label="Search the site"
                 aria-controls="erm-search-results"
                 aria-autocomplete="list" />
          <button type="button" class="erm-search-close" aria-label="Close search">Esc</button>
        </div>
        <div class="erm-search-results" id="erm-search-results" role="listbox" aria-label="Search results"></div>
        <div class="erm-search-footer">
          <span><kbd>↑</kbd><kbd>↓</kbd> Navigate · <kbd>↵</kbd> Open · <kbd>Esc</kbd> Close</span>
          <span>Search powered by MiniSearch</span>
        </div>
        <div class="sr-only" aria-live="polite" aria-atomic="true" style="position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden;"></div>
      </div>`;
    document.body.appendChild(modalEl);
    inputEl = modalEl.querySelector('.erm-search-input');
    resultsEl = modalEl.querySelector('.erm-search-results');
    liveEl = modalEl.querySelector('[aria-live="polite"]');

    // Backdrop click closes (only when clicking the backdrop itself).
    modalEl.addEventListener('click', (e) => {
      if (e.target === modalEl) closeModal();
    });
    modalEl.querySelector('.erm-search-close').addEventListener('click', closeModal);

    inputEl.addEventListener('input', (e) => debouncedSearch(e.target.value));
    inputEl.addEventListener('keydown', onInputKey);

    // Recent / suggest click handlers (delegated)
    resultsEl.addEventListener('click', (e) => {
      const recent = e.target.closest('[data-recent]');
      if (recent) {
        e.preventDefault();
        inputEl.value = recent.getAttribute('data-recent');
        inputEl.focus();
        doSearch(inputEl.value);
        return;
      }
      const result = e.target.closest('.erm-search-result');
      if (result) {
        const url = result.getAttribute('data-url');
        const idx = parseInt(result.getAttribute('data-idx') || '0', 10);
        gaEvent('search_result_click', {
          search_term: inputEl.value.trim(),
          result_url: url,
          result_position: idx + 1,
        });
        // Let navigation proceed naturally.
      }
    });
  }

  function onInputKey(e) {
    if (e.key === 'ArrowDown') { e.preventDefault(); updateActive(1); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); updateActive(-1); }
    else if (e.key === 'Enter') {
      const items = resultsEl.querySelectorAll('.erm-search-result');
      const target = activeIndex >= 0 ? items[activeIndex] : items[0];
      if (target) {
        e.preventDefault();
        const url = target.getAttribute('data-url');
        gaEvent('search_result_click', {
          search_term: inputEl.value.trim(),
          result_url: url,
          result_position: (activeIndex >= 0 ? activeIndex : 0) + 1,
        });
        window.location.href = url;
      }
    } else if (e.key === 'Escape') {
      closeModal();
    }
  }

  function openModal(prefill, opener) {
    openerEl = opener || document.activeElement;
    ensureModal();
    document.documentElement.classList.add('erm-search-open');
    document.body.classList.add('erm-search-open');
    modalEl.setAttribute('data-open', 'true');
    if (prefill != null) inputEl.value = prefill;
    // Show initial state (recent / popular) immediately
    activeIndex = -1;
    currentResults = [];
    resultsEl.innerHTML = renderEmpty(inputEl.value || '');
    setTimeout(() => inputEl.focus(), 20);

    // Lazy-load index on first open
    ensureLoaded().then(() => {
      if (inputEl.value) doSearch(inputEl.value);
    }).catch((err) => {
      console.error('[erm-search]', err);
      resultsEl.innerHTML = `<div class="erm-search-empty"><strong>Search is offline.</strong>Couldn't load the index. Try again, or <a href="/blog/" style="color:var(--erm-search-gold);">browse the blog</a>.</div>`;
    });

    if (inputEl.value) doSearch(inputEl.value);
  }

  function closeModal() {
    if (!modalEl) return;
    modalEl.setAttribute('data-open', 'false');
    document.documentElement.classList.remove('erm-search-open');
    document.body.classList.remove('erm-search-open');
    if (openerEl && typeof openerEl.focus === 'function') openerEl.focus();
    lastQueryFired = '';
  }

  // ---- Global keyboard shortcuts ---------------------------------------
  function isEditable(el) {
    if (!el) return false;
    const tag = el.tagName;
    return tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || el.isContentEditable;
  }

  function onGlobalKey(e) {
    // Cmd/Ctrl + K
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      openModal();
      return;
    }
    // "/" only when not typing in another field, and modal is closed
    if (e.key === '/' && !isEditable(e.target) && !(modalEl && modalEl.getAttribute('data-open') === 'true')) {
      e.preventDefault();
      openModal();
    }
  }

  // ---- Init: bind trigger button(s) + handle ?q= -----------------------
  function init() {
    document.addEventListener('keydown', onGlobalKey);
    document.querySelectorAll('[data-erm-search-trigger]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        openModal('', btn);
      });
    });

    // Sitelinks Searchbox / shareable search URL support: ?q=foo
    try {
      const params = new URLSearchParams(window.location.search);
      const q = params.get('q');
      if (q && q.trim()) {
        openModal(q.trim());
      }
    } catch (e) { /* noop */ }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Expose minimal API in case the user wants to trigger from elsewhere
  window.ermSearch = { open: openModal, close: closeModal };
})();
