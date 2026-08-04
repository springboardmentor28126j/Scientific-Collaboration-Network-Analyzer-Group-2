function PublicationCard({ publication }) {
  return (
    <div className="col-lg-4 mb-4">

      <div className="card shadow h-100">

        <div className="card-body">

          <h5>{publication.title}</h5>

          <p className="text-muted">
            {publication.journal || publication.conference}
          </p>

          <p>
            {publication.abstract?.length > 120
              ? publication.abstract.substring(0, 120) + "..."
              : publication.abstract}
          </p>

        </div>

      </div>

    </div>
  );
}

export default PublicationCard;
