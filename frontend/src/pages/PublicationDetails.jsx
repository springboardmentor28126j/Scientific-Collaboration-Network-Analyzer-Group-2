import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";

import {
  getPublication,
  downloadPublication,
} from "../services/publicationService";

function PublicationDetails() {
  const { id } = useParams();

  const [publication, setPublication] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPublication();
  }, []);

  const loadPublication = async () => {
    try {
      const data = await getPublication(id);
      setPublication(data);
    } catch (err) {
      console.error(err);
      alert("Failed to load publication.");
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    try {
      const response = await downloadPublication(id);

      const url = window.URL.createObjectURL(
        new Blob([response.data])
      );

      const link = document.createElement("a");

      link.href = url;
      link.download =
        publication.file_name || "publication.pdf";

      document.body.appendChild(link);

      link.click();

      document.body.removeChild(link);

      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
      alert("Download failed.");
    }
  };

  if (loading) {
    return (
      <div className="container mt-5">
        <h3>Loading...</h3>
      </div>
    );
  }

  if (!publication) {
    return (
      <div className="container mt-5">
        <div className="alert alert-danger">
          Publication not found.
        </div>
      </div>
    );
  }

  return (
    <div className="container mt-5">

      <div className="card shadow">

        <div className="card-body">

          <h2 className="text-primary mb-4">
            {publication.title}
          </h2>

          <table className="table table-bordered">

            <tbody>

              <tr>
                <th>Abstract</th>
                <td>{publication.abstract}</td>
              </tr>

              <tr>
                <th>DOI</th>
                <td>{publication.doi}</td>
              </tr>

              <tr>
                <th>Journal</th>
                <td>{publication.journal}</td>
              </tr>

              <tr>
                <th>Conference</th>
                <td>{publication.conference}</td>
              </tr>

              <tr>
                <th>Publication Year</th>
                <td>{publication.publication_year}</td>
              </tr>

              <tr>
                <th>Publication Type</th>
                <td>{publication.publication_type}</td>
              </tr>

              <tr>
                <th>Status</th>
                <td>{publication.status}</td>
              </tr>

              <tr>
                <th>Citation Count</th>
                <td>{publication.citation_count}</td>
              </tr>

              <tr>
                <th>URL</th>
                <td>
                  <a
                    href={publication.url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    {publication.url}
                  </a>
                </td>
              </tr>

              <tr>
                <th>Uploaded File</th>
                <td>{publication.file_name}</td>
              </tr>

              <tr>
                <th>Created At</th>
                <td>{publication.created_at}</td>
              </tr>

              <tr>
                <th>Updated At</th>
                <td>{publication.updated_at}</td>
              </tr>

            </tbody>

          </table>

          <button
            className="btn btn-success me-2"
            onClick={handleDownload}
          >
            Download PDF
          </button>

          <Link
            to={`/publications/edit/${publication.id}`}
            className="btn btn-warning me-2"
          >
            Edit
          </Link>

          <Link
            to="/publications"
            className="btn btn-secondary"
          >
            Back
          </Link>

        </div>

      </div>

    </div>
  );
}

export default PublicationDetails;
