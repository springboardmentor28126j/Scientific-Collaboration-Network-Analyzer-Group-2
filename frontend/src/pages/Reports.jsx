function Reports() {
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

          <p>
            View publication-related information and statistics.
          </p>

          <button
            style={{
              padding: "10px 20px",
              border: "none",
              borderRadius: "6px",
              backgroundColor: "#1f73c9",
              color: "white",
              cursor: "pointer",
            }}
          >
            Generate Report
          </button>
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

          <p>
            View researcher-related information and statistics.
          </p>

          <button
            style={{
              padding: "10px 20px",
              border: "none",
              borderRadius: "6px",
              backgroundColor: "#1f73c9",
              color: "white",
              cursor: "pointer",
            }}
          >
            Generate Report
          </button>
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

          <p>
            View collaboration-related information and statistics.
          </p>

          <button
            style={{
              padding: "10px 20px",
              border: "none",
              borderRadius: "6px",
              backgroundColor: "#1f73c9",
              color: "white",
              cursor: "pointer",
            }}
          >
            Generate Report
          </button>
        </div>
      </div>
    </div>
  );
}

export default Reports;