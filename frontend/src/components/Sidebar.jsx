import { Link } from "react-router-dom";
import "../styles/sidebar.css";

function Sidebar() {
  return (
    <div className="sidebar">

      <h2>Navigation</h2>

      <hr />

      <Link to="/">🏠 Dashboard</Link>

      <Link to="/researchers">👨‍🔬 Researchers</Link>

      <Link to="/papers">📄 Research Papers</Link>

      <Link to="/institutions">🏫 Institutions</Link>

      <Link to="/login">🔐 Authentication</Link>
       
      <Link to="/login">🔐 Login</Link>

      <Link to="/register">📝 Register</Link>

    </div>
  );
}

export default Sidebar;