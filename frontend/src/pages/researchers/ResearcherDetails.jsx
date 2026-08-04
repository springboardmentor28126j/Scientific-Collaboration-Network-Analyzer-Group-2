import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../../api/api";

function ResearcherDetails() {
  const { id } = useParams();
  const [researcher, setResearcher] = useState(null);

  useEffect(() => {
    fetchResearcher();
  }, []);

  const fetchResearcher = async () => {
    try {
      const token = localStorage.getItem("access_token");

      const response = await api.get(`/researchers/${id}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      setResearcher(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  if (!researcher) {
    return (
      <div className="container mt-5">
        <h3>Loading...</h3>
      </div>
    );
  }

  return (
    <div className="container mt-5">
      <div className="card shadow p-4">
        <h2>{researcher.first_name} {researcher.last_name}</h2>
        <hr />

        <p><strong>Bio:</strong> {researcher.bio}</p>
        <p><strong>Phone:</strong> {researcher.phone}</p>
        <p><strong>Experience:</strong> {researcher.experience} years</p>
        <p><strong>ORCID:</strong> {researcher.orcid}</p>
      </div>
    </div>
  );
}

export default ResearcherDetails;