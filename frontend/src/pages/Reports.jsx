import { useEffect, useState } from "react";

function Reports() {
  const [reportData, setReportData] = useState({
    researchers: 0,
    publications: 0,
    collaborations: 0,
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchReports = async () => {
      try {
        const response = await fetch(
          "http://127.0.0.1:8000/reports/"
        );

        if (!response.ok) {
          throw new Error("Failed to fetch reports");
        }

        const data = await response.json();
        setReportData(data);
      } catch {
        setError("Unable to load report data");
      } finally {
        setLoading(false);
      }
    };

    fetchReports();
  }, []);

  return (
    <div
      style={{
        padding: "40px",
        minHeight: "100vh",
        backgroundColor: "#f4f8fc",
      }}
    >
      <h1
        style={{
          color: "#1f4e9e",
          marginBottom: "10px",
        }}
      >
        Reports
      </h1>

      <p
        style={{
          fontSize: "18px",
          color: "#555",
          marginBottom: "30px",
        }}
      >
        Generate and view reports related to the Scientific Collaboration
        Network.
      </p>

      {loading && <p>Loading report data...</p>}

      {error && (
        <p style={{ color: "red" }}>
          {error}
        </p>
      )}

      {!loading && !error && (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(3, 1fr)",
            gap: "20px",
          }}
        >
          {/* Publication Report */}
          <div
            style={{
              padding: "25px",
              border: "1px solid #ddd",
              borderRadius: "10px",
              backgroundColor: "white",
              boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
            }}
          >
            <h2>Publication Report</h2>

            <h3
              style={{
                fontSize: "36px",
                color: "#1f73c9",
              }}
            >
              {reportData.publications}
            </h3>

            <p>Number of publications in the system.</p>
          </div>

          {/* Researcher Report */}
          <div
            style={{
              padding: "25px",
              border: "1px solid #ddd",
              borderRadius: "10px",
              backgroundColor: "white",
              boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
            }}
          >
            <h2>Researcher Report</h2>

            <h3
              style={{
                fontSize: "36px",
                color: "#1f73c9",
              }}
            >
              {reportData.researchers}
            </h3>

            <p>Number of researchers in the system.</p>
          </div>

          {/* Collaboration Report */}
          <div
            style={{
              padding: "25px",
              border: "1px solid #ddd",
              borderRadius: "10px",
              backgroundColor: "white",
              boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
            }}
          >
            <h2>Collaboration Report</h2>

            <h3
              style={{
                fontSize: "36px",
                color: "#1f73c9",
              }}
            >
              {reportData.collaborations}
            </h3>

            <p>Number of collaborations in the system.</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default Reports;