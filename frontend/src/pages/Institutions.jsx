import React, { useEffect, useState } from "react";
import api from "../api/api";

function Institutions() {
  const [institutions, setInstitutions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchInstitutions();
  }, []);

  const fetchInstitutions = async () => {
    try {
      const response = await api.get("/institutions/");
      setInstitutions(response.data);
    } catch (err) {
      console.error(err);
      setError("Failed to load institutions.");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container mt-5">
        <h3>Loading Institutions...</h3>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mt-5">
        <div className="alert alert-danger">{error}</div>
      </div>
    );
  }

  return (
    <div className="container mt-5">
      <h2 className="text-primary mb-4">Institutions</h2>

      <div className="row">
        {institutions.map((institution) => (
          <div
            className="col-lg-4 col-md-6 mb-4"
            key={institution.id}
          >
            <div className="card shadow h-100">
              <div className="card-body">

                <h4 className="card-title">
                  {institution.name}
                </h4>

                <hr />

                <p>
                  <strong>Abbreviation:</strong><br />
                  {institution.abbreviation}
                </p>

                <p>
                  <strong>Email:</strong><br />
                  {institution.email}
                </p>

                <p>
                  <strong>Phone:</strong><br />
                  {institution.phone}
                </p>

                <p>
                  <strong>Website:</strong><br />
                  <a
                    href={`https://${institution.website}`}
                    target="_blank"
                    rel="noreferrer"
                  >
                    {institution.website}
                  </a>
                </p>

                <p>
                  <strong>Address:</strong><br />
                  {institution.address}
                </p>

                <p>
                  <strong>Location:</strong><br />
                  {institution.city}, {institution.state}
                </p>

                <p>
                  <strong>Country:</strong><br />
                  {institution.country}
                </p>

                <button className="btn btn-primary w-100">
                  View Details
                </button>

              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Institutions;
