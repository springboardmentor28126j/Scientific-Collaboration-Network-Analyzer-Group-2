import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";
import axios from "axios";
import "../css/register.css";

function Register() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    username: "",
    email: "",
    institution: "",
    department: "",
    country: "",
    password: "",
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/register",
        {
          username: formData.username,
          email: formData.email,
          password: formData.password,
        }
      );

      alert(response.data.message);

      setFormData({
        username: "",
        email: "",
        institution: "",
        department: "",
        country: "",
        password: "",
      });

      navigate("/login");

    } catch (error) {
      if (error.response) {
        alert(error.response.data.detail);
      } else {
        alert("Unable to connect to the server.");
      }
    }
  };

  return (
    <div className="register-page">
      <div className="register-container">

        {/* Left Side */}
        <div className="left-side">
          <h1>Scientific Collaboration Network Analyzer</h1>

          <p>
            Create your account and become part of the scientific collaboration
            network. Manage your publications, projects, collaborations, and
            conferences in one place.
          </p>

          <ul>
            <li>✔ Researcher Profiles</li>
            <li>✔ Publication Management</li>
            <li>✔ Collaboration Network</li>
            <li>✔ Conference Tracking</li>
            <li>✔ Dashboard Analytics</li>
          </ul>
        </div>

        {/* Right Side */}
        <div className="right-side">

          <h2>Create Account</h2>

          <form className="register-form" onSubmit={handleSubmit}>

            <div className="form-row">

              <div className="form-group">
                <label>Full Name</label>
                <input
                  type="text"
                  name="username"
                  placeholder="Enter full name"
                  value={formData.username}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  name="email"
                  placeholder="Enter email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                />
              </div>

            </div>

            <div className="form-row">

              <div className="form-group">
                <label>Institution</label>
                <input
                  type="text"
                  name="institution"
                  placeholder="Institution"
                  value={formData.institution}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label>Department</label>
                <input
                  type="text"
                  name="department"
                  placeholder="Department"
                  value={formData.department}
                  onChange={handleChange}
                />
              </div>

            </div>

            <div className="form-row">

              <div className="form-group">
                <label>Country</label>
                <input
                  type="text"
                  name="country"
                  placeholder="Country"
                  value={formData.country}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label>Password</label>
                <input
                  type="password"
                  name="password"
                  placeholder="Create Password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                />
              </div>

            </div>

            <button type="submit">
              Create Account
            </button>

          </form>

          <p className="login-text">
            Already have an account?
            <Link to="/login"> Login</Link>
          </p>

          <Link className="back-home" to="/">
            ← Back to Home
          </Link>

        </div>

      </div>
    </div>
  );
}

export default Register;