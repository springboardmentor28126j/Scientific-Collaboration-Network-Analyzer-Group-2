import { Link} from "react-router-dom" 
import React, { useEffect, useState } from "react";
import api from "../api/api";

function Researchers() {
  const [researchers, setResearchers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchResearchers();
  }, []);

  const fetchResearchers = async () => {
    try {
      const token = localStorage.getItem("access_token");

      const response = await api.get("/researchers/", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      setResearchers(response.data);
    } catch (err) {
      console.error(err);
      setError("Failed to load researchers.");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container mt-5">
        <h3>Loading Researchers...</h3>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mt-5">
        <div className="alert alert-danger">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="container mt-5">
      <h2 className="text-primary mb-4">
        Researchers
      </h2>

      <div className="row">
        {researchers.map((researcher) => (
          <div
            className="col-md-4 mb-4"
            key={researcher.id}
          >
            <div className="card shadow h-100">
              <div className="card-body">

                <h5>{researcher.first_name} {researcher.last_name}</h5>

                <p>
                  <strong>Bio:</strong>
                  <br />
                  {researcher.bio}
                </p>

                <p>
                  <strong>Phone:</strong>
                  <br />
                  {researcher.phone}
                </p>

                <p>
                  <strong>Experience:</strong>
                  <br />
                  {researcher.experience} years
                </p>

                <p>
                  <strong>ORCID:</strong>
                  <br />
                  {researcher.orcid}
                </p>

                <Link
  to={`/researchers/${researcher.id}`}
  className="btn btn-primary"
>
  View
</Link>


              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Researchers;
