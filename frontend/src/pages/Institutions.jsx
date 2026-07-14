import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import Footer from "../components/Footer";
import api from "../services/api";

import "../styles/institutions.css";

function Institutions() {

  const [institutions, setInstitutions] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {

    api
      .get("/institutions/")
      .then((res) => {
        setInstitutions(res.data);
      })
      .catch((err) => {
        console.error(err);
      })
      .finally(() => {
        setLoading(false);
      });

  }, []);

  const filteredInstitutions = institutions.filter((item) => {

    const institution = (item.institution_name || "").toLowerCase();
    const country = (item.country || "").toLowerCase();
    const city = (item.city || "").toLowerCase();

    return (
      institution.includes(search.toLowerCase()) ||
      country.includes(search.toLowerCase()) ||
      city.includes(search.toLowerCase())
    );

  });

  if (loading) {

    return (

      <>
        <Navbar />

        <div className="dashboard-container">

          <Sidebar />

          <div className="institutions-content">

            <div className="loading-container">

              <div className="spinner"></div>

              <div className="loading-text">
                Loading Institutions...
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

        <div className="institutions-content">

          <h2>
            🏫 Institutions ({filteredInstitutions.length})
          </h2>

          <input
            type="text"
            className="search-box"
            placeholder="🔍 Search by Institution, Country or City..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />

          <table className="institutions-table">

            <thead>

              <tr>
                <th>ID</th>
                <th>Institution</th>
                <th>Country</th>
                <th>City</th>
                <th>Website</th>
                <th>Established</th>
              </tr>

            </thead>

            <tbody>

              {filteredInstitutions.length > 0 ? (

                filteredInstitutions.map((item) => (

                  <tr key={item.id}>

                    <td>{item.id}</td>
                    <td>{item.institution_name || "-"}</td>
                    <td>{item.country || "-"}</td>
                    <td>{item.city || "-"}</td>

                    <td>

                      {item.website ? (
                        <a
                          href={item.website}
                          target="_blank"
                          rel="noreferrer"
                        >
                          Visit
                        </a>
                      ) : (
                        "-"
                      )}

                    </td>

                    <td>{item.established_year || "-"}</td>

                  </tr>

                ))

              ) : (

                <tr>

                  <td
                    colSpan="6"
                    style={{
                      textAlign: "center",
                      padding: "20px",
                      color: "#ef4444",
                      fontWeight: "bold",
                    }}
                  >
                    ❌ No Institutions Found
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

export default Institutions;