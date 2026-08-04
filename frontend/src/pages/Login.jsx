import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  login,
  getCurrentUser,
} from "../services/authService";

function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    setLoading(true);
    setError("");

    try {
      // Login
      const response = await login(email, password);

      // Save JWT
      if (response.access_token) {
        localStorage.setItem(
          "access_token",
          response.access_token
        );
      }

      // Fetch logged-in user
      const user = await getCurrentUser();

      // Save user information (including role)
      localStorage.setItem(
        "user",
        JSON.stringify(user)
      );

      navigate("/dashboard");

    } catch (err) {
      console.error(err);

      if (err.response?.status === 403) {
        setError(
          "Please verify your email before logging in."
        );
      } else if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError("Login failed.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="d-flex justify-content-center align-items-center"
      style={{
        minHeight: "100vh",
        background:
          "linear-gradient(135deg,#e3f2fd,#ffffff)",
      }}
    >
      <div
        className="card shadow-lg p-4"
        style={{
          width: "420px",
          borderRadius: "15px",
        }}
      >
        <h2 className="text-center text-primary mb-4">
          Login to SCNA
        </h2>

        {error && (
          <div className="alert alert-danger">
            <div>{error}</div>

            {error
              .toLowerCase()
              .includes("verify") && (
              <div className="mt-2">
                <Link
                  to="/resend-verification"
                  className="btn btn-warning btn-sm"
                >
                  Resend Verification Email
                </Link>
              </div>
            )}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label className="form-label fw-bold">
              Email
            </label>

            <input
              type="email"
              className="form-control"
              placeholder="Enter your email"
              value={email}
              onChange={(e) =>
                setEmail(e.target.value)
              }
              required
            />
          </div>

          <div className="mb-3">
            <label className="form-label fw-bold">
              Password
            </label>

            <input
              type="password"
              className="form-control"
              placeholder="Enter your password"
              value={password}
              onChange={(e) =>
                setPassword(e.target.value)
              }
              required
            />
          </div>

          <div className="d-flex justify-content-between align-items-center mb-3">
            <div className="form-check">
              <input
                className="form-check-input"
                type="checkbox"
                id="remember"
              />

              <label
                className="form-check-label"
                htmlFor="remember"
              >
                Remember Me
              </label>
            </div>

            <Link
              to="/forgot-password"
              className="text-decoration-none"
            >
              Forgot Password?
            </Link>
          </div>

          <button
            type="submit"
            className="btn btn-primary w-100"
            disabled={loading}
          >
            {loading
              ? "Logging in..."
              : "Login"}
          </button>

          <p className="text-center mt-3 mb-0">
            Don't have an account?{" "}
            <Link
              to="/register"
              className="text-decoration-none fw-bold"
            >
              Register
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}

export default Login;
