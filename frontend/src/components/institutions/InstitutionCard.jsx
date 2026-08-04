import { Link } from "react-router-dom";

function InstitutionCard({ institution, onDelete }) {
  return (
    <div className="card shadow-sm h-100 border-0">

      <div className="card-body">

        <h4 className="card-title text-primary">
          {institution.name}
        </h4>

        <p className="text-muted">
          {institution.abbreviation || "N/A"}
        </p>

        <hr />

        <p className="mb-2">
          <strong>Website</strong>
          <br />
          {institution.website ? (
            <a
              href={institution.website}
              target="_blank"
              rel="noopener noreferrer"
            >
              {institution.website}
            </a>
          ) : (
            "Not Available"
          )}
        </p>

        <p className="mb-2">
          <strong>Email</strong>
          <br />
          {institution.email || "Not Available"}
        </p>

        <p className="mb-2">
          <strong>Phone</strong>
          <br />
          {institution.phone || "Not Available"}
        </p>

        <p className="mb-2">
          <strong>Address</strong>
          <br />
          {institution.address || "Not Available"}
        </p>

        <p className="mb-3">
          <strong>Location</strong>
          <br />
          {[institution.city, institution.state, institution.country]
            .filter(Boolean)
            .join(", ") || "Not Available"}
        </p>

      </div>

      <div className="card-footer bg-white border-0">

        <div className="d-grid gap-2">

          <Link
            to={`/institutions/${institution.id}`}
            className="btn btn-outline-primary"
          >
            View Details
          </Link>

          <Link
            to={`/institutions/edit/${institution.id}`}
            className="btn btn-warning"
          >
            Edit
          </Link>

          <button
            type="button"
            className="btn btn-danger"
            onClick={() => onDelete(institution.id)}
          >
            Delete
          </button>

        </div>

      </div>

    </div>
  );
}

export default InstitutionCard;
