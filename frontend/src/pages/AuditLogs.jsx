import { useEffect, useState } from "react";
import DashboardNavbar from "../components/DashboardNavbar";
import Footer from "../components/Footer";
import api from "../services/api";

import "../styles/auditLogs.css";

function AuditLogs() {

  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  const [stats, setStats] = useState({
    total: 0,
    logins: 0,
    failed: 0,
    papers: 0
  });

  useEffect(() => {

    const fetchAuditLogs = async () => {

      try {

        const token = localStorage.getItem("token");

        const response = await api.get("/audit-logs/", {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });

        const data = response.data;

        setLogs(data);

        setStats({
          total: data.length,
          logins: data.filter(
            log => log.action === "LOGIN"
          ).length,

          failed: data.filter(
            log => log.action === "LOGIN_FAILED"
          ).length,

          papers: data.filter(
            log => log.action === "PAPER_CREATED"
          ).length
        });

      } catch (error) {

        console.error(
          "Failed to load audit logs:",
          error
        );

      } finally {

        setLoading(false);

      }

    };

    fetchAuditLogs();

  }, []);

  return (
    <>
      <DashboardNavbar />

      <div className="audit-container">

        {/* Header */}
        <div className="audit-header">

          <div>
            <h2>Audit Logs</h2>

            <p>
              Track user activity, security events and system actions.
            </p>
          </div>

        </div>


        {/* Summary Cards */}
        {!loading && (
          <div className="audit-stats">

            <div className="audit-stat-card">
              <span>Total Activities</span>
              <strong>{stats.total}</strong>
            </div>

            <div className="audit-stat-card">
              <span>Successful Logins</span>
              <strong>{stats.logins}</strong>
            </div>

            <div className="audit-stat-card">
              <span>Failed Attempts</span>
              <strong>{stats.failed}</strong>
            </div>

            <div className="audit-stat-card">
              <span>Papers Created</span>
              <strong>{stats.papers}</strong>
            </div>

          </div>
        )}


        {/* Loading */}
        {loading ? (

          <div className="audit-loading">
            Loading audit logs...
          </div>

        ) : logs.length === 0 ? (

          <div className="audit-empty">
            No audit logs available.
          </div>

        ) : (

          /* Audit Table */
          <div className="audit-table-wrapper">

            <table className="audit-table">

              <thead>

                <tr>
                  <th>ID</th>
                  <th>User ID</th>
                  <th>Action</th>
                  <th>Module</th>
                  <th>Description</th>
                  <th>Date & Time</th>
                </tr>

              </thead>

              <tbody>

                {logs.map((log) => (

                  <tr key={log.id}>

                    <td>
                      {log.id}
                    </td>

                    <td>
                      {log.user_id}
                    </td>

                    <td>

                      <span
                        className={`audit-action ${log.action
                          .toLowerCase()
                          .replace(/_/g, "-")}`}
                      >
                        {log.action}
                      </span>

                    </td>

                    <td>
                      {log.module}
                    </td>

                    <td>
                      {log.description}
                    </td>

                    <td>
                      {new Date(
                        log.created_at
                      ).toLocaleString()}
                    </td>

                  </tr>

                ))}

              </tbody>

            </table>

          </div>

        )}

      </div>

      <Footer />
    </>
  );
}

export default AuditLogs;