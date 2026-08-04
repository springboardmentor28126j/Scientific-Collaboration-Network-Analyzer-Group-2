function FeatureCard() {
  return (
    <div className="container py-5">
      <h2 className="text-center mb-5 text-primary">
        Platform Features
      </h2>

      <div className="row">

        <div className="col-md-4 mb-4">
          <div className="card shadow h-100">
            <div className="card-body text-center">
              <h3>👨‍🔬</h3>
              <h4>Researchers</h4>
              <p>
                Discover researchers, their expertise, publications,
                and collaboration networks.
              </p>
            </div>
          </div>
        </div>

        <div className="col-md-4 mb-4">
          <div className="card shadow h-100">
            <div className="card-body text-center">
              <h3>🏛️</h3>
              <h4>Institutions</h4>
              <p>
                Explore universities, research centers,
                and their scientific contributions.
              </p>
            </div>
          </div>
        </div>

        <div className="col-md-4 mb-4">
          <div className="card shadow h-100">
            <div className="card-body text-center">
              <h3>📚</h3>
              <h4>Publications</h4>
              <p>
                Browse journals, conferences,
                and research publications with ease.
              </p>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}

export default FeatureCard;