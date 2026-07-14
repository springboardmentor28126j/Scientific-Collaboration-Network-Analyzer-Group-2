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

            <div className="card researchers-card">
              <h3>👨‍🔬 Researchers</h3>
              <h1>{dashboard.total_researchers}</h1>
            </div>

            <div className="card papers-card">
              <h3>📄 Research Papers</h3>
              <h1>{dashboard.total_papers}</h1>
            </div>

            <div className="card institutions-card">
              <h3>🏫 Institutions</h3>
              <h1>{dashboard.total_institutions}</h1>
            </div>

            <div className="card collaborations-card">
              <h3>🤝 Collaborations</h3>
              <h1>{dashboard.total_collaborations}</h1>
            </div>

          </div>

          <div className="welcome-box">

            <h3>
              🚀 Welcome to the Scientific Collaboration Network Analyzer
            </h3>

            <p>
              Explore researcher profiles, discover research publications,
              analyze institutional collaborations, and gain valuable insights
              through an intelligent research analytics platform.
            </p>

          </div>

          <div className="info-box">

            <h3>Platform Highlights</h3>

            <ul>

              <li>✅ Search researchers quickly using smart filtering.</li>

              <li>✅ Explore research papers with detailed publication information.</li>

              <li>✅ Browse institutions and their research profiles.</li>

              <li>✅ View collaboration statistics from the dashboard.</li>

              <li>✅ Secure login with JWT authentication.</li>

              <li>✅ Simple, responsive and user-friendly interface.</li>

            </ul>

          </div>

        </div>

      </div>

    </div>
  );
}

export default Dashboard;