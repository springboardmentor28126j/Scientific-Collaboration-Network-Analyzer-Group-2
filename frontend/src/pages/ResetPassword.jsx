import React, { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { resetPassword } from "../services/authService";

function ResetPassword() {
  const navigate = useNavigate();

  const [searchParams] = useSearchParams();

  const token = searchParams.get("token");

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    setMessage("");
    setError("");

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      const response = await resetPassword(
        token,
        password
      );

      setMessage(
        response.message ||
          "Password reset successfully."
      );

      setTimeout(() => {
        navigate("/login");
      }, 3000);

    } catch (err) {
      console.error(err);

      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError("Unable to reset password.");
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
        background: "linear-gradient(135deg,#e3f2fd,#ffffff)",
      }}
    >
      <div
        className="card shadow-lg p-4"
        style={{
          width: "450px",
          borderRadius: "15px",
        }}
      >
        <h2 className="text-center text-primary mb-4">
          Reset Password
        </h2>

        {message && (
          <div className="alert alert-success">
            {message}
            <br />
            Redirecting to Login...
          </div>
        )}

        {error && (
          <div className="alert alert-danger">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>

          <div className="mb-3">
            <label className="form-label fw-bold">
              New Password
            </label>

            <input
              type="password"
              className="form-control"
              value={password}
              onChange={(e) =>
                setPassword(e.target.value)
              }
              required
            />
          </div>

          <div className="mb-3">
            <label className="form-label fw-bold">
              Confirm Password
            </label>

            <input
              type="password"
              className="form-control"
              value={confirmPassword}
              onChange={(e) =>
                setConfirmPassword(e.target.value)
              }
              required
            />
          </div>

          <button
            className="btn btn-primary w-100"
            disabled={loading}
          >
            {loading
              ? "Resetting..."
              : "Reset Password"}
          </button>

        </form>

        <div className="text-center mt-3">
          <Link to="/login">
            Back to Login
          </Link>
        </div>

      </div>
    </div>
  );
}

export default ResetPassword;
