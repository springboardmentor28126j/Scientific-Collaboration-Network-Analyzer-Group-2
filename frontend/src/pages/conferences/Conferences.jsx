import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {
  getConferences,
  deleteConference,
} from "../../services/conferenceService";

import ConferenceSearch from "../../components/conferences/ConferenceSearch";
import ConferencePagination from "../../components/conferences/ConferencePagination";
import ConferenceCard from "../../components/conferences/ConferenceCard";

import {
  isSystemAdmin,
  isInstitutionAdmin,
} from "../../utils/auth";

function Conferences() {
  const [conferences, setConferences] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [currentPage, setCurrentPage] = useState(1);

  const conferencesPerPage = 6;

  const canManage =
    isSystemAdmin() || isInstitutionAdmin();

  useEffect(() => {
    fetchConferences();
  }, []);

  useEffect(() => {
    const results = conferences.filter((conference) =>
      conference.title
        ?.toLowerCase()
        .includes(search.toLowerCase())
    );

    setFiltered(results);
    setCurrentPage(1);
  }, [search, conferences]);

  const fetchConferences = async () => {
    try {
      setLoading(true);

      const data = await getConferences();

      setConferences(data);
      setFiltered(data);
    } catch (err) {
      console.error(err);
      alert("Unable to load conferences.");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this conference?")) {
      return;
    }

    try {
      await deleteConference(id);
      fetchConferences();
    } catch (err) {
      console.error(err);

      if (err.response?.data?.detail) {
        alert(err.response.data.detail);
      } else {
        alert("Failed to delete conference.");
      }
    }
  };

  const indexOfLast = currentPage * conferencesPerPage;
  const indexOfFirst = indexOfLast - conferencesPerPage;

  const currentConferences = filtered.slice(
    indexOfFirst,
    indexOfLast
  );

  return (
    <div className="container mt-4">

      <div className="d-flex justify-content-between align-items-center mb-4">

        <h2>Conference Management</h2>

        {canManage && (
          <Link
            to="/conferences/create"
            className="btn btn-success"
          >
            + Add Conference
          </Link>
        )}

      </div>

      <ConferenceSearch
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
      ) : currentConferences.length === 0 ? (
        <div className="alert alert-warning mt-4">
          No conferences found.
        </div>
      ) : (
        <>
          <div className="row">
            {currentConferences.map((conference) => (
              <div
                key={conference.id}
                className="col-md-6 col-lg-4 mb-4"
              >
                <ConferenceCard
                  conference={conference}
                  onDelete={handleDelete}
                />
              </div>
            ))}
          </div>

          <ConferencePagination
            totalItems={filtered.length}
            itemsPerPage={conferencesPerPage}
            currentPage={currentPage}
            paginate={setCurrentPage}
          />
        </>
      )}

    </div>
  );
}

export default Conferences;
