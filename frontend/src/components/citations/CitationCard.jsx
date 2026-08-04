import { Link } from "react-router-dom";

function CitationCard({
  citation,
  onDelete,
  onExportBibtex,
}) {
  return (
    <div className="card shadow h-100">

      <div className="card-body">

        <h5 className="card-title text-primary">
          {citation.title}
        </h5>

        <hr />

        <p>
          <strong>Authors</strong>
          <br />
          {citation.authors}
        </p>

        <p>
          <strong>Journal</strong>
          <br />
          {citation.journal || "N/A"}
        </p>

        <p>
          <strong>Year</strong>
          <br />
          {citation.year}
        </p>

        <p>
          <strong>DOI</strong>
          <br />
          {citation.doi || "N/A"}
        </p>

        <p>
          <strong>Citation Style</strong>
          <br />

          <span className="badge bg-primary">
            {citation.citation_style}
          </span>

        </p>

        <p>
          <strong>Formatted Citation</strong>
          <br />

          <small className="text-muted">
            {citation.formatted_citation}
          </small>

        </p>

      </div>

      <div className="card-footer bg-white">

        <div className="d-flex flex-wrap gap-2">

          <Link
            to={`/citations/edit/${citation.id}`}
            className="btn btn-warning"
          >
            Edit
          </Link>

          <button
            className="btn btn-danger"
            onClick={() => onDelete(citation.id)}
          >
            Delete
          </button>

          <button
            className="btn btn-success"
            onClick={() =>
              onExportBibtex(citation.id)
            }
          >
            BibTeX
          </button>

        </div>

      </div>

    </div>
  );
}

export default CitationCard;
