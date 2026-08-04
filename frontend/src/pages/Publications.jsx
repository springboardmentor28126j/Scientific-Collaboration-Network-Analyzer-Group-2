import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {
  getPublications,
  downloadPublication,
  deletePublication,
} from "../services/publicationService";

function Publications() {
  const [publications, setPublications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadPublications();
  }, []);

  const loadPublications = async () => {
    try {
      const data = await getPublications();
      setPublications(data);
    } catch (err) {
      console.error(err);
      setError("Failed to load publications.");
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (id, fileName) => {
    try {
      const response = await downloadPublication(id);

      const url = window.URL.createObjectURL(
        new Blob([response.data])
      );

      const link = document.createElement("a");

      link.href = url;
      link.download = fileName || "publication.pdf";

      document.body.appendChild(link);
      link.click();

      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
      alert("Failed to download publication.");
    }
  };

  const handleDelete = async (id) => {
  const confirmed = window.confirm(
    "Are you sure you want to delete this publication?"
  );

  if (!confirmed) return;

  try {
    await deletePublication(id);

    alert("Publication deleted successfully.");

    // Refresh publication list
    setPublications((prev) =>
      prev.filter((publication) => publication.id !== id)
    );

  } catch (err) {
    console.error(err);

    alert(
      err.response?.data?.detail ||
      "Failed to delete publication."
    );
  }
};
  if (loading) {
    return (
      <div className="container mt-5">
        <h3>Loading Publications...</h3>
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

      <div className="d-flex justify-content-between align-items-center mb-4">

        <h2 className="text-primary">
          Publications
        </h2>

        <Link
          to="/publications/create"
          className="btn btn-success"
        >
          Add Publication
        </Link>

      </div>

      <div className="row">

        {publications.length === 0 ? (
          <div className="alert alert-info">
            No publications found.
          </div>
        ) : (
          publications.map((publication) => (

            <div
              className="col-lg-6 mb-4"
              key={publication.id}
            >
              <div className="card shadow h-100">

                <div className="card-body">

                  <h4 className="card-title">
                    {publication.title}
                  </h4>

                  <hr />

                  <p>
                    <strong>Abstract</strong>
                    <br />
                    {publication.abstract}
                  </p>

                  <p>
                    <strong>Conference</strong>
                    <br />
                    {publication.conference}
                  </p>

                  <p>
                    <strong>Journal</strong>
                    <br />
                    {publication.journal}
                  </p>

                  <p>
                    <strong>Publication Year</strong>
                    <br />
                    {publication.publication_year}
                  </p>

                  <p>
                    <strong>Publication Type</strong>
                    <br />
                    {publication.publication_type}
                  </p>

                  <p>
                    <strong>Status</strong>
                    <br />
                    {publication.status}
                  </p>

                  <p>
                    <strong>Citation Count</strong>
                    <br />
                    {publication.citation_count}
                  </p>

                  <p>
                    <strong>DOI</strong>
                    <br />
                    {publication.doi}
                  </p>

                  <div className="mt-3">

                    {publication.url && (
                      <a
                        href={publication.url}
                        target="_blank"
                        rel="noreferrer"
                        className="btn btn-outline-primary me-2 mb-2"
                      >
                        Open Link
                      </a>
                    )}

                    <Link
                      to={`/publications/${publication.id}`}
                      className="btn btn-primary me-2 mb-2"
                    >
                      View Details
                    </Link>

                    <button
                      className="btn btn-success me-2 mb-2"
                      onClick={() =>
                        handleDownload(
                          publication.id,
                          publication.file_name
                        )
                      }
                    >
                      Download PDF
                    </button>

                    <Link
                      to={`/publications/edit/${publication.id}`}
                      className="btn btn-warning me-2 mb-2"
                    >
                      Edit
                    </Link>

                    <button
                      className="btn btn-danger mb-2"
                      onClick={() =>
                        handleDelete(publication.id)
                      }
                    >
                      Delete
                    </button>

                  </div>

                </div>

              </div>
            </div>

          ))
        )}

      </div>

    </div>
  );
}

export default Publications;
