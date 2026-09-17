import { useEffect, useState } from "react";
import "../css/analytics.css";

function Analytics() {
  const [analytics, setAnalytics] = useState({
    total_researchers: 0,
    total_publications: 0,
    total_collaborations: 0,
    total_conferences: 0,
  });

  useEffect(() => {
    fetch("http://127.0.0.1:8000/analytics/")
      .then((response) => response.json())
      .then((data) => {
        setAnalytics(data);
      })
      .catch((error) => {
        console.error("Error fetching analytics:", error);
      });
  }, []);

  return (
    <div className="analytics-page">
      <h1>Analytics Dashboard</h1>

      <div className="analytics-cards">

        <div className="analytics-card">
          <h2>Researchers</h2>
          <p>{analytics.total_researchers}</p>
        </div>

        <div className="analytics-card">
          <h2>Publications</h2>
          <p>{analytics.total_publications}</p>
        </div>

        <div className="analytics-card">
          <h2>Collaborations</h2>
          <p>{analytics.total_collaborations}</p>
        </div>

        <div className="analytics-card">
          <h2>Conferences</h2>
          <p>{analytics.total_conferences}</p>
        </div>

      </div>
    </div>
  );
}

export default Analytics;