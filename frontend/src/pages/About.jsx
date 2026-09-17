import { Link } from "react-router-dom";
import "./About.css";

function About() {
  return (
    <div className="about-page">
      <nav className="about-navbar">
        <div className="about-logo">🔬 SciCollab</div>

        <div className="about-nav-links">
          <Link to="/">Home</Link>
          <Link to="/researchers">Researchers</Link>
          <Link to="/dashboard">Dashboard</Link>
          <Link to="/about" className="active">About</Link>
          <Link to="/login">Login</Link>
          <Link to="/register">Register</Link>
        </div>
      </nav>

      <section className="about-hero">
        <div className="about-badge">SCIENTIFIC RESEARCH PLATFORM</div>

        <h1>
          About <span>SciCollab</span>
        </h1>

        <p>
          Scientific Collaboration Network Analyzer is a platform designed
          to help researchers and institutions manage publications,
          collaborations, conferences, reviews, and research activities
          in one connected workspace.
        </p>
      </section>

      <section className="about-section">
        <h2>Our Platform</h2>

        <p>
          SciCollab provides a centralized platform for managing scientific
          research information and collaboration activities.
        </p>

        <div className="about-cards">
          <div className="about-card">
            <h3>👩‍🔬 Researchers</h3>
            <p>
              Manage researcher profiles, interests, skills, and research
              activities.
            </p>
          </div>

          <div className="about-card">
            <h3>📚 Publications</h3>
            <p>
              Manage research papers, books, patents, reports, and
              publication status.
            </p>
          </div>

          <div className="about-card">
            <h3>🤝 Collaborations</h3>
            <p>
              Manage research partnerships, projects, and co-author
              collaborations.
            </p>
          </div>

          <div className="about-card">
            <h3>🎓 Conferences</h3>
            <p>
              Manage conference participation and research presentation
              records.
            </p>
          </div>
        </div>
      </section>

      <section className="roles-section">
        <h2>Platform Roles</h2>

        <div className="about-cards">
          <div className="about-card">
            <h3>Researcher</h3>
            <p>Manage personal research activities and publications.</p>
          </div>

          <div className="about-card">
            <h3>Institution Admin</h3>
            <p>Manage institution-related research activities and reports.</p>
          </div>

          <div className="about-card">
            <h3>Reviewer</h3>
            <p>Manage assigned publication reviews and feedback.</p>
          </div>

          <div className="about-card">
            <h3>System Admin</h3>
            <p>Manage and oversee the overall platform.</p>
          </div>
        </div>
      </section>

      <section className="about-footer-section">
        <h2>Connect Research. Collaborate. Innovate.</h2>

        <p>
          Explore the SciCollab research collaboration platform.
        </p>

        <Link to="/login" className="about-button">
          Get Started →
        </Link>
      </section>
    </div>
  );
}

export default About;