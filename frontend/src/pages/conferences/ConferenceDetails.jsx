import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import {
  getConference,
  deleteConference,
} from "../../services/conferenceService";

import { isAdmin } from "../../utils/auth";

function ConferenceDetails() {
  const { id } = useParams();
  const navigate = useNavigate();

  const admin = isAdmin();

  const [conference, setConference] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchConference();
  }, []);

  const fetchConference = async () => {
    try {
      setLoading(true);

      const data = await getConference(id);

      setConference(data);
    } catch (err) {
      console.error(err);
      setError("Unable to load conference details.");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    const confirmDelete = window.confirm(
      "Are you sure you want to delete this conference?"
    );

    if (!confirmDelete) return;

    try {
      await deleteConference(id);

      alert("Conference deleted successfully.");

      navigate("/conferences");
    } catch (err) {
      console.error(err);
      alert("Failed to delete conference.");
    }
  };

  const handleJoin = () => {
    alert(
      "Join Conference feature will be connected to the backend."
    );
  };

  const formatDate = (date) => {
    if (!date) return "N/A";

    try {
      return new Date(date).toLocaleDateString();
    } catch {
      return date;
    }
  };

  if (loading) {
    return (
      <div className="container mt-5 text-center">
        <div
          className="spinner-border text-primary"
          role="status"
        ></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mt-5">
        <div className="alert alert-danger">
          {error}
        </div>

        <Link
          to="/conferences"
          className="btn btn-secondary"
        >
          Back
        </Link>
      </div>
    );
  }

  return (
    <div className="container mt-4">

      <div className="card shadow">

        <div className="card-header bg-primary text-white">
          <h3 className="mb-0">
            {conference.title}
          </h3>
        </div>

        <div className="card-body">

          <div className="mb-3">
            <h5>Location</h5>
            <p>{conference.location}</p>
          </div>

          <div className="mb-3">
            <h5>Conference Date</h5>
            <p>{formatDate(conference.conference_date)}</p>
          </div>

          <div className="mb-4">
            <h5>Description</h5>
            <p>{conference.description}</p>
          </div>

        </div>

        <div className="card-footer">

          <div className="d-flex flex-wrap gap-2">

            <Link
              to="/conferences"
              className="btn btn-secondary"
            >
              Back
            </Link>

            {admin && (
              <Link
                to={`/conferences/edit/${conference.id}`}
                className="btn btn-warning"
              >
                Edit
              </Link>
            )}

            <button
              className="btn btn-success"
              onClick={handleJoin}
            >
              Join Conference
            </button>

            {admin && (
              <button
                className="btn btn-danger"
                onClick={handleDelete}
              >
                Delete
              </button>
            )}

          </div>

        </div>

      </div>

    </div>
  );
}

export default ConferenceDetails;
