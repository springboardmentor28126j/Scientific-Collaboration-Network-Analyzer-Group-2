import { useEffect, useState } from "react";

import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import api from "../services/api";

import "../styles/settings.css";

function Settings() {
  const [user, setUser] = useState(null);
  const [form, setForm] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("");

  const token = localStorage.getItem("token");
  const role = localStorage.getItem("role");

  useEffect(() => {
    fetchUser();
  }, []);

  const fetchUser = async () => {
    try {
      const response = await api.get("/auth/me", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      setUser(response.data);

      setForm({
        full_name: response.data.full_name || "",
        phone_number: response.data.phone_number || "",
        institution: response.data.institution || "",
        department: response.data.department || "",
        designation: response.data.designation || "",
        specialization: response.data.specialization || "",
        research_interests: response.data.research_interests || "",
        country: response.data.country || "",
        state: response.data.state || "",
        city: response.data.city || "",
        website: response.data.website || "",
      });
    } catch (error) {
      console.error("Failed to load profile:", error);
      setMessage("Unable to load profile information.");
      setMessageType("error");
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });

    if (message) {
      setMessage("");
      setMessageType("");
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();

    setSaving(true);
    setMessage("");
    setMessageType("");

    try {
      const response = await api.put(
        "/auth/update-profile",
        form,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setUser(response.data);

      localStorage.setItem(
        "user",
        response.data.full_name
      );

      setMessage("Profile updated successfully.");
      setMessageType("success");
    } catch (error) {
      setMessage(
        error.response?.data?.detail ||
          "Failed to update profile."
      );
      setMessageType("error");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <>
        <Navbar />

        <div className="settings-loading">
          <div className="loading-spinner"></div>
          <p>Loading your profile...</p>
        </div>

        <Footer />
      </>
    );
  }

  const displayName =
    user?.full_name || user?.username || "User";

  const firstLetter =
    displayName.charAt(0).toUpperCase();

  return (
    <>
      <Navbar />

      <main className="settings-page">

        <div className="settings-wrapper">

          {/* PAGE HEADER */}

          <div className="settings-header">

            <div>
              <span className="settings-eyebrow">
                ACCOUNT SETTINGS
              </span>

              <h1>Settings</h1>

              <p>
                Manage your profile, academic information,
                research interests and contact details.
              </p>
            </div>

            {/* PROFILE SUMMARY */}

            <div className="profile-summary">

              <div className="profile-avatar">
                {firstLetter}
              </div>

              <div className="profile-summary-text">

                <strong>{displayName}</strong>

                <span>
                  {user?.role || role || "Researcher"}
                </span>

              </div>

            </div>

          </div>

          {/* MESSAGE */}

          {message && (
            <div
              className={`settings-message ${messageType}`}
            >
              <span className="message-icon">
                {messageType === "success" ? "✓" : "!"}
              </span>

              <span>{message}</span>
            </div>
          )}

          <form onSubmit={handleSave}>

            {/* PROFILE INFORMATION */}

            <section className="settings-card">

              <div className="section-header">

                <div className="section-icon profile-icon">
                  👤
                </div>

                <div>
                  <h2>Profile Information</h2>

                  <p>
                    Your basic account and contact information
                  </p>
                </div>

              </div>

              <div className="section-divider"></div>

              <div className="settings-grid">

                <div className="form-group">

                  <label htmlFor="full_name">
                    Full Name
                  </label>

                  <input
                    id="full_name"
                    name="full_name"
                    type="text"
                    value={form.full_name || ""}
                    onChange={handleChange}
                    placeholder="Enter your full name"
                  />

                </div>

                <div className="form-group">

                  <label htmlFor="email">
                    Email Address
                  </label>

                  <input
                    id="email"
                    type="email"
                    value={user?.email || ""}
                    disabled
                  />

                  <small>
                    Email address cannot be changed here.
                  </small>

                </div>

                <div className="form-group">

                  <label htmlFor="username">
                    Username
                  </label>

                  <input
                    id="username"
                    type="text"
                    value={user?.username || ""}
                    disabled
                  />

                  <small>
                    Username is linked to your account.
                  </small>

                </div>

                <div className="form-group">

                  <label htmlFor="phone_number">
                    Phone Number
                  </label>

                  <input
                    id="phone_number"
                    name="phone_number"
                    type="tel"
                    value={form.phone_number || ""}
                    onChange={handleChange}
                    placeholder="Enter your phone number"
                  />

                </div>

              </div>

            </section>

            {/* ACADEMIC INFORMATION */}

            <section className="settings-card">

              <div className="section-header">

                <div className="section-icon academic-icon">
                  🎓
                </div>

                <div>
                  <h2>
                    {role === "Researcher"
                      ? "Academic & Research Information"
                      : "Institution Information"}
                  </h2>

                  <p>
                    Keep your professional and academic
                    information up to date.
                  </p>
                </div>

              </div>

              <div className="section-divider"></div>

              <div className="settings-grid">

                <div className="form-group">

                  <label htmlFor="institution">
                    {role === "Researcher"
                      ? "Institution"
                      : "Institution Name"}
                  </label>

                  <input
                    id="institution"
                    name="institution"
                    type="text"
                    value={form.institution || ""}
                    onChange={handleChange}
                    placeholder="Enter institution name"
                  />

                </div>

                <div className="form-group">

                  <label htmlFor="department">
                    Department
                  </label>

                  <input
                    id="department"
                    name="department"
                    type="text"
                    value={form.department || ""}
                    onChange={handleChange}
                    placeholder="Enter department"
                  />

                </div>

                <div className="form-group">

                  <label htmlFor="designation">
                    Designation
                  </label>

                  <input
                    id="designation"
                    name="designation"
                    type="text"
                    value={form.designation || ""}
                    onChange={handleChange}
                    placeholder="Enter designation"
                  />

                </div>

                <div className="form-group">

                  <label htmlFor="specialization">
                    Specialization
                  </label>

                  <input
                    id="specialization"
                    name="specialization"
                    type="text"
                    value={form.specialization || ""}
                    onChange={handleChange}
                    placeholder="Enter your specialization"
                  />

                </div>

              </div>

              <div className="form-group full-width">

                <label htmlFor="research_interests">
                  Research Interests
                </label>

                <textarea
                  id="research_interests"
                  name="research_interests"
                  value={form.research_interests || ""}
                  onChange={handleChange}
                  rows="4"
                  placeholder="e.g. Machine Learning, NLP, Computer Vision"
                />

                <small>
                  Add topics or research areas that describe
                  your academic interests.
                </small>

              </div>

            </section>

            {/* LOCATION */}

            <section className="settings-card">

              <div className="section-header">

                <div className="section-icon location-icon">
                  📍
                </div>

                <div>
                  <h2>Location & Website</h2>

                  <p>
                    Add your location and professional website.
                  </p>
                </div>

              </div>

              <div className="section-divider"></div>

              <div className="settings-grid">

                <div className="form-group">

                  <label htmlFor="country">
                    Country
                  </label>

                  <input
                    id="country"
                    name="country"
                    type="text"
                    value={form.country || ""}
                    onChange={handleChange}
                    placeholder="Enter country"
                  />

                </div>

                <div className="form-group">

                  <label htmlFor="state">
                    State
                  </label>

                  <input
                    id="state"
                    name="state"
                    type="text"
                    value={form.state || ""}
                    onChange={handleChange}
                    placeholder="Enter state"
                  />

                </div>

                <div className="form-group">

                  <label htmlFor="city">
                    City
                  </label>

                  <input
                    id="city"
                    name="city"
                    type="text"
                    value={form.city || ""}
                    onChange={handleChange}
                    placeholder="Enter city"
                  />

                </div>

                <div className="form-group">

                  <label htmlFor="website">
                    Professional Website
                  </label>

                  <input
                    id="website"
                    name="website"
                    type="url"
                    value={form.website || ""}
                    onChange={handleChange}
                    placeholder="https://example.com"
                  />

                </div>

              </div>

            </section>

            {/* ACTIONS */}

            <div className="settings-actions">

              <button
                type="submit"
                className="save-settings-btn"
                disabled={saving}
              >
                {saving ? (
                  <>
                    <span className="button-spinner"></span>
                    Saving...
                  </>
                ) : (
                  <>
                    Save Changes
                  </>
                )}
              </button>

            </div>

          </form>

        </div>

      </main>

      <Footer />
    </>
  );
}

export default Settings;