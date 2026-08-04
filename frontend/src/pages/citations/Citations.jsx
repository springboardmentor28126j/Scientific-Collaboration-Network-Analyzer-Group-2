import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {
  getCitations,
  deleteCitation,
  exportBibtex,
} from "../../services/citationService";

import CitationCard from "../../components/citations/CitationCard";
import CitationSearch from "../../components/citations/CitationSearch";
import CitationPagination from "../../components/citations/CitationPagination";

import {
  isSystemAdmin,
  isInstitutionAdmin,
} from "../../utils/auth";

function Citations() {

  const [citations, setCitations] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [currentPage, setCurrentPage] = useState(1);

  const citationsPerPage = 6;

  const canManage =
    isSystemAdmin() || isInstitutionAdmin();

  useEffect(() => {
    fetchCitations();
  }, []);

  useEffect(() => {
    const results = citations.filter((citation) =>
      citation.title
        ?.toLowerCase()
        .includes(search.toLowerCase())
    );

    setFiltered(results);
    setCurrentPage(1);

  }, [search, citations]);

  const fetchCitations = async () => {
    try {

      setLoading(true);

      const data = await getCitations();

      setCitations(data);
      setFiltered(data);

    } catch (err) {

      console.error(err);
      alert("Unable to load citations.");

    } finally {

      setLoading(false);

    }
  };

  const handleDelete = async (id) => {

    if (!window.confirm("Delete this citation?")) {
      return;
    }

    try {

      await deleteCitation(id);

      fetchCitations();

    } catch (err) {

      console.error(err);

      alert("Unable to delete citation.");

    }

  };

  const handleExportBibtex = async (id) => {

    try {

      const bibtex = await exportBibtex(id);

      const blob = new Blob(
        [bibtex],
        { type: "text/plain" }
      );

      const url = window.URL.createObjectURL(blob);

      const a = document.createElement("a");

      a.href = url;
      a.download = "citation.bib";

      a.click();

      window.URL.revokeObjectURL(url);

    } catch (err) {

      console.error(err);

      alert("Unable to export BibTeX.");

    }

  };

  const indexOfLast =
    currentPage * citationsPerPage;

  const indexOfFirst =
    indexOfLast - citationsPerPage;

  const currentCitations =
    filtered.slice(
      indexOfFirst,
      indexOfLast
    );

  return (

    <div className="container mt-4">

      <div className="d-flex justify-content-between align-items-center mb-4">

        <h2>Citation Management</h2>

        {canManage && (

          <Link
            to="/citations/create"
            className="btn btn-success"
          >
            + Add Citation
          </Link>

        )}

      </div>

      <CitationSearch
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

      ) : currentCitations.length === 0 ? (

        <div className="alert alert-warning mt-4">

          No citations found.

        </div>

      ) : (

        <>

          <div className="row">

            {currentCitations.map((citation) => (

              <div
                key={citation.id}
                className="col-md-6 col-lg-4 mb-4"
              >

                <CitationCard
                  citation={citation}
                  onDelete={handleDelete}
                  onExportBibtex={
                    handleExportBibtex
                  }
                />

              </div>

            ))}

          </div>

          <CitationPagination
            totalItems={filtered.length}
            itemsPerPage={citationsPerPage}
            currentPage={currentPage}
            paginate={setCurrentPage}
          />

        </>

      )}

    </div>

  );
}

export default Citations;
