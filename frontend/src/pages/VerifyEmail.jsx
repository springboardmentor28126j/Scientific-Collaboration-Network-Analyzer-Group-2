import React, { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { verifyEmail } from "../services/authService";

function VerifyEmail() {
  const [searchParams] = useSearchParams();

  const token = searchParams.get("token");

  const [loading, setLoading] = useState(true);
  const [success, setSuccess] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    const verify = async () => {
      if (!token) {
        setSuccess(false);
        setMessage("Verification token is missing.");
        setLoading(false);
        return;
      }

      try {
        const response = await verifyEmail(token);

        setSuccess(true);

        setMessage(
          response.message ||
            "Your email has been verified successfully."
        );
      } catch (err) {
        console.error(err);

        setSuccess(false);

        if (err.response?.data?.detail) {
          setMessage(err.response.data.detail);
        } else {
          setMessage("Email verification failed.");
        }
      } finally {
        setLoading(false);
      }
    };

    verify();
  }, [token]);

  return (
    <div
      className="d-flex justify-content-center align-items-center"
      style={{
        minHeight: "100vh",
        background: "linear-gradient(135deg,#e3f2fd,#ffffff)",
      }}
    >
      <div
        className="card shadow-lg p-5"
        style={{
          width: "500px",
          borderRadius: "15px",
        }}
      >
        <h2 className="text-center text-primary mb-4">
          Email Verification
        </h2>

        {loading ? (
          <div className="text-center">

            <div
              className="spinner-border text-primary mb-3"
              role="status"
            >
              <span className="visually-hidden">
                Loading...
              </span>
            </div>

            <p>Verifying your email...</p>

          </div>
        ) : success ? (
          <>
            <div className="alert alert-success">
              {message}
            </div>

            <div className="text-center">

              <Link
                to="/login"
                className="btn btn-success"
              >
                Go to Login
              </Link>

            </div>
          </>
        ) : (
          <>
            <div className="alert alert-danger">
              {message}
            </div>

            <div className="text-center">

              <Link
                to="/resend-verification"
                className="btn btn-warning me-2"
              >
                Resend Verification Email
              </Link>

              <Link
                to="/login"
                className="btn btn-secondary"
              >
                Login
              </Link>

            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default VerifyEmail;
