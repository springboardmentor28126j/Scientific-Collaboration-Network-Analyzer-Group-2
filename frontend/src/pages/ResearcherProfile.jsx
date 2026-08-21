import { Link } from "react-router-dom";

function ResearcherProfile() {
  return (
    <div
      style={{
        maxWidth: "700px",
        margin: "50px auto",
        padding: "30px",
        border: "1px solid #ddd",
        borderRadius: "10px",
        backgroundColor: "#fff",
        boxShadow: "0 2px 8px rgba(0,0,0,0.1)"
      }}
    >
      <h1 style={{ textAlign: "center", color: "#2563eb" }}>
        Researcher Profile
      </h1>

      <hr />

      <h3>Name</h3>
      <p>Selected Researcher</p>

      <h3>Email</h3>
      <p>researcher@example.com</p>

      <h3>Institution</h3>
      <p>Institution Name</p>

      <h3>Department</h3>
      <p>Department Name</p>

      <h3>Country</h3>
      <p>Country Name</p>

      <div style={{ marginTop: "30px" }}>
        <Link
          to="/researchers"
          style={{
            textDecoration: "none",
            background: "#2563eb",
            color: "white",
            padding: "10px 20px",
            borderRadius: "6px"
          }}
        >
          ← Back to Researchers
        </Link>
      </div>
    </div>
  );
}

export default ResearcherProfile;