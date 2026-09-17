import { Link } from "react-router-dom";
import "../css/sidebar.css";

function Sidebar() {
  return (
    <div className="sidebar">
      <h2>SCNA</h2>

      <Link to="/dashboard">Dashboard</Link>
      <Link to="/researchers">Researchers</Link>
      <Link to="/publications">Publications</Link>
      <Link to="/conferences">Conferences</Link>
      <Link to="/reports">Reports</Link>
    </div>
  );
}

export default Sidebar;