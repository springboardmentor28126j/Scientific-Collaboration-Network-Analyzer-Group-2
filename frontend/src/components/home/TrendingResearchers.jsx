import { Link } from "react-router-dom";

export default function TrendingResearchers({ researchers = [] }) {
  return (
    <section className="container py-5">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2 className="fw-bold">🔥 Trending Researchers</h2>

        <Link
          to="/researchers"
          className="btn btn-outline-primary"
        >
          View All
        </Link>
      </div>

      <div className="row g-4">
        {researchers.length === 0 ? (
          <div className="col-12">
            <div className="text-center text-muted py-5">
              <h5>No researchers found.</h5>
            </div>
          </div>
        ) : (
          researchers.map((researcher) => (
            <div
              className="col-lg-4 col-md-6"
              key={researcher.id}
            >
              <div
                className="card border-0 shadow-lg h-100"
                style={{
                  borderRadius: "20px",
                  transition: "0.3s ease",
                }}
              >
                <div className="card-body text-center p-4">
                  <img
                    src={`https://ui-avatars.com/api/?name=${encodeURIComponent(
                      researcher.name || "Researcher"
                    )}&background=1565C0&color=ffffff&size=200`}
                    alt={researcher.name}
                    className="rounded-circle mb-3 shadow"
                    width="90"
                    height="90"
                  />

                  <h4 className="fw-bold mb-2">
                    {researcher.name}
                  </h4>

                  <p className="text-muted mb-2">
                    {researcher.department || "Research Department"}
                  </p>

                  <span className="badge bg-primary mb-4 px-3 py-2">
                    {researcher.institution_name || "Unknown Institution"}
                  </span>

                  <div className="row text-center mb-4">
                    <div className="col-4">
                      <h5 className="fw-bold text-primary mb-1">
                        {researcher.publication_count ?? 0}
                      </h5>
                      <small className="text-muted">
                        Papers
                      </small>
                    </div>

                    <div className="col-4">
                      <h5 className="fw-bold text-success mb-1">
                        {researcher.experience ?? 0}
                      </h5>
                      <small className="text-muted">
                        Years
                      </small>
                    </div>

                    <div className="col-4">
                      <h5 className="fw-bold text-warning mb-1">
                        ⭐
                      </h5>
                      <small className="text-muted">
                        Trending
                      </small>
                    </div>
                  </div>

                  <Link
                    to={`/researchers/${researcher.id}`}
                    className="btn btn-primary w-100"
                  >
                    View Profile
                  </Link>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </section>
  );
}
