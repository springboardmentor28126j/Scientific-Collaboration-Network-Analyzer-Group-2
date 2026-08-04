(() => {
  const inPagesFolder = window.location.pathname.includes("/pages/");
  const current = window.location.pathname.split("/").pop();
  const links = [["dashboard.html","bi-speedometer2","Dashboard"],["pages/researchers.html","bi-people","Researchers"],["pages/institutions.html","bi-building","Institutions"],["pages/publications.html","bi-journal-text","Publications"],["pages/collaborations.html","bi-people-fill","Collaborations"],["pages/projects.html","bi-folder2-open","Projects"],["pages/conferences.html","bi-calendar-event","Conferences"],["pages/citations.html","bi-quote","Citations"],["pages/report.html","bi-file-earmark-bar-graph","Reports"]];
  const hrefFor = href => inPagesFolder ? (href === "dashboard.html" ? "../dashboard.html" : href.replace(/^pages\//, "")) : href;
  const filenameFor = href => href.replace(/^pages\//, "");
  const profileHref = inPagesFolder ? "../profile.html" : "profile.html";
  const loginHref = inPagesFolder ? "../index.html" : "index.html";

  document.querySelectorAll(".sidebar").forEach(sidebar => sidebar.remove());
  document.getElementById("sidebarToggle")?.remove();
  document.querySelectorAll("nav a.btn, nav .dropdown").forEach(item => item.remove());

  const sidebar = document.createElement("aside");
  sidebar.id = "appSidebar";
  sidebar.innerHTML = `<div class="app-sidebar-brand"><i class="bi bi-diagram-3-fill"></i><span>Research Portal</span></div><nav>${links.map(([href,icon,label]) => `<a href="${hrefFor(href)}" class="${filenameFor(href) === current ? "active" : ""}" title="${label}"><i class="bi ${icon}"></i><span>${label}</span></a>`).join("")}</nav><button id="appSidebarToggle" type="button" title="Collapse or expand navigation"><i class="bi bi-layout-sidebar-inset"></i></button>`;

  const userName = localStorage.getItem("username") || "User";
  const notificationMenu = document.createElement("div");
  notificationMenu.id = "appNotifications";
  notificationMenu.className = "dropdown";
  notificationMenu.innerHTML = `<button id="notificationButton" class="btn btn-light notification-button shadow-sm" type="button" data-bs-toggle="dropdown" aria-expanded="false" aria-label="Open notifications"><i class="bi bi-bell"></i><span id="notificationBadge" class="notification-badge d-none">0</span></button><div class="dropdown-menu dropdown-menu-end notification-menu shadow"><div class="notification-header"><div><strong>Notifications</strong><small>Latest system activity</small></div><span id="notificationCountText" class="badge text-bg-primary">0</span></div><div id="notificationList" class="notification-list"><div class="notification-empty">Loading notifications...</div></div></div>`;

  const userMenu = document.createElement("div");
  userMenu.id = "appUserMenu";
  userMenu.className = "dropdown";
  userMenu.innerHTML = `<button class="btn btn-light dropdown-toggle shadow-sm" data-bs-toggle="dropdown"><i class="bi bi-person-circle"></i> <span>${userName}</span></button><ul class="dropdown-menu dropdown-menu-end shadow"><li><a class="dropdown-item" href="${profileHref}"><i class="bi bi-person me-2"></i>View Profile</a></li><li><hr class="dropdown-divider"></li><li><button class="dropdown-item text-danger" id="globalLogout"><i class="bi bi-box-arrow-right me-2"></i>Sign out</button></li></ul>`;
  const topActions = document.createElement("div");
  topActions.id = "appTopActions";
  topActions.append(notificationMenu, userMenu);
  document.body.prepend(sidebar);
  document.body.prepend(topActions);
  const toggle = document.getElementById("appSidebarToggle");
  const applyState = collapsed => {
    document.body.classList.toggle("sidebar-collapsed", collapsed);
    toggle.querySelector("i").className = collapsed ? "bi bi-layout-sidebar" : "bi bi-layout-sidebar-inset";
  };
  applyState(localStorage.getItem("sidebarCollapsed") === "true");
  toggle.addEventListener("click", () => { const collapsed = !document.body.classList.contains("sidebar-collapsed"); applyState(collapsed); localStorage.setItem("sidebarCollapsed", collapsed); });
  document.getElementById("globalLogout").addEventListener("click", () => { localStorage.clear(); window.location.href = loginHref; });

  const notificationIcons = { publication: "bi-journal-text", conference: "bi-calendar-event", project: "bi-folder2-open" };
  const notificationList = document.getElementById("notificationList");
  const notificationBadge = document.getElementById("notificationBadge");
  const notificationCountText = document.getElementById("notificationCountText");
  fetch("http://127.0.0.1:8000/notifications/")
    .then(response => response.ok ? response.json() : Promise.reject(new Error("Unable to load notifications")))
    .then(data => {
      const notifications = data.notifications || [];
      const count = Number(data.count) || notifications.length;
      notificationCountText.textContent = count;
      notificationBadge.textContent = count > 9 ? "9+" : count;
      notificationBadge.classList.toggle("d-none", count === 0);
      notificationList.innerHTML = notifications.length
        ? notifications.map(item => `<div class="notification-item"><span class="notification-icon"><i class="bi ${notificationIcons[item.type] || "bi-bell"}"></i></span><span>${item.message}</span></div>`).join("")
        : '<div class="notification-empty"><i class="bi bi-bell-slash"></i> No new notifications</div>';
    })
    .catch(() => {
      notificationCountText.textContent = "0";
      notificationList.innerHTML = '<div class="notification-empty"><i class="bi bi-wifi-off"></i> Notifications are unavailable.</div>';
    });
})();
