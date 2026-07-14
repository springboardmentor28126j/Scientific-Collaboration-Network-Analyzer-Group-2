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
    city: "",

    website: "",
    established_year: "",
    institution_type: "",
    
    role: "Researcher"
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

          <h2>Create Account</h2>

          <form onSubmit={handleRegister}>

            <h3>Basic Information</h3>

            <input
              name="full_name"
              value={formData.full_name}
              placeholder="Full Name"
              onChange={handleChange}
              required
            />

            <input
              name="username"
              value={formData.username}
              placeholder="Username"
              onChange={handleChange}
              required
            />

            <input
              type="email"
              name="email"
              value={formData.email}
              placeholder="Email"
              onChange={handleChange}
              required
            />

            <input
              type="password"
              name="password"
              value={formData.password}
              placeholder="Password"
              onChange={handleChange}
              required
            />
            <h3>Account Type</h3>

            <select
              name="role"
              value={formData.role}
              onChange={(e) => {
                  console.log(e.target.value);
                  handleChange(e);
              }}
            >
              <option value="Researcher">Researcher</option>
              <option value="Institution">Institution</option>
            </select>

            <input
              name="phone_number"
              value={formData.phone_number}
              placeholder="Phone Number"
              onChange={handleChange}
              required
            />

            <select
               name="gender"
               value={formData.gender}
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
              value={formData.date_of_birth}
              onChange={handleChange}
              required
             />
           {formData.role === "Researcher" && (
  <>
            <h3>Academic Information</h3>

              <input
                name="institution"
                value={formData.institution}
                placeholder="Institution"
                onChange={handleChange}
                required
              />

              <input
                name="department"
                value={formData.department}
                placeholder="Department"
                onChange={handleChange}
                required
              />

              <input
                name="designation"
                value={formData.designation}
                placeholder="Designation"
                onChange={handleChange}
                required
              />

              <h3>Research Information</h3>

              <input
                name="specialization"
                value={formData.specialization}
                placeholder="Specialization"
                onChange={handleChange}
                required
              />

              <input
                name="research_interests"
                value={formData.research_interests}
                placeholder="Research Interests"
                onChange={handleChange}
                required
              />
  </>
)}
      {formData.role === "Institution" && (
  <>
    <h3>Institution Information</h3>

    <input
      name="website"
      value={formData.website || ""}
      placeholder="Official Website"
      onChange={handleChange}
    />

    <input
      name="established_year"
      value={formData.established_year || ""}
      placeholder="Established Year"
      onChange={handleChange}
    />

    <select
      name="institution_type"
      value={formData.institution_type || ""}
      onChange={handleChange}
    >
      <option value="">Institution Type</option>
      <option value="University">University</option>
      <option value="College">College</option>
      <option value="Research Lab">Research Lab</option>
      <option value="Private Organization">Private Organization</option>
    </select>
  </>
)}
            <h3>Location</h3>

            <input
              name="country"
              value={formData.country}
              placeholder="Country"
              onChange={handleChange}
              required
            />

            <input
              name="state"
              value={formData.state}
              placeholder="State"
              onChange={handleChange}
              required
            />

            <input
              name="city"
              value={formData.city}
              placeholder="City"
              onChange={handleChange}
              required
            />
            <button type="submit">
                Register as {formData.role}
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