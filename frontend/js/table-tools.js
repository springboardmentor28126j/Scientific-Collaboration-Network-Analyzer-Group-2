(() => {
  const DEFAULT_PAGE_SIZE = 10;
  const realRows = body => [...body.querySelectorAll('tr')].filter(row => row.children.length > 1 && !row.querySelector('[colspan]'));
  function enhance(table) {
    if (table.dataset.tableToolsReady) return;
    const body = table.tBodies[0];
    if (!body) return;
    table.dataset.tableToolsReady = 'true';
    const host = document.createElement('div');
    host.className = 'd-flex flex-wrap justify-content-between align-items-center gap-2 mt-3 table-tools';
    host.innerHTML = `<div class="d-flex flex-wrap gap-2"><div class="input-group input-group-sm" style="max-width:280px"><span class="input-group-text"><i class="bi bi-search"></i></span><input class="form-control" placeholder="Search visible records..."></div><button class="btn btn-sm btn-outline-secondary table-reset" type="button"><i class="bi bi-arrow-counterclockwise"></i> Reset</button></div><div class="d-flex flex-wrap align-items-center gap-2"><label class="small text-muted mb-0">Rows <select class="form-select form-select-sm d-inline-block table-size" style="width:auto"><option>10</option><option>25</option><option>50</option><option>100</option></select></label><small class="text-muted table-count"></small><nav class="table-pagination"></nav></div>`;
    table.parentElement.after(host);
    const filter = host.querySelector('input'), reset = host.querySelector('.table-reset'), pageSizeSelect = host.querySelector('.table-size'), count = host.querySelector('.table-count'), pager = host.querySelector('.table-pagination');
    const tableKey = `scnaTablePageSize:${location.pathname}:${[...document.querySelectorAll('table.table')].indexOf(table)}`;
    pageSizeSelect.value = localStorage.getItem(tableKey) || String(DEFAULT_PAGE_SIZE);
    let rows = [], originalRows = [], page = 1, pageSize = Number(pageSizeSelect.value), sortIndex = -1, ascending = true;
    const updateRows = () => { rows = realRows(body); originalRows = [...rows]; page = 1; rows.forEach((row, index) => { row.dataset.tableToolsRow = String(index); }); render(); };
    const filteredRows = () => { const term = filter.value.trim().toLowerCase(); return term ? rows.filter(row => row.innerText.toLowerCase().includes(term)) : rows; };
    const render = () => {
      const visible = filteredRows(); const pages = Math.max(1, Math.ceil(visible.length / pageSize)); page = Math.min(page, pages);
      body.replaceChildren(...visible.slice((page - 1) * pageSize, page * pageSize));
      count.textContent = visible.length ? `Showing ${(page - 1) * pageSize + 1}–${Math.min(page * pageSize, visible.length)} of ${visible.length}` : 'No matching records';
      const candidates = [...new Set([1, page - 1, page, page + 1, pages].filter(number => number >= 1 && number <= pages))];
      pager.innerHTML = pages > 1 ? `<button class="btn btn-sm btn-outline-secondary" data-page="${page - 1}" ${page === 1 ? 'disabled' : ''}>Previous</button>${candidates.map(number => `<button class="btn btn-sm ${page === number ? 'btn-primary' : 'btn-outline-secondary'}" data-page="${number}">${number}</button>`).join('')}<button class="btn btn-sm btn-outline-secondary" data-page="${page + 1}" ${page === pages ? 'disabled' : ''}>Next</button>` : '';
    };
    filter.addEventListener('input', () => { page = 1; render(); });
    reset.addEventListener('click', () => { filter.value = ''; rows = [...originalRows]; page = 1; sortIndex = -1; [...table.tHead?.rows[0]?.cells || []].forEach(header => { if (header.dataset.label) header.innerHTML = `${header.dataset.label} <i class="bi bi-arrow-down-up text-muted small"></i>`; }); render(); });
    pageSizeSelect.addEventListener('change', () => { pageSize = Number(pageSizeSelect.value); localStorage.setItem(tableKey, String(pageSize)); page = 1; render(); });
    pager.addEventListener('click', event => { const target = event.target.closest('[data-page]'); if (!target || target.disabled) return; page = Number(target.dataset.page); render(); });
    [...table.tHead?.rows[0]?.cells || []].forEach((header, index) => { header.dataset.label = header.innerText; header.innerHTML = `${header.dataset.label} <i class="bi bi-arrow-down-up text-muted small"></i>`; header.style.cursor = 'pointer'; header.title = 'Sort by this column'; header.addEventListener('click', () => { ascending = sortIndex === index ? !ascending : true; sortIndex = index; [...table.tHead.rows[0].cells].forEach(item => item.innerHTML = `${item.dataset.label} <i class="bi bi-arrow-down-up text-muted small"></i>`); header.innerHTML = `${header.dataset.label} <i class="bi bi-arrow-${ascending ? 'up' : 'down'} text-primary"></i>`; rows.sort((first, second) => first.cells[index]?.innerText.localeCompare(second.cells[index]?.innerText, undefined, { numeric: true }) * (ascending ? 1 : -1)); render(); }); });
    const observer = new MutationObserver(() => { const current = realRows(body); if (current.some(row => !row.dataset.tableToolsRow)) updateRows(); });
    observer.observe(body, { childList: true });
    updateRows();
  }
  function start() { document.querySelectorAll('table.table').forEach(enhance); new MutationObserver(() => document.querySelectorAll('table.table').forEach(enhance)).observe(document.body, { childList: true, subtree: true }); }
  document.readyState === 'loading' ? document.addEventListener('DOMContentLoaded', start) : start();
})();
