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

        <Link
          to="/settings"
          className={location.pathname === "/settings" ? "active" : ""}
        >
          ⚙ Settings
        </Link>
        <Link to="/my-papers">
    📄 My Papers
</Link>

      </nav>

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