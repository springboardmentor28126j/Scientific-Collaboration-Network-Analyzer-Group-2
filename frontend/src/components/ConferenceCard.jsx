function ConferenceCard({ conference }) {
  return (
    <div className="col-lg-4 mb-4">

      <div className="card shadow h-100">

        <div className="card-body">

          <h5>{conference.name}</h5>

          <p className="text-muted">
            {conference.location}
          </p>

          <p>
            {conference.description}
          </p>

        </div>

      </div>

    </div>
  );
}

export default ConferenceCard;
