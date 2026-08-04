import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { resendVerification } from "../services/authService";

function ResendVerification() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");

  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    setLoading(true);
    setSuccess("");
    setError("");

    try {
      const response = await resendVerification(email);

      setSuccess(
        response.message ||
          "Verification email has been sent successfully."
      );

      setTimeout(() => {
        navigate("/login");
      }, 3000);

    } catch (err) {
      console.error(err);

      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError(
          "Unable to send verification email. Please try again."
        );
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
          Resend Verification Email
        </h2>

        {success && (
          <div className="alert alert-success">
            {success}
            <br />
            Redirecting to login...
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
              Email Address
            </label>

            <input
              type="email"
              className="form-control"
              placeholder="Enter your registered email"
              value={email}
              onChange={(e) =>
                setEmail(e.target.value)
              }
              required
            />

          </div>

          <button
            type="submit"
            className="btn btn-primary w-100"
            disabled={loading}
          >
            {loading
              ? "Sending..."
              : "Resend Verification Email"}
          </button>

        </form>

        <div className="text-center mt-3">

          <Link
            to="/login"
            className="text-decoration-none"
          >
            ← Back to Login
          </Link>

        </div>

      </div>
    </div>
  );
}

export default ResendVerification;
