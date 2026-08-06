import { Link, useLocation, useNavigate } from "react-router-dom";

import "../styles/researcherSidebar.css";

function ResearcherSidebar() {

  const location = useLocation();
  const navigate = useNavigate();

  const logout = () => {

    localStorage.clear();

    navigate("/login");

  };

  return (

    <aside className="sidebar">

      <div className="sidebar-top">

        <h2>👨‍🔬</h2>

        <h3>Researcher</h3>

      </div>
<nav>

  <Link
    to="/researcher-dashboard"
    className={location.pathname === "/researcher-dashboard" ? "active" : ""}
  >
    🏠 Dashboard
  </Link>

  <Link
    to="/researcher-profile"
    className={location.pathname === "/researcher-profile" ? "active" : ""}
  >
    👤 My Profile
  </Link>

  <Link
    to="/my-papers"
    className={location.pathname === "/my-papers" ? "active" : ""}
  >
    📄 My Papers
  </Link>

  <Link
    to="/upload-paper"
    className={location.pathname === "/upload-paper" ? "active" : ""}
  >
    📤 Upload Paper
  </Link>

  <Link
    to="/collaborations"
    className={location.pathname === "/collaborations" ? "active" : ""}
  >
    🤝 Collaborations
  </Link>

  <Link
    to="/analytics"
    className={location.pathname === "/analytics" ? "active" : ""}
  >
    📊 Analytics
  </Link>
  <li>
    <Link to="/reports">
        📊 Reports
    </Link>
</li>

  <Link
    to="/settings"
    className={location.pathname === "/settings" ? "active" : ""}
  >
    ⚙ Settings
  </Link>

  <Link
    to="/add-conference"
    className={location.pathname === "/add-conference" ? "active" : ""}
  >
    ➕ Add Conference
  </Link>

  <Link
    to="/my-conferences"
    className={location.pathname === "/my-conferences" ? "active" : ""}
  >
    🎓 My Conferences
  </Link>

  <Link
    to="/institution-management"
    className={location.pathname === "/institution-management" ? "active" : ""}
  >
    🏛 Institution Management
  </Link>

  <hr />

  <Link
    to="/projects"
    className={location.pathname === "/projects" ? "active" : ""}
  >
    📁 Projects
  </Link>

  <Link
    to="/collaboration-dashboard"
    className={location.pathname === "/collaboration-dashboard" ? "active" : ""}
  >
    📈 Collaboration Dashboard
  </Link>

  <Link
    to="/collaboration-requests"
    className={location.pathname === "/collaboration-requests" ? "active" : ""}
  >
    👥 Collaboration Requests
  </Link>

  <Link
    to="/institution-requests"
    className={location.pathname === "/institution-requests" ? "active" : ""}
  >
    🏢 Institution Requests
  </Link>

  <Link
    to="/citations"
    className={location.pathname === "/citations" ? "active" : ""}
  >
    📚 Citation Management
  </Link>

  <Link
    to="/shared-files"
    className={location.pathname === "/shared-files" ? "active" : ""}
  >
    📂 Shared Files
  </Link>

  <Link
    to="/progress-updates"
    className={location.pathname === "/progress-updates" ? "active" : ""}
  >
    📊 Progress Updates
  </Link>

  <Link
    to="/notifications"
    className={location.pathname === "/notifications" ? "active" : ""}
  >
    🔔 Notifications
  </Link>

  <Link
    to="/timeline"
    className={location.pathname === "/timeline" ? "active" : ""}
  >
    🕒 Timeline
  </Link>

</nav>
      <li>
    <Link to="/add-conference">
        ➕ Add Conference
    </Link>
</li>

<li>
    <Link to="/my-conferences">
        🎓 My Conferences
    </Link>
</li>
<Link to="/institution-management">
    🏛 Institution Management
</Link>
      <button
        className="logout-btn"
        onClick={logout}
      >
        🚪 Logout
      </button>

    </aside>

  );

}

export default ResearcherSidebar;