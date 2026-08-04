import { Link } from "react-router-dom";

export default function SearchCard({
  id,
  type,
  title,
  subtitle,
  badge,
  description,
}) {

  const getLink = () => {
    switch (type) {
      case "researcher":
        return `/researchers/${id}`;

      case "publication":
        return `/publications/${id}`;

      case "institution":
        return `/institutions/${id}`;

      default:
        return "#";
    }
  };

  return (
    <div
      className="card shadow-sm border-0 mb-3"
      style={{
        borderRadius: "18px",
      }}
    >
      <div className="card-body">

        <div className="d-flex justify-content-between">

          <div>

            <h4 className="fw-bold">
              {title}
            </h4>

            {subtitle && (
              <p className="text-muted mb-2">
                {subtitle}
              </p>
            )}

            {badge && (
              <span className="badge bg-primary mb-3">
                {badge}
              </span>
            )}

            <p className="text-secondary">
              {description}
            </p>

          </div>

          <div className="text-end">

            <Link
              to={getLink()}
              className="btn btn-primary"
            >
              View
            </Link>

          </div>

        </div>

      </div>
    </div>
  );
}
