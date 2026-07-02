// v0.4.3 — UI polish: dedup stats/filters, pagination, card density, TOC, reading layout.
// Data-driven: every count, every card, every label comes from data/catalog.json.

const GITHUB_REPO = 'https://github.com/conanxin/hermes-knowledge-base/tree/main/';

let allRecords = [];
let currentFilter = 'all';

const IS_HOME_PAGE = !!(
  document.getElementById('search') &&
  document.getElementById('records') &&
  document.getElementById('stats') &&
  document.getElementById('filters')
);

// Canonical type order — keeps the stats / filters in a predictable visual sequence.
const KNOWN_TYPES = ['article', 'note', 'project', 'resource_collection', 'essay', 'interview', 'academic_paper', 'video'];

const TYPE_LABELS_ZH = {
  article: '文章',
  note: '笔记',
  project: '项目',
  resource_collection: '合集',
  essay: '随笔',
  interview: '访谈',
  academic_paper: '论文',
  video: '视频',
};

// ---- Pagination state ----
let currentPage = 1;
const PAGE_SIZES = [12, 24, 48, 9999];
let currentPageSize = PAGE_SIZES[0]; // default 12

async function loadData() {
  if (!IS_HOME_PAGE) return;
  const res = await fetch('data/catalog.json');
  allRecords = await res.json();
  // Sort by updated_date desc, then published_date desc, then title for stability.
  allRecords.sort((a, b) => {
    const da = a.updated_date || '';
    const db = b.updated_date || '';
    if (db !== da) return db.localeCompare(da);
    const pa = a.published_date || '';
    const pb = b.published_date || '';
    if (pb !== pa) return pb.localeCompare(pa);
    return (a.title || '').localeCompare(b.title || '');
  });
  renderStats();
  renderFilters();
  renderRecords();
  bindGlobalControls();
}

function summarizeType(type) {
  return TYPE_LABELS_ZH[type] || type;
}

// ---- v0.4.3 Stage C: Stats as pure overview (non-interactive) ----
function renderStats() {
  const counts = { total: allRecords.length };
  for (const t of KNOWN_TYPES) {
    counts[t] = allRecords.filter(r => r.type === t).length;
  }
  const known = new Set(KNOWN_TYPES);
  const unknowns = [...new Set(allRecords.map(r => r.type).filter(t => !known.has(t)))];
  if (unknowns.length) {
    console.warn('[ui] unknown types in catalog:', unknowns);
    for (const t of unknowns) counts[t] = allRecords.filter(r => r.type === t).length;
  }

  const top = [
    { key: 'total', label: '总记录', accent: 'total' },
    { key: 'article', label: '文章', accent: 'article' },
    { key: 'note', label: '笔记', accent: 'note' },
    { key: 'project', label: '项目', accent: 'project' },
    { key: 'resource_collection', label: '合集', accent: 'collection' },
  ];

  const container = document.getElementById('stats');
  container.innerHTML = `
    <div class="stats-label">知识库概览</div>
    <div class="stat-card-grid">
      ${top.map(c => `
        <div class="stat-card stat-${c.accent}" aria-label="${c.label}: ${counts[c.key]}">
          <span class="stat-number">${counts[c.key]}</span>
          <span class="stat-label">${c.label}</span>
        </div>
      `).join('')}
    </div>
  `;

  const footer = document.getElementById('footer-line');
  if (footer) {
    footer.textContent = `hermes-knowledge-base · 共 ${counts.total} 条记录`;
  }
}

function renderFilters() {
  const counts = { all: allRecords.length };
  for (const t of KNOWN_TYPES) {
    counts[t] = allRecords.filter(r => r.type === t).length;
  }
  const known = new Set(KNOWN_TYPES);
  const unknowns = [...new Set(allRecords.map(r => r.type).filter(t => !known.has(t)))];
  for (const t of unknowns) counts[t] = allRecords.filter(r => r.type === t).length;

  const order = ['all', ...KNOWN_TYPES.filter(t => counts[t] > 0), ...unknowns.filter(t => counts[t] > 0)];
  const container = document.getElementById('filters');
  container.innerHTML = order.map(t => {
    const label = t === 'all' ? '全部' : summarizeType(t);
    const active = t === currentFilter ? 'active' : '';
    return `<button type="button" class="filter-btn ${active}" data-type="${t}">${label} <span class="filter-count">${counts[t]}</span></button>`;
  }).join('');

  container.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      currentFilter = btn.dataset.type;
      currentPage = 1; // reset to first page on filter change
      renderFilters();
      renderRecords();
    });
  });
}

function getSearchableText(r) {
  return [
    r.title || '',
    r.title_zh || '',
    r.summary || '',
    r.summary_zh || '',
    r.author || '',
    r.author_zh || '',
    r.source_site || '',
    ...(r.tags || []),
    ...(r.topics || []),
  ].join(' ').toLowerCase();
}

async function copyPath(path, btn) {
  if (!path) return;
  try {
    await navigator.clipboard.writeText(path);
  } catch (e) {
    const ta = document.createElement('textarea');
    ta.value = path;
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); } catch (_) {}
    document.body.removeChild(ta);
  }
  if (!btn) return;
  const original = btn.dataset.label || btn.textContent;
  btn.dataset.label = original;
  btn.textContent = '已复制 ✓';
  btn.classList.add('copied');
  clearTimeout(btn._t);
  btn._t = setTimeout(() => {
    btn.textContent = original;
    btn.classList.remove('copied');
  }, 1400);
}

function tagList(r, max = 6) {
  const tags = r.tags || [];
  if (tags.length <= max) {
    return tags.map(t => `<span class="chip">${escapeHtml(t)}</span>`).join('');
  }
  const shown = tags.slice(0, max).map(t => `<span class="chip">${escapeHtml(t)}</span>`).join('');
  const rest = tags.length - max;
  return `${shown}<span class="chip chip-more" title="${escapeHtml(tags.slice(max).join(' · '))}">+${rest}</span>`;
}

function metaLine(r) {
  const parts = [];
  if (r.author || r.author_zh) parts.push(escapeHtml(r.author_zh || r.author));
  if (r.source_site) parts.push(escapeHtml(r.source_site));
  const date = r.published_date || r.captured_date || r.updated_date || '';
  if (date) parts.push(escapeHtml(date));
  return parts.join(' · ');
}

function pageSizeLabel(size) {
  return size >= 9999 ? '全部' : String(size);
}

function renderRecords() {
  const queryEl = document.getElementById('search');
  const query = (queryEl ? queryEl.value : '').trim().toLowerCase();
  const clearBtn = document.getElementById('clear-search');
  if (clearBtn) clearBtn.hidden = query.length === 0;

  let filtered = allRecords;
  if (currentFilter !== 'all') {
    filtered = filtered.filter(r => r.type === currentFilter);
  }
  if (query) {
    filtered = filtered.filter(r => getSearchableText(r).includes(query));
  }

  const total = filtered.length;
  const pageSize = currentPageSize >= 9999 ? total : currentPageSize;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  if (currentPage > totalPages) currentPage = totalPages;

  // Result meta: shows range
  const resultMeta = document.getElementById('result-meta');
  if (resultMeta) {
    if (total === 0) {
      resultMeta.textContent = '无匹配结果';
    } else if (total <= pageSize && pageSize < 9999) {
      resultMeta.textContent = `显示 ${total} / ${allRecords.length} 条${currentFilter !== 'all' ? ' · ' + summarizeType(currentFilter) : ''}`;
    } else {
      const start = (currentPage - 1) * pageSize + 1;
      const end = Math.min(currentPage * pageSize, total);
      resultMeta.textContent = `显示 ${start}–${end} / ${total} 条${currentFilter !== 'all' ? ' · ' + summarizeType(currentFilter) : ''}`;
    }
  }

  const container = document.getElementById('records');

  // Empty state
  if (filtered.length === 0) {
    const emptyMsg = query
      ? `没有匹配 "${escapeHtml(query)}" 的条目，试试减少关键词或切换类型。`
      : '当前筛选下没有条目。';
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">∅</div>
        <div class="empty-text">${emptyMsg}</div>
        <button type="button" class="action-btn" id="empty-reset">清除筛选</button>
      </div>
    `;
    const reset = document.getElementById('empty-reset');
    if (reset) reset.addEventListener('click', resetFilters);
    return;
  }

  // Slice to current page
  const start = (currentPage - 1) * pageSize;
  const pageRecords = filtered.slice(start, start + pageSize);

  // Render cards
  container.innerHTML = pageRecords.map(r => {
    const githubLink = r.github_url || (GITHUB_REPO + r.path);
    const detailLink = r.detail_url || '';
    const titleHref = detailLink || githubLink;
    const titleTarget = detailLink ? '' : 'target="_blank" rel="noopener"';
    const summary = r.summary_zh || r.summary || '';
    const summaryHtml = summary
      ? `<p class="record-summary">${escapeHtml(summary.slice(0, 160))}${summary.length > 160 ? '…' : ''}</p>`
      : '';
    return `
      <article class="record-card">
        <div class="record-header">
          <span class="type-badge type-${escapeAttr(r.type)}">${escapeHtml(summarizeType(r.type))}</span>
          <a class="record-title" href="${titleHref}" ${titleTarget}>${escapeHtml(r.title_zh || r.title || '无标题')}</a>
        </div>
        ${(r.title && r.title_zh && r.title_zh !== r.title) ? `<p class="record-title-en">${escapeHtml(r.title)}</p>` : ''}
        <p class="record-info">${metaLine(r)}</p>
        ${summaryHtml}
        <div class="record-meta">${tagList(r, 6)}</div>
        <div class="record-actions">
          ${detailLink ? `<a class="action-link primary" href="${detailLink}">阅读 →</a>` : ''}
          <a class="action-link" href="${githubLink}" target="_blank" rel="noopener">GitHub</a>
          ${r.source_url ? `<a class="action-link" href="${escapeAttr(r.source_url)}" target="_blank" rel="noopener">原始来源</a>` : ''}
          <button type="button" class="action-btn" data-path="${escapeAttr(r.path || '')}">复制路径</button>
        </div>
      </article>
    `;
  }).join('');

  // Pagination controls (only show when total > pageSize or All was selected and there are many)
  const needsPagination = total > pageSize || currentPageSize >= 9999;
  if (needsPagination && total > 0) {
    container.innerHTML += renderPaginationHTML(currentPage, totalPages, total, pageSize, pageRecords.length);
    attachPaginationHandlers();
  }

  container.querySelectorAll('.action-btn[data-path]').forEach(btn => {
    btn.addEventListener('click', () => copyPath(btn.dataset.path, btn));
  });
}

function renderPaginationHTML(page, totalPages, total, pageSize, pageCount) {
  if (totalPages <= 1 && pageSize >= 9999) return ''; // All and fits in one page

  const pages = [];
  const delta = 2;
  for (let i = 1; i <= totalPages; i++) {
    if (i === 1 || i === totalPages || (i >= page - delta && i <= page + delta)) {
      pages.push(i);
    } else if (pages[pages.length - 1] !== '…') {
      pages.push('…');
    }
  }

  const sizeOptions = PAGE_SIZES.map(s => {
    const label = pageSizeLabel(s);
    const sel = s === currentPageSize ? 'selected' : '';
    return `<option value="${s}" ${sel}>${label}</option>`;
  }).join('');

  return `
    <nav class="pagination" aria-label="分页导航">
      <div class="pagination-controls">
        <button type="button" class="page-btn" data-page="${page - 1}" ${page <= 1 ? 'disabled' : ''} aria-label="上一页">
          ← 上一页
        </button>
        <div class="page-numbers">
          ${pages.map(p => p === '…'
            ? '<span class="page-ellipsis">…</span>'
            : `<button type="button" class="page-num ${p === page ? 'active' : ''}" data-page="${p}" aria-label="第 ${p} 页" aria-current="${p === page ? 'page' : ''}">${p}</button>`
          ).join('')}
        </div>
        <button type="button" class="page-btn" data-page="${page + 1}" ${page >= totalPages ? 'disabled' : ''} aria-label="下一页">
          下一页 →
        </button>
      </div>
      <div class="pagination-meta">
        <label class="page-size-label" for="page-size-select">每页显示</label>
        <select id="page-size-select" class="page-size-select" aria-label="每页显示数量">
          ${sizeOptions}
        </select>
        <span class="page-size-note">${page} / ${totalPages} 页 · 共 ${total} 条</span>
      </div>
    </nav>
  `;
}

function attachPaginationHandlers() {
  document.querySelectorAll('.page-num, .page-btn[data-page]').forEach(btn => {
    btn.addEventListener('click', () => {
      const p = parseInt(btn.dataset.page, 10);
      if (isNaN(p) || p < 1) return;
      currentPage = p;
      renderRecords();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  });

  const sel = document.getElementById('page-size-select');
  if (sel) {
    sel.addEventListener('change', () => {
      currentPageSize = parseInt(sel.value, 10);
      currentPage = 1;
      renderRecords();
    });
  }
}

function bindGlobalControls() {
  const search = document.getElementById('search');
  if (!search) return;
  let debounceId;
  const onInput = () => {
    clearTimeout(debounceId);
    debounceId = setTimeout(() => {
      currentPage = 1; // reset to first page on search
      renderRecords();
    }, 80);
  };
  search.addEventListener('input', onInput);

  const clear = document.getElementById('clear-search');
  if (clear) {
    clear.addEventListener('click', () => {
      search.value = '';
      clear.hidden = true;
      currentPage = 1;
      renderRecords();
      search.focus();
    });
  }
}

function resetFilters() {
  currentFilter = 'all';
  currentPage = 1;
  const search = document.getElementById('search');
  if (search) search.value = '';
  const clear = document.getElementById('clear-search');
  if (clear) clear.hidden = true;
  renderFilters();
  renderRecords();
}

// Minimal HTML escaping for user-supplied content rendered into innerHTML.
function escapeHtml(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
function escapeAttr(s) {
  return escapeHtml(s).replace(/`/g, '&#96;');
}

// ============================================================
// Music Track Players (v0.3.19 music-track-links)
// ============================================================
function initTrackPlayers() {
  const buttons = document.querySelectorAll('.track-play-button');
  buttons.forEach((btn) => {
    if (btn.dataset.replaced === '1') return;
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const url = btn.getAttribute('data-embed-url');
      if (!url) return;
      const wrapper = btn.closest('.track-actions');
      if (!wrapper) return;
      const iframe = document.createElement('iframe');
      iframe.src = url;
      iframe.className = 'track-embed';
      iframe.setAttribute('allow', 'autoplay; encrypted-media; picture-in-picture');
      iframe.setAttribute('allowfullscreen', '');
      iframe.setAttribute('loading', 'lazy');
      iframe.setAttribute('title', btn.getAttribute('data-track-title') || 'track player');
      wrapper.innerHTML = '';
      wrapper.appendChild(iframe);
      btn.dataset.replaced = '1';
    });
  });
}

// ============================================================
// v0.3.28: Playable track filter
// ============================================================
function initTrackFilter() {
  const bar = document.getElementById('track-filter-bar');
  if (!bar) return;
  const buttons = bar.querySelectorAll('.track-filter-button');
  if (!buttons.length) return;
  const scope = bar.closest('.detail-article') || document;
  const cards = scope.querySelectorAll('.track-card');

  function applyFilter(filter) {
    cards.forEach((card) => {
      const status = card.getAttribute('data-track-status');
      let visible = true;
      if (filter === 'playable') {
        visible = status === 'verified';
      } else if (filter === 'pending') {
        visible = status !== 'verified';
      }
      card.classList.toggle('is-hidden', !visible);
    });
  }

  buttons.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const filter = btn.getAttribute('data-filter') || 'all';
      buttons.forEach((b) => {
        const isActive = b === btn;
        b.classList.toggle('active', isActive);
        b.setAttribute('aria-pressed', isActive ? 'true' : 'false');
      });
      applyFilter(filter);
    });
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    initTrackPlayers();
    initTrackFilter();
  });
} else {
  initTrackPlayers();
  initTrackFilter();
}

loadData();