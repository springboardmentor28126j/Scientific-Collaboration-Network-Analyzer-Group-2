import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";
import axios from "axios";
import "../css/login.css";

function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/login",
        {
          email: email,
          password: password,
        }
      );

      alert(response.data.message);

      navigate("/dashboard");
    } catch (error) {
      if (error.response) {
        alert(error.response.data.detail);
      } else {
        alert("Unable to connect to the server.");
      }
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">

        {/* Left Side */}
        <div className="left-side">
          <h1>🔬 Scientific Collaboration Network Analyzer</h1>

          <p>
            Welcome back! Login to access your researcher profile,
            publications, collaborations, conferences, and dashboard.
          </p>

          <ul>
            <li>✔ Researcher Profiles</li>
            <li>✔ Publication Management</li>
            <li>✔ Collaboration Network</li>
            <li>✔ Conference Management</li>
            <li>✔ Dashboard Analytics</li>
          </ul>
        </div>

        {/* Right Side */}
        <div className="right-side">

          <h2>Login</h2>

          <form onSubmit={handleLogin}>

            <label>Email</label>
            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />

            <label>Password</label>
            <input
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />

            <button type="submit">
              Login
            </button>

          </form>

          <p className="register-text">
            Don't have an account?
            <Link to="/register"> Register</Link>
          </p>

          <Link className="back-home" to="/">
            ← Back to Home
          </Link>

        </div>

      </div>
    </div>
  );
}

export default Login;