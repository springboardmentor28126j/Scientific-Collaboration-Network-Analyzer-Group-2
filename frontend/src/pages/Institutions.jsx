import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import Footer from "../components/Footer";
import Pagination from "../components/Pagination";
import api from "../services/api";

import "../styles/institutions.css";

function Institutions() {

  const [institutions, setInstitutions] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  const [currentPage, setCurrentPage] = useState(1);

  const institutionsPerPage = 5;

  useEffect(() => {

    loadInstitutions();

  }, []);

  const loadInstitutions = async () => {

    try {

      const res = await api.get("/institutions/");

      setInstitutions(res.data);

    }

    catch (err) {

      console.error(err);

    }

    finally {

      setLoading(false);

    }

  };

  const filteredInstitutions = institutions.filter((item) => {

    const institution =
      (item.institution_name || "").toLowerCase();

    const country =
      (item.country || "").toLowerCase();

    const city =
      (item.city || "").toLowerCase();

    return (

      institution.includes(search.toLowerCase()) ||

      country.includes(search.toLowerCase()) ||

      city.includes(search.toLowerCase())

    );

  });

  const indexOfLastInstitution =
    currentPage * institutionsPerPage;

  const indexOfFirstInstitution =
    indexOfLastInstitution - institutionsPerPage;

  const currentInstitutions =
    filteredInstitutions.slice(
      indexOfFirstInstitution,
      indexOfLastInstitution
    );

  const totalPages = Math.ceil(
    filteredInstitutions.length /
      institutionsPerPage
  );

  const totalInstitutions =
    filteredInstitutions.length;

  const totalCountries =
    new Set(
      filteredInstitutions.map((i) => i.country)
    ).size;

  const totalCities =
    new Set(
      filteredInstitutions.map((i) => i.city)
    ).size;

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

          <div className="d-flex justify-content-between align-items-center mb-4">

            <div>

              <h2 className="fw-bold">

                🏫 Institutions

              </h2>

              <p className="text-muted mb-0">

                Browse institutions participating in the Scientific Collaboration Network.

              </p>

            </div>

          </div>

          {/* Summary Cards */}

          <div className="row mb-4">

            <div className="col-md-4">

              <div className="card shadow-sm border-0">

                <div className="card-body text-center">

                  <h6 className="text-muted">

                    Total Institutions

                  </h6>

                  <h2 className="fw-bold text-primary">

                    {totalInstitutions}

                  </h2>

                </div>

              </div>

            </div>

            <div className="col-md-4">

              <div className="card shadow-sm border-0">

                <div className="card-body text-center">

                  <h6 className="text-muted">

                    Countries

                  </h6>

                  <h2 className="fw-bold text-success">

                    {totalCountries}

                  </h2>

                </div>

              </div>

            </div>

            <div className="col-md-4">

              <div className="card shadow-sm border-0">

                <div className="card-body text-center">

                  <h6 className="text-muted">

                    Cities

                  </h6>

                  <h2 className="fw-bold text-warning">

                    {totalCities}

                  </h2>

                </div>

              </div>

            </div>

          </div>
                    {/* Search */}

          <div className="card shadow-sm border-0 mb-4">

            <div className="card-body">

              <input
                type="text"
                className="form-control form-control-lg"
                placeholder="🔍 Search by Institution, Country or City..."
                value={search}
                onChange={(e) => {

                  setSearch(e.target.value);

                  setCurrentPage(1);

                }}
              />

            </div>

          </div>

          {/* Institutions Table */}

          <div className="card shadow border-0">

            <div className="card-body">

              <div className="table-responsive">

                <table className="table table-hover align-middle">

                  <thead className="table-primary">

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

                    {currentInstitutions.length > 0 ? (

                      currentInstitutions.map((item) => (

                        <tr key={item.id}>

                          <td>

                            <span className="badge bg-primary">

                              {item.id}

                            </span>

                          </td>

                          <td className="fw-semibold">

                            {item.institution_name || "-"}

                          </td>

                          <td>

                            <span className="badge bg-success">

                              {item.country || "-"}

                            </span>

                          </td>

                          <td>

                            {item.city || "-"}

                          </td>

                          <td>

                            {item.website ? (

                              <a
                                href={item.website}
                                target="_blank"
                                rel="noreferrer"
                                className="btn btn-sm btn-outline-primary"
                              >

                                Visit

                              </a>

                            ) : (

                              <span className="text-muted">

                                -

                              </span>

                            )}

                          </td>

                          <td>

                            <span className="badge bg-warning text-dark">

                              {item.established_year || "-"}

                            </span>

                          </td>

                        </tr>

                      ))

                    ) : (

                      <tr>

                        <td
                          colSpan="6"
                          className="text-center text-danger fw-bold py-5"
                        >

                          ❌ No Institutions Found

                        </td>

                      </tr>

                    )}

                  </tbody>

                </table>

              </div>

              <div className="d-flex justify-content-center mt-4">

                <Pagination
                  currentPage={currentPage}
                  totalPages={totalPages}
                  onPageChange={setCurrentPage}
                />

              </div>

            </div>

          </div>

        </div>

      </div>

      <Footer />

    </>

  );

}

export default Institutions;