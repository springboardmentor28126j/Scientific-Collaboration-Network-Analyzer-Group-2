import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import {
  getCitation,
  exportBibtex,
} from "../../services/citationService";

function CitationDetails() {

  const { id } = useParams();

  const [citation, setCitation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchCitation();
  }, []);

  const fetchCitation = async () => {
    try {
      setLoading(true);

      const data = await getCitation(id);

      setCitation(data);
    } catch (err) {
      console.error(err);
      setError("Unable to load citation.");
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      const bibtex = await exportBibtex(id);

      const blob = new Blob(
        [bibtex],
        {
          type: "text/plain",
        }
      );

      const url = window.URL.createObjectURL(blob);

      const a = document.createElement("a");

      a.href = url;
      a.download = "citation.bib";

      a.click();

      window.URL.revokeObjectURL(url);

    } catch (err) {
      console.error(err);
      alert("Unable to export BibTeX.");
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
      </div>
    );
  }

  return (

    <div className="container mt-4">

      <div className="card shadow">

        <div className="card-header bg-primary text-white">
          <h3 className="mb-0">
            Citation Details
          </h3>
        </div>

        <div className="card-body">

          <h4 className="text-primary">
            {citation.title}
          </h4>

          <hr />

          <p>
            <strong>Authors</strong><br />
            {citation.authors}
          </p>

          <p>
            <strong>Journal</strong><br />
            {citation.journal || "N/A"}
          </p>

          <p>
            <strong>Year</strong><br />
            {citation.year}
          </p>

          <p>
            <strong>Volume</strong><br />
            {citation.volume || "N/A"}
          </p>

          <p>
            <strong>Issue</strong><br />
            {citation.issue || "N/A"}
          </p>

          <p>
            <strong>Pages</strong><br />
            {citation.pages || "N/A"}
          </p>

          <p>
            <strong>DOI</strong><br />
            {citation.doi ? (
              <a
                href={`https://doi.org/${citation.doi}`}
                target="_blank"
                rel="noreferrer"
              >
                {citation.doi}
              </a>
            ) : (
              "N/A"
            )}
          </p>

          <p>
            <strong>URL</strong><br />
            {citation.url ? (
              <a
                href={citation.url}
                target="_blank"
                rel="noreferrer"
              >
                {citation.url}
              </a>
            ) : (
              "N/A"
            )}
          </p>

          <p>
            <strong>Citation Style</strong><br />

            <span className="badge bg-success">
              {citation.citation_style}
            </span>
          </p>

          <div className="mt-4">

            <label className="form-label">
              Formatted Citation
            </label>

            <div className="border rounded p-3 bg-light">
              {citation.formatted_citation}
            </div>

          </div>

        </div>

        <div className="card-footer bg-white">

          <button
            className="btn btn-success"
            onClick={handleExport}
          >
            Download BibTeX
          </button>

        </div>

      </div>

    </div>

  );

}

export default CitationDetails;
