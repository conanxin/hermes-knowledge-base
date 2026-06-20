const GITHUB_REPO = 'https://github.com/conanxin/hermes-knowledge-base/tree/main/';

let allRecords = [];
let currentFilter = 'all';

async function loadData() {
  const res = await fetch('data/catalog.json');
  allRecords = await res.json();
  // Sort by updated_date descending
  allRecords.sort((a, b) => {
    const da = a.updated_date || '';
    const db = b.updated_date || '';
    return db.localeCompare(da);
  });
  renderStats();
  renderFilters();
  renderRecords();
}

function renderStats() {
  const stats = {
    total: allRecords.length,
    article: allRecords.filter(r => r.type === 'article').length,
    note: allRecords.filter(r => r.type === 'note').length,
    project: allRecords.filter(r => r.type === 'project').length,
    resource_collection: allRecords.filter(r => r.type === 'resource_collection').length,
  };

  const container = document.getElementById('stats');
  container.innerHTML = `
    <div class="stat-card"><div class="number">${stats.total}</div><div class="label">总记录</div></div>
    <div class="stat-card"><div class="number">${stats.article}</div><div class="label">article</div></div>
    <div class="stat-card"><div class="number">${stats.note}</div><div class="label">note</div></div>
    <div class="stat-card"><div class="number">${stats.project}</div><div class="label">project</div></div>
    <div class="stat-card"><div class="number">${stats.resource_collection}</div><div class="label">collection</div></div>
  `;
}

function renderFilters() {
  const counts = {
    all: allRecords.length,
    article: allRecords.filter(r => r.type === 'article').length,
    note: allRecords.filter(r => r.type === 'note').length,
    project: allRecords.filter(r => r.type === 'project').length,
    resource_collection: allRecords.filter(r => r.type === 'resource_collection').length,
  };
  const types = ['all', 'article', 'note', 'project', 'resource_collection'];
  const labels = { all: '全部', article: 'article', note: 'note', project: 'project', resource_collection: 'collection' };
  const container = document.getElementById('filters');
  container.innerHTML = types.map(t =>
    `<button class="filter-btn ${t === currentFilter ? 'active' : ''}" data-type="${t}">${labels[t]} (${counts[t]})</button>`
  ).join('');

  container.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      currentFilter = btn.dataset.type;
      renderFilters();
      renderRecords();
    });
  });
}

function getSearchableText(r) {
  return [
    r.title || '',
    r.title_zh || '',
    ...(r.tags || []),
    ...(r.topics || []),
  ].join(' ').toLowerCase();
}

function copyPath(path) {
  navigator.clipboard.writeText(path).catch(() => {});
}

function renderRecords() {
  const query = document.getElementById('search').value.trim().toLowerCase();
  const container = document.getElementById('records');

  let filtered = allRecords;

  if (currentFilter !== 'all') {
    filtered = filtered.filter(r => r.type === currentFilter);
  }

  if (query) {
    filtered = filtered.filter(r => getSearchableText(r).includes(query));
  }

  if (filtered.length === 0) {
    container.innerHTML = '<div class="empty-state">未找到匹配记录，请尝试其他关键词</div>';
    return;
  }

  container.innerHTML = filtered.map(r => {
    const githubLink = GITHUB_REPO + r.path;
    const date = r.updated_date || '';
    const author = r.author || '';
    const tags = (r.tags || []).slice(0, 10).map(t => `<span class="chip">${t}</span>`).join('');
    return `
      <div class="record-card">
        <div class="record-header">
          <span class="type-badge ${r.type}">${r.type}</span>
          <a class="record-title" href="${githubLink}" target="_blank" rel="noopener">${r.title_zh || r.title}</a>
        </div>
        <div class="record-title-en">${r.title || ''}</div>
        <div class="record-info">
          ${author ? `<span class="info-item">${author}</span>` : ''}
          ${date ? `<span class="info-item">${date}</span>` : ''}
        </div>
        <div class="record-meta">${tags}</div>
        <div class="record-actions">
          <a class="action-link" href="${githubLink}" target="_blank" rel="noopener">在 GitHub 中打开</a>
          <button class="action-btn" onclick="copyPath('${r.path}')">复制 path</button>
        </div>
      </div>
    `;
  }).join('');
}

document.getElementById('search').addEventListener('input', renderRecords);

loadData();
