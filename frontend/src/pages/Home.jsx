import { Link } from "react-router-dom";
import "./Home.css";

function Home() {
  return (
    <div className="home">

      {/* ================= NAVBAR ================= */}
      <nav className="navbar">

        <Link to="/" className="logo">
          🔬 <span>SciCollab</span>
        </Link>

        <div className="nav-links">
          <Link to="/">Home</Link>
          <Link to="/profile">Researchers</Link>
          <Link to="/dashboard">Dashboard</Link>
          <Link to="/about">About</Link>
          <Link to="/login" className="btn login">
            Login
          </Link>

          <Link to="/register" className="btn register">
            Register
          </Link>
        </div>

      </nav>


      {/* ================= HERO SECTION ================= */}
      <section className="hero">

        <div className="hero-content">

          <span className="hero-tag">
            SCIENTIFIC RESEARCH PLATFORM
          </span>

          <h1>
            Connect Research.
            <br />
            <span>Collaborate & Innovate.</span>
          </h1>

          <p>
            A professional platform for researchers and institutions to
            manage publications, collaborations, conferences, and research
            activities in one place.
          </p>

          <div className="buttons">

            <Link to="/login" className="hero-btn">
              Get Started →
            </Link>

            <Link to="/profile" className="hero-btn-outline">
              Explore Researchers
            </Link>

          </div>

        </div>


        {/* ================= HERO INFO CARD ================= */}
        <div className="hero-card">

          <div className="card-header">
            <div className="card-icon">🔬</div>

            <div>
              <h3>Research Network</h3>
              <p>One connected workspace</p>
            </div>
          </div>


          <div className="network-item">
            <span className="network-icon">👨‍🔬</span>

            <div>
              <strong>Researchers</strong>
              <small>Connect with researchers</small>
            </div>
          </div>


          <div className="network-item">
            <span className="network-icon">📚</span>

            <div>
              <strong>Publications</strong>
              <small>Manage research publications</small>
            </div>
          </div>


          <div className="network-item">
            <span className="network-icon">🤝</span>

            <div>
              <strong>Collaborations</strong>
              <small>Build research partnerships</small>
            </div>
          </div>


          <div className="network-item">
            <span className="network-icon">🎓</span>

            <div>
              <strong>Conferences</strong>
              <small>Manage research events</small>
            </div>
          </div>

        </div>

      </section>


      {/* ================= FEATURES ================= */}
      <section className="features-section">

        <div className="section-heading">
          <span>PLATFORM FEATURES</span>

          <h2>
            Everything researchers need
          </h2>

          <p>
            Manage your scientific research activities through a single
            professional platform.
          </p>
        </div>


        <div className="features-grid">

          <div className="feature-card">
            <div className="feature-icon">👨‍🔬</div>

            <h3>Researcher Management</h3>

            <p>
              Create academic profiles, manage research interests,
              departments, skills, and affiliations.
            </p>
          </div>


          <div className="feature-card">
            <div className="feature-icon">📚</div>

            <h3>Publication Management</h3>

            <p>
              Manage journal papers, conference papers, books, patents,
              and technical reports.
            </p>
          </div>


          <div className="feature-card">
            <div className="feature-icon">🤝</div>

            <h3>Research Collaboration</h3>

            <p>
              Connect researchers, manage projects, co-authors,
              institutional collaborations, and teams.
            </p>
          </div>


          <div className="feature-card">
            <div className="feature-icon">🎓</div>

            <h3>Conference Management</h3>

            <p>
              Manage conference registrations, presentations,
              participation history, and events.
            </p>
          </div>

        </div>

      </section>


      {/* ================= RESEARCH AT A GLANCE ================= */}
      <section className="stats-section">

        <div className="section-heading">
          <span>RESEARCH AT A GLANCE</span>

          <h2>
            A connected research ecosystem
          </h2>
        </div>


        <div className="stats-grid">

          <div className="stat-box">
            <strong>150+</strong>
            <span>Researchers</span>
          </div>

          <div className="stat-box">
            <strong>540+</strong>
            <span>Publications</span>
          </div>

          <div className="stat-box">
            <strong>95+</strong>
            <span>Collaborations</span>
          </div>

          <div className="stat-box">
            <strong>28+</strong>
            <span>Conferences</span>
          </div>

        </div>

      </section>


      {/* ================= CTA ================= */}
      <section className="cta-section">

        <div>
          <span>SCICOLLAB</span>

          <h2>
            Bring your research network together.
          </h2>

          <p>
            Discover researchers, manage publications, and build
            meaningful scientific collaborations.
          </p>
        </div>

        <Link to="/register" className="cta-btn">
          Create Account →
        </Link>

      </section>


      {/* ================= FOOTER ================= */}
      <footer className="home-footer">

        <div>
          <h3>🔬 SciCollab</h3>

          <p>
            Scientific Collaboration Network Analyzer
          </p>
        </div>

        <div className="footer-links">
          <Link to="/">Home</Link>
          <Link to="/profile">Researchers</Link>
          <Link to="/dashboard">Dashboard</Link>
          <Link to="/login">Login</Link>
        </div>

        <p className="copyright">
          © 2026 SciCollab. Scientific Research Platform.
        </p>

      </footer>

    </div>
  );
}

export default Home;