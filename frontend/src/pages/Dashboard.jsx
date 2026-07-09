import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import api from "../services/api";

import "../styles/dashboard.css";

function Dashboard() {
  const [dashboard, setDashboard] = useState({
    total_papers: 0,
    total_researchers: 0,
    total_institutions: 0,
    total_collaborations: 0,
  });

  useEffect(() => {
    api
      .get("/analytics/dashboard")
      .then((res) => {
        setDashboard(res.data);
      })
      .catch((err) => {
        console.error("Dashboard Error:", err);
      });
  }, []);

  return (
    <div>
      <Navbar />

      <div className="dashboard-container">
        <Sidebar />

        <div className="dashboard-content">
          <h2>📊 Dashboard Overview</h2>

          <div className="cards">
            <div className="card">
              <h3>👨‍🔬 Researchers</h3>
              <h1>{dashboard.total_researchers}</h1>
            </div>

            <div className="card">
              <h3>📄 Research Papers</h3>
              <h1>{dashboard.total_papers}</h1>
            </div>

            <div className="card">
              <h3>🏫 Institutions</h3>
              <h1>{dashboard.total_institutions}</h1>
            </div>

            <div className="card">
              <h3>🤝 Collaborations</h3>
              <h1>{dashboard.total_collaborations}</h1>
            </div>
          </div>

          <div className="welcome-box">
            <h3>Welcome to Scientific Collaboration Network Analyzer</h3>
            <p>
              This dashboard provides a quick overview of researchers,
              publications, institutions, and collaborations available in the
              system.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
<div className="info-box">

<h3>Milestone 1 Status</h3>

<ul>

<li>✅ FastAPI Backend Completed</li>

<li>✅ PostgreSQL Connected</li>

<li>✅ Authentication Implemented</li>

<li>✅ Researcher Module Completed</li>

<li>✅ Dashboard Connected with Live API</li>

</ul>

</div>

export default Dashboard;