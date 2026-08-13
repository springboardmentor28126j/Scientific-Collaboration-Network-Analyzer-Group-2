(() => {
  const nativeFetch = window.fetch.bind(window);
  window.fetch = (input, init = {}) => {
    const url = typeof input === "string" ? input : input.url;
    const token = localStorage.getItem("token");
    if (token && url.startsWith("http://127.0.0.1:8000/") && !url.includes("/users/login") && !url.includes("/users/register")) {
      const headers = new Headers(init.headers || {});
      if (!headers.has("Authorization")) headers.set("Authorization", "Bearer " + token);
      return nativeFetch(input, { ...init, headers });
    }
    return nativeFetch(input, init);
  };
  const inPagesFolder = window.location.pathname.includes("/pages/");
  const current = window.location.pathname.split("/").pop();
  const allLinks = [["dashboard.html","bi-speedometer2","Dashboard"],["pages/researchers.html","bi-people","Researchers"],["pages/institutions.html","bi-building","Institutions"],["pages/publications.html","bi-journal-text","Publications"],["pages/reviews.html","bi-clipboard-check","Reviews"],["pages/collaborations.html","bi-people-fill","Collaborations"],["pages/projects.html","bi-folder2-open","Projects"],["pages/conferences.html","bi-calendar-event","Conferences"],["pages/citations.html","bi-quote","Citations"],["pages/report.html","bi-file-earmark-bar-graph","Reports"]];
  const currentRole = (localStorage.getItem("role") || "Researcher").toLowerCase();
  const isSystemAdmin = ["admin", "system admin"].includes(currentRole);
  const roleDashboard = {"researcher":"researcher-dashboard.html","institution admin":"institution-dashboard.html","publisher":"publisher-dashboard.html","reviewer":"reviewer-dashboard.html"}[currentRole];
  const isAdminOnlyPage = ["dashboard.html", "admin-notifications.html", "admin-approvals.html", "admin-accounts.html", "audit-logs.html", "data-quality.html"].includes(current);
  if (!isSystemAdmin && roleDashboard && isAdminOnlyPage) {
    window.location.replace(inPagesFolder ? roleDashboard : `pages/${roleDashboard}`);
    return;
  }
  const allowedLabels = isSystemAdmin ? null : (currentRole === "institution admin" ? ["Dashboard","Researchers","Institutions","Publications","Reviews","Conferences","Reports"] : currentRole === "publisher" ? ["Dashboard","Publications","Reviews","Citations","Reports"] : currentRole === "reviewer" ? ["Dashboard","Reviews","Publications","Citations","Reports"] : ["Dashboard","Publications","Conferences","Reports"]);
  const links = allowedLabels ? allLinks.filter(([, , label]) => allowedLabels.includes(label)) : [...allLinks, ["pages/audit-logs.html","bi-shield-check","Audit log"], ["pages/data-quality.html","bi-clipboard2-check","Data quality"]];
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
  const isAdmin = isSystemAdmin;
  const notificationMenu = document.createElement("div");
  notificationMenu.id = "appNotifications";
  notificationMenu.className = "dropdown";
  notificationMenu.innerHTML = `<button id="notificationButton" class="btn btn-light notification-button shadow-sm" type="button" data-bs-toggle="dropdown" aria-expanded="false" aria-label="Open notifications"><i class="bi bi-bell"></i><span id="notificationBadge" class="notification-badge d-none">0</span></button><div class="dropdown-menu dropdown-menu-end notification-menu shadow"><div class="notification-header"><div><strong>Notifications</strong><small>Latest system activity</small></div><button id="markAllNotifications" class="btn btn-sm btn-link p-0">Mark all read</button></div><div id="notificationList" class="notification-list"><div class="notification-empty">Loading notifications...</div></div></div>`;

  const userMenu = document.createElement("div");
  userMenu.id = "appUserMenu";
  userMenu.className = "dropdown";
  userMenu.innerHTML = `<button class="btn btn-light dropdown-toggle shadow-sm" data-bs-toggle="dropdown"><i class="bi bi-person-circle"></i> <span>${userName}</span></button><ul class="dropdown-menu dropdown-menu-end shadow"><li><a class="dropdown-item" href="${profileHref}"><i class="bi bi-person me-2"></i>View Profile</a></li>${isAdmin ? `<li><a class="dropdown-item" href="${inPagesFolder ? "admin-approvals.html" : "pages/admin-approvals.html"}"><i class="bi bi-person-check me-2"></i>Account approvals</a></li><li><a class="dropdown-item" href="${inPagesFolder ? "admin-accounts.html" : "pages/admin-accounts.html"}"><i class="bi bi-people me-2"></i>Account directory</a></li>` : ""}<li><hr class="dropdown-divider"></li><li><button class="dropdown-item text-danger" id="globalLogout"><i class="bi bi-box-arrow-right me-2"></i>Sign out</button></li></ul>`;
  const topActions = document.createElement("div");
  topActions.id = "appTopActions";
  topActions.className = "app-navbar-actions";
  if (isAdmin) {
    const announcementButton = document.createElement("a");
    announcementButton.className = "btn btn-light shadow-sm";
    announcementButton.href = inPagesFolder ? "admin-notifications.html" : "pages/admin-notifications.html";
    announcementButton.title = "Send announcement";
    announcementButton.setAttribute("aria-label", "Send announcement");
    announcementButton.innerHTML = '<i class="bi bi-send"></i>';
    topActions.append(notificationMenu, announcementButton, userMenu);
  } else {
  topActions.append(notificationMenu, userMenu);
  }
  if (!document.getElementById("sharedTableTools")) {
    const tableTools = document.createElement("script");
    tableTools.id = "sharedTableTools";
    tableTools.src = inPagesFolder ? "../js/table-tools.js" : "js/table-tools.js";
    document.head.append(tableTools);
  }
  document.body.prepend(sidebar);
  const appNavbar = document.querySelector("nav.navbar");
  const navbarContent = appNavbar?.querySelector(".container-fluid");
  if (navbarContent) {
    appNavbar.classList.add("app-navbar-with-actions");
    navbarContent.append(topActions);
  } else {
    document.body.prepend(topActions);
  }
  const toggle = document.getElementById("appSidebarToggle");
  const applyState = collapsed => {
    document.body.classList.toggle("sidebar-collapsed", collapsed);
    toggle.querySelector("i").className = collapsed ? "bi bi-layout-sidebar" : "bi bi-layout-sidebar-inset";
  };
  applyState(localStorage.getItem("sidebarCollapsed") === "true");
  toggle.addEventListener("click", () => { const collapsed = !document.body.classList.contains("sidebar-collapsed"); applyState(collapsed); localStorage.setItem("sidebarCollapsed", collapsed); });
  document.getElementById("globalLogout").addEventListener("click", async () => { try { await fetch("http://127.0.0.1:8000/users/logout", { method: "POST", headers: { Authorization: "Bearer " + localStorage.getItem("token") } }); } finally { localStorage.clear(); window.location.href = loginHref; } });

  const notificationIcons = { publication: "bi-journal-text", conference: "bi-calendar-event", project: "bi-folder2-open", collaboration: "bi-people-fill", citation: "bi-quote", report: "bi-file-earmark-bar-graph", approval: "bi-person-check" };
  const notificationList = document.getElementById("notificationList");
  const notificationBadge = document.getElementById("notificationBadge");
  const notificationToken = localStorage.getItem("token");
  const notificationHeaders = notificationToken ? { Authorization: "Bearer " + notificationToken } : {};
  fetch("http://127.0.0.1:8000/notifications/", { headers: notificationHeaders })
    .then(response => response.ok ? response.json() : Promise.reject(new Error("Unable to load notifications")))
    .then(data => {
      const notifications = data.notifications || [];
      const count = Number(data.count);
      notificationBadge.textContent = count > 9 ? "9+" : count;
      notificationBadge.classList.toggle("d-none", count === 0);
      notificationList.innerHTML = notifications.length
        ? notifications.map(item => `<button class="notification-item w-100 border-0 text-start ${item.is_read ? "" : "fw-semibold"}" data-notification-id="${item.id}" data-link="${item.link || ""}"><span class="notification-icon"><i class="bi ${notificationIcons[item.type] || "bi-bell"}"></i></span><span><span class="d-block">${item.title}</span><small class="fw-normal">${item.message}</small></span></button>`).join("")
        : '<div class="notification-empty"><i class="bi bi-bell-slash"></i> No new notifications</div>';
      notificationList.querySelectorAll("[data-notification-id]").forEach(item => item.addEventListener("click", () => {
        fetch(`http://127.0.0.1:8000/notifications/${item.dataset.notificationId}/read`, { method: "POST", headers: notificationHeaders });
        if (item.dataset.link) window.location.href = inPagesFolder ? "../" + item.dataset.link : item.dataset.link;
      }));
    })
    .catch(() => {
      notificationList.innerHTML = '<div class="notification-empty"><i class="bi bi-wifi-off"></i> Notifications are unavailable.</div>';
    });
  document.getElementById("markAllNotifications").addEventListener("click", () => fetch("http://127.0.0.1:8000/notifications/read-all", { method: "POST", headers: notificationHeaders }).then(() => window.location.reload()));
})();
