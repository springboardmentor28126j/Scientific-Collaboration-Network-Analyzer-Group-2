const API_BASE = 'http://127.0.0.1:8000';
const pageRole = document.body.dataset.role;
const config = {
  researcher: { title: 'Researcher Dashboard', subtitle: 'Track your scholarly activity, opportunities, and collaboration network.', icon: 'bi-person-workspace', actions: [['bi-journal-text','Manage publications','publications.html'],['bi-people-fill','View collaboration network','network.html'],['bi-calendar-event','Browse conferences','conferences.html'],['bi-file-earmark-bar-graph','Open research reports','report.html']] },
  institution: { title: 'Institution Dashboard', subtitle: 'Monitor institutional research output, people, and collaboration activity.', icon: 'bi-building', actions: [['bi-people','Manage researchers','researchers.html'],['bi-journal-text','Review publications','publications.html'],['bi-clipboard-check','Assign reviews','reviews.html'],['bi-file-earmark-bar-graph','Generate institution report','report.html']] },
  publisher: { title: 'Publisher Dashboard', subtitle: 'Follow publication pipeline activity, review assignments, and citation records.', icon: 'bi-journal-check', actions: [['bi-journal-plus','Publication repository','publications.html'],['bi-clipboard-check','Assign reviewers','reviews.html'],['bi-quote','Citation records','citations.html'],['bi-file-earmark-bar-graph','Publication analytics','report.html']] },
  reviewer: { title: 'Reviewer Dashboard', subtitle: 'Complete assigned reviews, record decisions, and check citation context.', icon: 'bi-clipboard-check', actions: [['bi-clipboard-check','Open review queue','reviews.html'],['bi-journal-text','View assigned publications','publications.html'],['bi-quote','Check citations','citations.html'],['bi-file-earmark-bar-graph','Open analytics','report.html']] }
}[pageRole];

const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const stat = (icon, label, value, href, color = 'primary') => `<div class="col-md-6 col-xl-3"><a class="card role-stat p-3 text-decoration-none h-100" href="${href}"><div class="d-flex justify-content-between"><div class="icon"><i class="bi ${icon}"></i></div><span class="badge text-bg-${color} align-self-start">Open</span></div><h2>${value}</h2><p class="text-muted mb-0">${label}</p></a></div>`;
const safeJson = async url => { const response = await fetch(url); if (!response.ok) return []; return response.json(); };

function renderWorkspace({ user, researchers, institutions, publications, collaborations, reviews }) {
  const panel = document.createElement('section');
  panel.className = 'custom-card p-4 mt-4';
  const researcher = user.workspace?.researcher ? researchers.find(item => item.id === user.workspace.researcher.id) : null;
  const institution = user.workspace?.institution ? institutions.find(item => item.id === user.workspace.institution.id) : null;
  const pendingCollabs = collaborations.filter(item => item.status === 'pending').length;
  if (pageRole === 'researcher') {
    const mine = researcher ? publications.filter(item => (item.authors || []).some(author => author.id === researcher.id)) : [];
    const drafts = mine.filter(item => item.status === 'draft').length;
    panel.innerHTML = `<div class="d-flex justify-content-between align-items-center mb-3"><div><h2 class="h5 mb-1">My pending actions</h2><p class="text-muted mb-0">Work that needs your attention.</p></div><a class="btn btn-outline-primary btn-sm" href="profile.html">View profile</a></div>${researcher ? `<div class="row g-3"><div class="col-md-4"><a class="text-decoration-none text-dark" href="publications.html"><strong>${drafts}</strong><small class="d-block text-muted">Draft publications to complete</small></a></div><div class="col-md-4"><a class="text-decoration-none text-dark" href="collaborations.html"><strong>${pendingCollabs}</strong><small class="d-block text-muted">Collaboration requests to review</small></a></div><div class="col-md-4"><strong>${escapeHtml(researcher.full_name)}</strong><small class="d-block text-muted">${escapeHtml(researcher.department || 'Researcher profile')}</small></div></div>` : '<div class="alert alert-info mb-0">Your account has not been assigned to a researcher profile yet. Ask a System Admin to assign your workspace.</div>'}`;
  } else if (pageRole === 'institution') {
    const institutionPubs = institution ? publications.filter(item => item.institution_id === institution.id) : [];
    const submitted = institutionPubs.filter(item => item.status === 'submitted').length;
    const pendingReviews = reviews.filter(item => item.status === 'pending').length;
    panel.innerHTML = `<div class="d-flex justify-content-between align-items-center mb-3"><div><h2 class="h5 mb-1">Institution action centre</h2><p class="text-muted mb-0">Assigned institution activity requiring attention.</p></div><a class="btn btn-outline-primary btn-sm" href="report.html">Open reports</a></div>${institution ? `<div class="row g-3"><div class="col-md-4"><a class="text-decoration-none text-dark" href="publications.html"><strong>${submitted}</strong><small class="d-block text-muted">Submitted publications</small></a></div><div class="col-md-4"><a class="text-decoration-none text-dark" href="reviews.html"><strong>${pendingReviews}</strong><small class="d-block text-muted">Pending reviewer assignments</small></a></div><div class="col-md-4"><strong>${escapeHtml(institution.name)}</strong><small class="d-block text-muted">Assigned institution workspace</small></div></div>` : '<div class="alert alert-info mb-0">Your account has not been assigned to an institution yet. Ask a System Admin to assign your workspace.</div>'}`;
  } else if (pageRole === 'publisher') {
    const statuses = ['draft','submitted','published','archived'];
    panel.innerHTML = `<h2 class="h5 mb-1">Publication pipeline</h2><p class="text-muted mb-3">Select a stage to manage those publication records.</p><div class="row g-3">${statuses.map(status => `<div class="col-sm-3"><a href="publications.html" class="border rounded-3 p-3 text-center text-decoration-none d-block text-dark"><strong class="fs-4">${publications.filter(item => item.status === status).length}</strong><small class="d-block text-capitalize text-muted">${status}</small></a></div>`).join('')}</div>`;
  } else {
    const pending = reviews.filter(item => item.status === 'pending');
    const overdue = pending.filter(item => item.due_date && new Date(item.due_date) < new Date()).length;
    panel.innerHTML = `<div class="d-flex justify-content-between align-items-center mb-3"><div><h2 class="h5 mb-1">Review action centre</h2><p class="text-muted mb-0">Only reviews assigned to your account are shown.</p></div><a class="btn btn-primary btn-sm" href="reviews.html">Start review</a></div><div class="row g-3"><div class="col-md-4"><a class="text-decoration-none text-dark" href="reviews.html"><strong>${pending.length}</strong><small class="d-block text-muted">Pending reviews</small></a></div><div class="col-md-4"><a class="text-decoration-none text-dark" href="reviews.html"><strong>${overdue}</strong><small class="d-block text-muted">Overdue reviews</small></a></div><div class="col-md-4"><strong>${reviews.filter(item => item.status !== 'pending').length}</strong><small class="d-block text-muted">Completed decisions</small></div></div>`;
  }
  document.querySelector('main').append(panel);
}

async function loadRoleDashboard() {
  document.getElementById('roleTitle').textContent = config.title;
  document.getElementById('roleSubtitle').textContent = config.subtitle;
  document.getElementById('roleIcon').className = `bi ${config.icon}`;
  document.getElementById('roleActions').innerHTML = config.actions.map(([icon,label,href]) => `<a class="role-action text-decoration-none" href="${href}"><i class="bi ${icon}"></i><span class="flex-grow-1 fw-semibold text-dark">${label}</span><i class="bi bi-arrow-right-short"></i></a>`).join('');
  try {
    const [dashboard, publications, projects, conferences, user, researchers, institutions, collaborations, workspace, reviews] = await Promise.all([
      safeJson(`${API_BASE}/dashboard/workspace`), safeJson(`${API_BASE}/publications/`), safeJson(`${API_BASE}/projects/`), safeJson(`${API_BASE}/conferences/`), safeJson(`${API_BASE}/users/me`), safeJson(`${API_BASE}/researchers/`), safeJson(`${API_BASE}/institutions/`), safeJson(`${API_BASE}/collaborations/detailed`), safeJson(`${API_BASE}/users/me/workspace`), safeJson(`${API_BASE}/reviews/`)
    ]);
    user.workspace = workspace;
    const published = publications.filter(item => item.status === 'published').length;
    const submitted = publications.filter(item => item.status === 'submitted').length;
    const draft = publications.filter(item => item.status === 'draft').length;
    const pendingReviews = reviews.filter(item => item.status === 'pending').length;
    const entries = pageRole === 'researcher'
      ? [['bi-journal-text','My publications',dashboard.total_publications,'publications.html'],['bi-people-fill','My collaborations',dashboard.total_collaborations,'collaborations.html'],['bi-calendar-event','My conferences',dashboard.total_conferences,'conferences.html'],['bi-folder2-open','My projects',dashboard.total_projects,'projects.html']]
      : pageRole === 'institution'
        ? [['bi-people','Institution researchers',dashboard.total_researchers,'researchers.html'],['bi-journal-text','Institution publications',dashboard.total_publications,'publications.html'],['bi-folder2-open','Active projects',dashboard.total_projects,'projects.html'],['bi-clipboard-check','Pending reviews',pendingReviews,'reviews.html']]
        : pageRole === 'publisher'
          ? [['bi-journal-check','Published records',published,'publications.html'],['bi-send-check','Submitted records',submitted,'publications.html'],['bi-clipboard-check','Pending reviews',pendingReviews,'reviews.html'],['bi-quote','Citation records',dashboard.total_citations,'citations.html']]
          : [['bi-clipboard-check','Assigned reviews',reviews.length,'reviews.html'],['bi-hourglass-split','Pending decisions',pendingReviews,'reviews.html'],['bi-check2-circle','Completed reviews',reviews.filter(item => item.status !== 'pending').length,'reviews.html'],['bi-journal-text','Assigned publications',publications.length,'publications.html']];
    document.getElementById('roleStats').innerHTML = entries.map((entry, index) => stat(...entry, index === 1 ? 'success' : 'primary')).join('');
    const recent = pageRole === 'reviewer' ? reviews.slice(0, 6).map(item => ({title: item.publication_title, status: item.status, venue: item.due_date ? `Due ${item.due_date}` : 'No due date', href: 'reviews.html'})) : (pageRole === 'publisher' ? publications.filter(item => ['submitted','published'].includes(item.status)) : publications).slice(0, 6).map(item => ({title: item.title, status: item.status || 'draft', venue: item.journal_or_venue || 'No venue', href: 'publications.html'}));
    document.getElementById('recentTitle').textContent = pageRole === 'researcher' ? 'My recent research activity' : pageRole === 'institution' ? 'Institution publication activity' : pageRole === 'publisher' ? 'Publication pipeline activity' : 'Assigned review activity';
    document.getElementById('recentItems').innerHTML = recent.length ? recent.map(item => `<a class="role-action text-decoration-none" href="${item.href}"><i class="bi ${pageRole === 'reviewer' ? 'bi-clipboard-check' : 'bi-journal-text'}"></i><div class="flex-grow-1"><strong>${escapeHtml(item.title)}</strong><small class="d-block text-muted text-capitalize">${escapeHtml(item.status)} · ${escapeHtml(item.venue)}</small></div><i class="bi bi-arrow-right-short"></i></a>`).join('') : '<p class="text-muted mb-0">No relevant activity yet.</p>';
    renderWorkspace({ user, researchers, institutions, publications, collaborations, reviews });
  } catch (error) {
    document.getElementById('roleStats').innerHTML = '<div class="col-12"><div class="alert alert-warning">Dashboard data is unavailable. Please sign in again and retry.</div></div>';
  }
}

loadRoleDashboard();
