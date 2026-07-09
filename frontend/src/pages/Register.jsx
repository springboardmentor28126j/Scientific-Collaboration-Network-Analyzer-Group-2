import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";

import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import api from "../services/api";

import "../styles/register.css";

function Register() {

  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    full_name: "",
    username: "",
    email: "",
    password: "",
    phone_number: "",
    gender: "",
    date_of_birth: "",

    institution: "",
    department: "",
    designation: "",

    specialization: "",
    research_interests: "",

    country: "",
    state: "",
    city: ""
  });

  const [message, setMessage] = useState("");

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleRegister = async (e) => {
    e.preventDefault();

    try {

      await api.post("/auth/register", formData);

      setMessage("✅ Registration Successful");

      setTimeout(() => {
        navigate("/login");
      }, 1500);

    } catch (err) {

      if (err.response) {
        setMessage(err.response.data.detail || "Registration Failed");
      } else {
        setMessage("Server Error");
      }

    }
  };

  return (
    <div>

      <Navbar />

      <div className="register-container">

        <div className="register-card">

          <h2>Create Researcher Account</h2>

          <form onSubmit={handleRegister}>

            <h3>Basic Information</h3>

            <input
              name="full_name"
              placeholder="Full Name"
              onChange={handleChange}
              required
            />

            <input
              name="username"
              placeholder="Username"
              onChange={handleChange}
              required
            />

            <input
              type="email"
              name="email"
              placeholder="Email"
              onChange={handleChange}
              required
            />

            <input
              type="password"
              name="password"
              placeholder="Password"
              onChange={handleChange}
              required
            />

            <input
              name="phone_number"
              placeholder="Phone Number"
              onChange={handleChange}
              required
            />

            <select
              name="gender"
              onChange={handleChange}
              required
            >
              <option value="">Select Gender</option>
              <option>Male</option>
              <option>Female</option>
              <option>Other</option>
            </select>

            <input
              type="date"
              name="date_of_birth"
              onChange={handleChange}
              required
            />

            <h3>Academic Information</h3>

            <input
              name="institution"
              placeholder="Institution"
              onChange={handleChange}
              required
            />

            <input
              name="department"
              placeholder="Department"
              onChange={handleChange}
              required
            />

            <input
              name="designation"
              placeholder="Designation"
              onChange={handleChange}
              required
            />

            <h3>Research Information</h3>

            <input
              name="specialization"
              placeholder="Specialization"
              onChange={handleChange}
              required
            />

            <input
              name="research_interests"
              placeholder="Research Interests"
              onChange={handleChange}
              required
            />

            <h3>Location</h3>

            <input
              name="country"
              placeholder="Country"
              onChange={handleChange}
              required
            />

            <input
              name="state"
              placeholder="State"
              onChange={handleChange}
              required
            />

            <input
              name="city"
              placeholder="City"
              onChange={handleChange}
              required
            />

            <button type="submit">
              Register
            </button>

          </form>

          <p>{message}</p>

          <p>
            Already have an account?{" "}
            <Link to="/login">Login</Link>
          </p>

        </div>

      </div>

      <Footer />

    </div>
  );
}

export default Register;