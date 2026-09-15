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

      // Login successful
      alert(response.data.message);

      // Get user details from backend
      const userId = response.data.user_id;
      const username = response.data.username;
      const userEmail = response.data.email;
      const role = response.data.role;
      const accessToken = response.data.access_token;

      // Save user information in browser
      localStorage.setItem("user_id", userId);
      localStorage.setItem("username", username);
      localStorage.setItem("email", userEmail);
      localStorage.setItem("role", role);
      localStorage.setItem("access_token", accessToken);

      // Go to dashboard
      navigate("/dashboard");

    } catch (error) {
      console.log(error);

      if (error.response) {
        alert(
          error.response.data.detail ||
          "Invalid Email or Password"
        );
      } else {
        alert("Unable to connect to the server.");
      }
    }
  };

  return (
    <div className="login-page">

      <div className="login-container">

        {/* =========================
            LEFT SIDE
        ========================= */}

        <div className="left-side">

          <h1>
            🔬 Scientific Collaboration Network Analyzer
          </h1>

          <p>
            Welcome back! Login to access your researcher
            profile, publications, collaborations,
            conferences, and dashboard.
          </p>

          <ul>
            <li>✔ Researcher Profiles</li>
            <li>✔ Publication Management</li>
            <li>✔ Collaboration Network</li>
            <li>✔ Conference Management</li>
            <li>✔ Dashboard Analytics</li>
          </ul>

        </div>


        {/* =========================
            RIGHT SIDE
        ========================= */}

        <div className="right-side">

          <h2>Login</h2>

          <form onSubmit={handleLogin}>

            {/* EMAIL */}

            <label>Email</label>

            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />


            {/* PASSWORD */}

            <label>Password</label>

            <input
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />


            {/* LOGIN BUTTON */}

            <button type="submit">
              Login
            </button>

          </form>


          {/* REGISTER */}

          <p className="register-text">
            Don't have an account?

            <Link to="/register">
              {" "}Register
            </Link>
          </p>


          {/* BACK TO HOME */}

          <Link
            className="back-home"
            to="/"
          >
            ← Back to Home
          </Link>

        </div>

      </div>

    </div>
  );
}

export default Login;