import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import Footer from "../components/Footer";
import api from "../services/api";

import "../styles/researchers.css";

function Researchers() {
  const [researchers, setResearchers] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get("/researchers/")
      .then((res) => {
        setResearchers(res.data);
      })
      .catch((err) => {
        console.error(err);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const filteredResearchers = researchers.filter((researcher) => {
    const fullName = (researcher.full_name || "").toLowerCase();
    const email = (researcher.email || "").toLowerCase();
    const institution = (researcher.institution || "").toLowerCase();
    const specialization = (researcher.specialization || "").toLowerCase();

    return (
      fullName.includes(search.toLowerCase()) ||
      email.includes(search.toLowerCase()) ||
      institution.includes(search.toLowerCase()) ||
      specialization.includes(search.toLowerCase())
    );
  });

  if (loading) {
  return (
    <>
      <Navbar />

      <div className="dashboard-container">
        <Sidebar />

        <div className="researchers-content">

          <div className="loading-container">

            <div className="spinner"></div>

            <div className="loading-text">
              Loading Researchers...
            </div>

          </div>

        </div>
      </div>

      <Footer />
    </>
  );
}

  return (
    <>
      <Navbar />

      <div className="dashboard-container">
        <Sidebar />

        <div className="researchers-content">
          <h2>👨‍🔬 Researchers ({filteredResearchers.length})</h2>

          <input
            type="text"
            className="search-box"
            placeholder="🔍 Search by Name, Email, Institution or Specialization..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />

          <table className="researchers-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Institution</th>
                <th>Department</th>
                <th>Specialization</th>
                <th>H-Index</th>
                <th>Publications</th>
              </tr>
            </thead>

            <tbody>
              {filteredResearchers.length > 0 ? (
                filteredResearchers.map((researcher) => (
                  <tr key={researcher.id}>
                    <td>{researcher.id}</td>
                    <td>{researcher.full_name}</td>
                    <td>{researcher.email}</td>
                    <td>{researcher.institution || "-"}</td>
                    <td>{researcher.department || "-"}</td>
                    <td>{researcher.specialization || "-"}</td>
                    <td>{researcher.h_index ?? "-"}</td>
                    <td>{researcher.total_publications ?? "-"}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td
                    colSpan="8"
                    style={{
                      textAlign: "center",
                      padding: "20px",
                      color: "#ef4444",
                      fontWeight: "bold",
                    }}
                  >
                    ❌ No Researchers Found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <Footer />
    </>
  );
}

export default Researchers;