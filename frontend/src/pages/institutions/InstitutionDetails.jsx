import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import {
  getInstitution,
  deleteInstitution,
} from "../../services/institutionService";

function InstitutionDetails() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [institution, setInstitution] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchInstitution();
  }, []);

  const fetchInstitution = async () => {
    try {
      setLoading(true);

      const data = await getInstitution(id);

      setInstitution(data);
    } catch (err) {
      console.error(err);
      setError("Unable to load institution details.");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    const confirmDelete = window.confirm(
      "Are you sure you want to delete this institution?"
    );

    if (!confirmDelete) return;

    try {
      await deleteInstitution(id);

      alert("Institution deleted successfully.");

      navigate("/institutions");
    } catch (err) {
      console.error(err);
      alert("Failed to delete institution.");
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
          to="/institutions"
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
            {institution.name}
          </h3>

          <small>
            {institution.abbreviation}
          </small>
        </div>

        <div className="card-body">

          <div className="row">

            <div className="col-md-6 mb-3">
              <h5>Website</h5>

              {institution.website ? (
                <a
                  href={institution.website}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {institution.website}
                </a>
              ) : (
                <p>Not Available</p>
              )}
            </div>

            <div className="col-md-6 mb-3">
              <h5>Email</h5>
              <p>{institution.email || "Not Available"}</p>
            </div>

            <div className="col-md-6 mb-3">
              <h5>Phone</h5>
              <p>{institution.phone || "Not Available"}</p>
            </div>

            <div className="col-md-6 mb-3">
              <h5>Country</h5>
              <p>{institution.country || "Not Available"}</p>
            </div>

            <div className="col-md-6 mb-3">
              <h5>State</h5>
              <p>{institution.state || "Not Available"}</p>
            </div>

            <div className="col-md-6 mb-3">
              <h5>City</h5>
              <p>{institution.city || "Not Available"}</p>
            </div>

            <div className="col-12 mb-3">
              <h5>Address</h5>
              <p>{institution.address || "Not Available"}</p>
            </div>

          </div>

        </div>

        <div className="card-footer">

          <div className="d-flex flex-wrap gap-2">

            <Link
              to="/institutions"
              className="btn btn-secondary"
            >
              Back
            </Link>

            <Link
              to={`/institutions/edit/${institution.id}`}
              className="btn btn-warning"
            >
              Edit
            </Link>

            <button
              className="btn btn-danger"
              onClick={handleDelete}
            >
              Delete
            </button>

          </div>

        </div>

      </div>

    </div>
  );
}

export default InstitutionDetails;
