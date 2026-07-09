import "../styles/navbar.css";
import { useNavigate } from "react-router-dom";

function Navbar() {

  const navigate = useNavigate();

  const today = new Date();

  const user = localStorage.getItem("user");

  const handleLogout = () => {

    localStorage.removeItem("token");
    localStorage.removeItem("user");

    navigate("/login");

  };

  return (

    <nav className="navbar">

      <div className="logo">
        🔬 Scientific Collaboration Network Analyzer
      </div>

      <div className="status">

        <div className="online">
          🟢 System Online
        </div>

        <div className="date">
          {today.toLocaleDateString()}
        </div>

        {user && (
          <>
            <div className="welcome">
              👋 Welcome, {user}
            </div>

            <button
              className="logout-btn"
              onClick={handleLogout}
            >
              Logout
            </button>
          </>
        )}

      </div>

    </nav>

  );

}

export default Navbar;