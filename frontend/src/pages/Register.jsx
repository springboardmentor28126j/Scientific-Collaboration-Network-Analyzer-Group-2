import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { register } from "../services/authService";

function Register() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    email: "",
    password: "",
    role: "Researcher",
  });

  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setLoading(true);
    setError("");
    setSuccess("");

    try {
      await register(formData);

      setSuccess(
        "Registration successful! Please check your email to verify your account."
      );

      setTimeout(() => {
        navigate("/login");
      }, 3000);
    } catch (err) {
      console.error(err);

      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError("Registration failed.");
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
        background: "linear-gradient(135deg, #e3f2fd, #ffffff)",
      }}
    >
      <div
        className="card shadow-lg p-4"
        style={{
          width: "460px",
          borderRadius: "15px",
        }}
      >
        <h2 className="text-center text-primary mb-4">
          Create SCNA Account
        </h2>

        {success && (
          <div className="alert alert-success">
            {success}
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
              Full Name
            </label>

            <input
              type="text"
              name="first_name"
              className="form-control"
              placeholder="Enter your first name"
              value={formData.first_name}
              onChange={handleChange}
              required
            />
          </div>

          <div className="mb-3">
            <label className="form-label fw-bold">
              Last Name
            </label>

            <input
              type="text"
              name="last_name"
              className="form-control"
              placeholder="Enter your last name"
              value={formData.last_name}
              onChange={handleChange}
              required
            />
          </div>

          <div className="mb-3">
            <label className="form-label fw-bold">
              Email
            </label>

            <input
              type="email"
              name="email"
              className="form-control"
              placeholder="Enter your email"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>

          <div className="mb-3">
            <label className="form-label fw-bold">
              Password
            </label>

            <input
              type="password"
              name="password"
              className="form-control"
              placeholder="Enter your password"
              value={formData.password}
              onChange={handleChange}
              required
              minLength={6}
            />
          </div>

          <div className="mb-4">
            <label className="form-label fw-bold">
              Role
            </label>

            <select
              name="role"
              className="form-select"
              value={formData.role}
              onChange={handleChange}
            >
              <option value="Researcher">Researcher</option>
              <option value="Reviewer">Reviewer</option>
              <option value="InstitutionAdmin">
                Institution Admin
              </option>
              <option value="SystemAdmin">
                System Admin
              </option>
            </select>
          </div>

          <button
            type="submit"
            className="btn btn-primary w-100"
            disabled={loading}
          >
            {loading ? "Creating Account..." : "Register"}
          </button>

          <p className="text-center mt-3 mb-0">
            Already have an account?{" "}
            <Link
              to="/login"
              className="fw-bold text-decoration-none"
            >
              Login
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}

export default Register;
