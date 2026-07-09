import { useState } from "react";
import { useNavigate } from "react-router-dom";

import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import api from "../services/api";

import "../styles/login.css";

function Login() {

  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const handleLogin = async (e) => {

    e.preventDefault();

    try {

      const response = await api.post("/auth/login", {
        email,
        password,
      });

      localStorage.setItem(
        "token",
        response.data.access_token
      );
      localStorage.setItem(
  "user",
  response.data.full_name
);

      setMessage("✅ Login Successful");

      // 1 second tarvatha Dashboard ki redirect
      setTimeout(() => {
        navigate("/");
      }, 1000);

    } catch (err) {

      setMessage("❌ Invalid Email or Password");

    }

  };

  return (

    <div>

      <Navbar />

      <div className="login-container">

        <div className="login-card">

          <h2>🔐 Login</h2>

          <form onSubmit={handleLogin}>

            <input
              type="email"
              placeholder="Enter Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />

            <input
              type="password"
              placeholder="Enter Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />

            <button type="submit">
              Login
            </button>

          </form>

          {message && <p>{message}</p>}

        </div>

      </div>

      <Footer />

    </div>

  );

}

export default Login;