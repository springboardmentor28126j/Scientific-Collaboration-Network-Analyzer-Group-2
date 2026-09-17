import { Link } from "react-router-dom";
import "./Home.css";

function Home() {
  return (
    <div className="home">

      {/* Navbar */}
      <nav className="navbar">

        <h2 className="logo">🔬 SciCollab</h2>

        <div className="nav-links">

          <Link to="/">Home</Link>

          <Link to="/profile">Researchers</Link>

          <Link to="/dashboard">Dashboard</Link>

          <Link to="/">About</Link>

          <Link to="/login" className="btn login">
            Login
          </Link>

          <Link to="/register" className="btn register">
            Register
          </Link>

        </div>

      </nav>

      {/* Hero Section */}

      <section className="hero">

        <h1>Scientific Collaboration Network Analyzer</h1>

        <p>
          Connect with researchers around the world, discover research
          publications, build collaborations, manage conferences, and
          accelerate scientific innovation through one powerful platform.
        </p>

        <div className="buttons">

          <Link to="/login" className="hero-btn">
            Get Started
          </Link>

          <Link to="/register" className="hero-btn2">
            Join Now
          </Link>

          <Link to="/dashboard" className="hero-btn3">
            Dashboard
          </Link>

        </div>

      </section>

    </div>
  );
}

export default Home;