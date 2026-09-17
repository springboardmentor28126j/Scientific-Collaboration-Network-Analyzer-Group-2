import { Link, useNavigate } from "react-router-dom";
import "../css/dashboard.css";

function Dashboard() {
  const navigate = useNavigate();

  // Get logged-in user details
  const username = localStorage.getItem("username");
  const role = localStorage.getItem("role");

  // Logout
  const handleLogout = () => {
    localStorage.removeItem("username");
    localStorage.removeItem("email");
    localStorage.removeItem("role");
    localStorage.removeItem("user_id");
    localStorage.removeItem("access_token");

    navigate("/");
  };

  const menuItems = [
    {
      label: "Dashboard",
      icon: "⌂",
      path: "/dashboard",
      roles: [
        "Researcher",
        "Institution Admin",
        "Reviewer",
        "System Admin",
      ],
    },
    {
      label: "Researchers",
      icon: "♙",
      path: "/researchers",
      roles: [
        "Researcher",
        "Institution Admin",
        "System Admin",
      ],
    },
    {
      label: "Publications",
      icon: "▤",
      path: "/publications",
      roles: [
        "Researcher",
        "Institution Admin",
        "Reviewer",
        "System Admin",
      ],
    },
    {
      label: "Collaborations",
      icon: "⇄",
      path: "/collaborations",
      roles: [
        "Researcher",
        "Institution Admin",
        "System Admin",
      ],
    },
    {
      label: "Conferences",
      icon: "▣",
      path: "/conferences",
      roles: [
        "Researcher",
        "Institution Admin",
        "Reviewer",
        "System Admin",
      ],
    },
    {
      label: "Reviews",
      icon: "✓",
      path: "/reviews",
      roles: [
        "Institution Admin",
        "Reviewer",
        "System Admin",
      ],
    },
    {
      label: "Analytics",
      icon: "◫",
      path: "/analytics",
      roles: [
        "Institution Admin",
        "System Admin",
      ],
    },
    {
      label: "Reports",
      icon: "▥",
      path: "/reports",
      roles: [
        "Institution Admin",
        "Reviewer",
        "System Admin",
      ],
    },
    {
      label: "Citations",
      icon: "❖",
      path: "/citations",
      roles: [
        "Researcher",
        "Institution Admin",
        "Reviewer",
        "System Admin",
      ],
    },
    {
      label: "Profile",
      icon: "◉",
      path: "/profile",
      roles: [
        "Researcher",
        "Institution Admin",
        "Reviewer",
        "System Admin",
      ],
    },
  ];

  const visibleMenu = menuItems.filter((item) =>
    item.roles.includes(role)
  );

  const roleInfo = {
    "System Admin": {
      title: "System Administration",
      text: "Manage the complete research collaboration platform and monitor overall system activity.",
      badge: "Full System Access",
    },

    "Institution Admin": {
      title: "Institution Management",
      text: "Manage researchers, publications, collaborations, conferences and institutional analytics.",
      badge: "Institution Access",
    },

    Researcher: {
      title: "Research Workspace",
      text: "Manage your research profile, publications, collaborations and conference activities.",
      badge: "Researcher Access",
    },

    Reviewer: {
      title: "Review Workspace",
      text: "Review assigned publications and monitor review queues and publication information.",
      badge: "Reviewer Access",
    },
  };

  const currentRole = roleInfo[role] || {
    title: "Research Workspace",
    text: "Manage your research activities from one place.",
    badge: "User Access",
  };

  const stats = [
    {
      value: "150",
      label: "Researchers",
      icon: "♙",
      tone: "blue",
    },
    {
      value: "540",
      label: "Publications",
      icon: "▤",
      tone: "violet",
    },
    {
      value: "95",
      label: "Collaborations",
      icon: "⇄",
      tone: "green",
    },
    {
      value: "28",
      label: "Conferences",
      icon: "▣",
      tone: "orange",
    },
  ];

  return (
    <div className="dashboard-container">

      {/* ================= TOP NAVBAR ================= */}

      <header className="topbar">

        <div className="brand">
          <div className="brand-mark">S</div>

          <div>
            <div className="brand-name">
              SciCollab
            </div>

            <div className="brand-subtitle">
              Scientific Collaboration Network
            </div>
          </div>
        </div>

        <div className="topbar-right">

          {/* User Profile */}

          <div className="user-mini">

            <div className="user-avatar">
              {(username || "U").charAt(0).toUpperCase()}
            </div>

            <div className="user-mini-info">
              <strong>
                {username || "User"}
              </strong>

              <span>
                {role || "User"}
              </span>
            </div>

          </div>

          {/* ================= NOTIFICATIONS ================= */}

          <Link
            to="/notifications"
            className="notification-bell"
            title="Notifications"
            aria-label="Notifications"
          >
            <span className="notification-bell-icon">
              🔔
            </span>
          </Link>

          {/* Logout */}

          <button
            className="top-logout"
            onClick={handleLogout}
          >
            Logout
          </button>

        </div>

      </header>

      {/* ================= DASHBOARD BODY ================= */}

      <div className="dashboard-body">

        {/* ================= SIDEBAR ================= */}

        <aside className="sidebar">

          <div className="sidebar-heading">
            <span>WORKSPACE</span>
          </div>

          <nav className="sidebar-nav">

            {visibleMenu.map((item) => (

              <Link
                key={item.path}
                to={item.path}
                className={`sidebar-link ${
                  item.path === "/dashboard"
                    ? "active"
                    : ""
                }`}
              >

                <span className="sidebar-icon">
                  {item.icon}
                </span>

                <span>
                  {item.label}
                </span>

              </Link>

            ))}

          </nav>

          <div className="sidebar-footer">

            <div className="secure-dot"></div>

            <div>
              <strong>
                Secure Workspace
              </strong>

              <span>
                Role-based access enabled
              </span>
            </div>

          </div>

        </aside>

        {/* ================= MAIN CONTENT ================= */}

        <main className="content">

          {/* Welcome */}

          <section className="welcome-section">

            <div>

              <span className="eyebrow">
                SCIENTIFIC COLLABORATION NETWORK
              </span>

              <h1>
                Welcome back,{" "}
                {username || "Researcher"}.
              </h1>

              <p>
                Monitor research, publications,
                collaborations and conferences
                from one professional workspace.
              </p>

            </div>

            <div className="date-chip">

              <span className="date-dot"></span>

              {currentRole.badge}

            </div>

          </section>

          {/* Workspace */}

          <section className="role-banner">

            <div className="role-banner-icon">

              {role === "System Admin"
                ? "⚙"
                : role === "Institution Admin"
                ? "⌂"
                : role === "Reviewer"
                ? "✓"
                : "♙"}

            </div>

            <div className="role-banner-content">

              <span className="section-label">
                CURRENT WORKSPACE
              </span>

              <h2>
                {currentRole.title}
              </h2>

              <p>
                {currentRole.text}
              </p>

            </div>

          </section>

          {/* Statistics */}

          <section className="stats-grid">

            {stats.map((stat) => (

              <div
                className={`stat-card ${stat.tone}`}
                key={stat.label}
              >

                <div className="stat-top">

                  <div className="stat-icon">
                    {stat.icon}
                  </div>

                  <span className="stat-indicator">
                    Overview
                  </span>

                </div>

                <strong>
                  {stat.value}
                </strong>

                <span>
                  {stat.label}
                </span>

              </div>

            ))}

          </section>

          {/* ================= DASHBOARD GRID ================= */}

          <section className="dashboard-grid">

            {/* Recent Publications */}

            <div className="panel publications-panel">

              <div className="panel-header">

                <div>

                  <span className="section-label">
                    RESEARCH OUTPUT
                  </span>

                  <h2>
                    Recent Publications
                  </h2>

                </div>

                <Link
                  to="/publications"
                  className="view-link"
                >
                  View all →
                </Link>

              </div>

              <div className="publication-list">

                <div className="publication-row">

                  <div className="publication-number">
                    01
                  </div>

                  <div className="publication-info">

                    <strong>
                      AI in Healthcare
                    </strong>

                    <span>
                      Jhansi Padala · 2026
                    </span>

                  </div>

                  <span className="status-pill published">
                    Published
                  </span>

                </div>

                <div className="publication-row">

                  <div className="publication-number">
                    02
                  </div>

                  <div className="publication-info">

                    <strong>
                      Machine Learning
                    </strong>

                    <span>
                      Rahul Kumar · 2025
                    </span>

                  </div>

                  <span className="status-pill review">
                    Under Review
                  </span>

                </div>

                <div className="publication-row">

                  <div className="publication-number">
                    03
                  </div>

                  <div className="publication-info">

                    <strong>
                      Natural Language Processing
                    </strong>

                    <span>
                      Priya Sharma · 2026
                    </span>

                  </div>

                  <span className="status-pill published">
                    Published
                  </span>

                </div>

              </div>

            </div>

            {/* Recent Activity */}

            <div className="panel activity-panel">

              <div className="panel-header">

                <div>

                  <span className="section-label">
                    SYSTEM ACTIVITY
                  </span>

                  <h2>
                    Recent Activity
                  </h2>

                </div>

              </div>

              <div className="activity-list">

                <div className="activity-item">

                  <div className="activity-icon success">
                    ✓
                  </div>

                  <div>

                    <strong>
                      New publication added
                    </strong>

                    <span>
                      Research repository updated
                    </span>

                  </div>

                </div>

                <div className="activity-item">

                  <div className="activity-icon collaboration">
                    ⇄
                  </div>

                  <div>

                    <strong>
                      Collaboration activity
                    </strong>

                    <span>
                      Research collaboration updated
                    </span>

                  </div>

                </div>

                <div className="activity-item">

                  <div className="activity-icon conference">
                    ▣
                  </div>

                  <div>

                    <strong>
                      Conference activity
                    </strong>

                    <span>
                      Conference information updated
                    </span>

                  </div>

                </div>

                <div className="activity-item">

                  <div className="activity-icon profile">
                    ◉
                  </div>

                  <div>

                    <strong>
                      Research profile updated
                    </strong>

                    <span>
                      Profile information saved
                    </span>

                  </div>

                </div>

              </div>

            </div>

          </section>

          {/* ================= QUICK NAVIGATION ================= */}

          <section className="quick-section">

            <div className="panel-header">

              <div>

                <span className="section-label">
                  QUICK NAVIGATION
                </span>

                <h2>
                  Research Workspace
                </h2>

              </div>

            </div>

            <div className="quick-grid">

              {visibleMenu
                .filter(
                  (item) =>
                    item.path !== "/dashboard" &&
                    item.path !== "/profile"
                )
                .slice(0, 6)
                .map((item) => (

                  <Link
                    to={item.path}
                    className="quick-card"
                    key={item.path}
                  >

                    <span className="quick-icon">
                      {item.icon}
                    </span>

                    <span>

                      <strong>
                        {item.label}
                      </strong>

                      <small>
                        Open workspace
                      </small>

                    </span>

                    <b>
                      →
                    </b>

                  </Link>

                ))}

            </div>

          </section>

          {/* Footer */}

          <footer className="dashboard-footer">

            <span>
              © 2026 SciCollab
            </span>

            <span>
              Scientific Collaboration Network Analyzer
            </span>

            <span>
              Secure role-based platform
            </span>

          </footer>

        </main>

      </div>

    </div>
  );
}

export default Dashboard;