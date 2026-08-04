import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import SearchBar from "./SearchBar";

export default function HeroSection({ statistics }) {
  const navigate = useNavigate();

  return (
    <section
      style={{
        background: "linear-gradient(135deg,#1565C0,#42A5F5)",
        color: "#fff",
        padding: "90px 0",
      }}
    >
      <div className="container">
        <div className="row justify-content-center">
          <motion.div
            className="col-lg-9"
            initial={{ opacity: 0, x: -60 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
          >
            <span className="badge bg-light text-primary mb-3 fs-6">
              Research Platform
            </span>

            <h1
              className="fw-bold"
              style={{
                fontSize: "4rem",
                lineHeight: 1.15,
              }}
            >
              Scientific Collaboration
            </h1>

            <h2 className="fw-light mb-4">
              Network Analyzer
            </h2>

            <p
              className="lead mb-4"
              style={{
                maxWidth: "650px",
              }}
            >
              Discover researchers, publications,
              institutions and conferences from one
              intelligent research platform.
            </p>

            <SearchBar />

            <div className="mt-5 d-flex flex-wrap gap-3">
              <button
                className="btn btn-light btn-lg"
                onClick={() => navigate("/researchers")}
              >
                Explore Research
              </button>

              <button
                className="btn btn-outline-light btn-lg"
                onClick={() => navigate("/dashboard")}
              >
                Go to Dashboard
              </button>
            </div>

            {/* Live Statistics */}

            <div className="row mt-5 text-center">
              <div className="col-md-3 col-6 mb-4">
                <h2 className="fw-bold">
                  {statistics?.researchers ?? 0}
                </h2>
                <small>Researchers</small>
              </div>

              <div className="col-md-3 col-6 mb-4">
                <h2 className="fw-bold">
                  {statistics?.publications ?? 0}
                </h2>
                <small>Publications</small>
              </div>

              <div className="col-md-3 col-6 mb-4">
                <h2 className="fw-bold">
                  {statistics?.institutions ?? 0}
                </h2>
                <small>Institutions</small>
              </div>

              <div className="col-md-3 col-6 mb-4">
                <h2 className="fw-bold">
                  {statistics?.conferences ?? 0}
                </h2>
                <small>Conferences</small>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
