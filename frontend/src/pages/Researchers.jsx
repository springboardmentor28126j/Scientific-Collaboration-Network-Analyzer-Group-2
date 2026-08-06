import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import Footer from "../components/Footer";
import Pagination from "../components/Pagination";
import api from "../services/api";

import "../styles/researchers.css";

function Researchers() {

  const [researchers, setResearchers] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  const [currentPage, setCurrentPage] = useState(1);

  const researchersPerPage = 5;

  useEffect(() => {

    loadResearchers();

  }, []);

  const loadResearchers = async () => {

    try {

      const res = await api.get("/researchers/");

      setResearchers(res.data);

    }

    catch (err) {

      console.error(err);

    }

    finally {

      setLoading(false);

    }

  };

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

  const indexOfLastResearcher =
    currentPage * researchersPerPage;

  const indexOfFirstResearcher =
    indexOfLastResearcher - researchersPerPage;

  const currentResearchers =
    filteredResearchers.slice(
      indexOfFirstResearcher,
      indexOfLastResearcher
    );

  const totalPages = Math.ceil(
    filteredResearchers.length /
    researchersPerPage
  );

  const totalResearchers =
    filteredResearchers.length;

  const totalPublications =
    filteredResearchers.reduce(
      (sum, r) =>
        sum + (r.total_publications || 0),
      0
    );

  const averageHIndex =
    totalResearchers > 0
      ? (
          filteredResearchers.reduce(
            (sum, r) =>
              sum + (r.h_index || 0),
            0
          ) / totalResearchers
        ).toFixed(1)
      : 0;

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

          <div className="d-flex justify-content-between align-items-center mb-4">

            <div>

              <h2 className="fw-bold">

                👨‍🔬 Researchers

              </h2>

              <p className="text-muted mb-0">

                Manage and view researcher information.

              </p>

            </div>

          </div>

          {/* Summary Cards */}

          <div className="row mb-4">

            <div className="col-md-4">

              <div className="card shadow-sm border-0">

                <div className="card-body text-center">

                  <h6 className="text-muted">

                    Total Researchers

                  </h6>

                  <h2 className="fw-bold text-primary">

                    {totalResearchers}

                  </h2>

                </div>

              </div>

            </div>

            <div className="col-md-4">

              <div className="card shadow-sm border-0">

                <div className="card-body text-center">

                  <h6 className="text-muted">

                    Average H-Index

                  </h6>

                  <h2 className="fw-bold text-success">

                    {averageHIndex}

                  </h2>

                </div>

              </div>

            </div>

            <div className="col-md-4">

              <div className="card shadow-sm border-0">

                <div className="card-body text-center">

                  <h6 className="text-muted">

                    Total Publications

                  </h6>

                  <h2 className="fw-bold text-warning">

                    {totalPublications}

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
                placeholder="🔍 Search by Name, Email, Institution or Specialization..."
                value={search}
                onChange={(e) => {

                  setSearch(e.target.value);

                  setCurrentPage(1);

                }}
              />

            </div>

          </div>

          {/* Researchers Table */}

          <div className="card shadow border-0">

            <div className="card-body">

              <div className="table-responsive">

                <table className="table table-hover align-middle">

                  <thead className="table-primary">

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

                    {currentResearchers.length > 0 ? (

                      currentResearchers.map((researcher) => (

                        <tr key={researcher.id}>

                          <td>

                            <span className="badge bg-primary">

                              {researcher.id}

                            </span>

                          </td>

                          <td className="fw-semibold">

                            {researcher.full_name}

                          </td>

                          <td>

                            {researcher.email}

                          </td>

                          <td>

                            {researcher.institution || "-"}

                          </td>

                          <td>

                            {researcher.department || "-"}

                          </td>

                          <td>

                            <span className="badge bg-info text-dark">

                              {researcher.specialization || "-"}

                            </span>

                          </td>

                          <td>

                            <span className="badge bg-success">

                              {researcher.h_index ?? 0}

                            </span>

                          </td>

                          <td>

                            <span className="badge bg-warning text-dark">

                              {researcher.total_publications ?? 0}

                            </span>

                          </td>

                        </tr>

                      ))

                    ) : (

                      <tr>

                        <td
                          colSpan="8"
                          className="text-center text-danger fw-bold py-5"
                        >

                          ❌ No Researchers Found

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

export default Researchers;