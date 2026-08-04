import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {
  getInstitutions,
  deleteInstitution,
} from "../../services/institutionService";

import InstitutionCard from "../../components/institutions/InstitutionCard";
import InstitutionSearch from "../../components/institutions/InstitutionSearch";
import InstitutionPagination from "../../components/institutions/InstitutionPagination";

function Institutions() {
  const [institutions, setInstitutions] = useState([]);
  const [filteredInstitutions, setFilteredInstitutions] = useState([]);

  const [loading, setLoading] = useState(true);

  const [search, setSearch] = useState("");

  const [currentPage, setCurrentPage] = useState(1);

  const institutionsPerPage = 6;

  useEffect(() => {
    fetchInstitutions();
  }, []);

  useEffect(() => {
    const filtered = institutions.filter((institution) =>
      institution.name
        ?.toLowerCase()
        .includes(search.toLowerCase())
    );

    setFilteredInstitutions(filtered);
    setCurrentPage(1);
  }, [search, institutions]);

  const fetchInstitutions = async () => {
    try {
      setLoading(true);

      const data = await getInstitutions();

      setInstitutions(data);
      setFilteredInstitutions(data);
    } catch (error) {
      console.error(error);
      alert("Failed to load institutions.");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this institution?"
    );

    if (!confirmed) return;

    try {
      await deleteInstitution(id);

      fetchInstitutions();
    } catch (error) {
      console.error(error);
      alert("Failed to delete institution.");
    }
  };

  const indexOfLastInstitution =
    currentPage * institutionsPerPage;

  const indexOfFirstInstitution =
    indexOfLastInstitution - institutionsPerPage;

  const currentInstitutions =
    filteredInstitutions.slice(
      indexOfFirstInstitution,
      indexOfLastInstitution
    );

  return (
    <div className="container mt-4">

      <div className="d-flex justify-content-between align-items-center mb-4">

        <h2>Institution Management</h2>

        <Link
          to="/institutions/create"
          className="btn btn-primary"
        >
          + Create Institution
        </Link>

      </div>

      <InstitutionSearch
        search={search}
        setSearch={setSearch}
      />

      {loading ? (

        <div className="text-center mt-5">

          <div
            className="spinner-border text-primary"
            role="status"
          />

        </div>

      ) : currentInstitutions.length === 0 ? (

        <div className="alert alert-warning mt-4">
          No institutions found.
        </div>

      ) : (

        <div className="row">

          {currentInstitutions.map((institution) => (

            <div
              key={institution.id}
              className="col-md-6 col-lg-4 mb-4"
            >
              <InstitutionCard
                institution={institution}
                onDelete={handleDelete}
              />
            </div>

          ))}

        </div>

      )}

      <InstitutionPagination
        totalItems={filteredInstitutions.length}
        itemsPerPage={institutionsPerPage}
        currentPage={currentPage}
        paginate={setCurrentPage}
      />

    </div>
  );
}

export default Institutions;
