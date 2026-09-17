import { useState } from "react";
import { Link } from "react-router-dom";
import "./ResearcherProfile.css";

function ResearcherProfile() {
  const [profile, setProfile] = useState({
    name: "Selected Researcher",
    email: "researcher@example.com",
    institution: "Institution Name",
    department: "Department Name",
    country: "Country Name",
    skills: "",
    research_interests: ""
  });

  const [editing, setEditing] = useState(false);
  const [profileImage, setProfileImage] = useState(null);

  const handleChange = (e) => {
    setProfile({
      ...profile,
      [e.target.name]: e.target.value
    });
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];

    if (file) {
      setProfileImage(URL.createObjectURL(file));
    }
  };

  const handleSave = () => {
    setEditing(false);
    alert("Profile updated successfully!");
  };

  return (
    <div className="profile-page">

      <div className="profile-card">

        {/* Top Banner */}
        <div className="profile-banner">
          <div className="banner-pattern"></div>
        </div>

        {/* Profile Header */}
        <div className="profile-header">

          <div className="profile-picture-section">

            {profileImage ? (
              <img
                src={profileImage}
                alt="Profile"
                className="profile-picture"
              />
            ) : (
              <div className="profile-picture default-picture">
                👤
              </div>
            )}

            {editing && (
              <label className="upload-button">
                Change Photo
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleImageChange}
                  hidden
                />
              </label>
            )}

          </div>

          <div className="profile-title">
            <h1>{profile.name}</h1>
            <p>Researcher Profile</p>
          </div>

        </div>

        {/* Profile Information */}
        <div className="profile-content">

          <div className="section-heading">
            <h2>Personal & Academic Information</h2>
            <span>Researcher Details</span>
          </div>

          <div className="profile-grid">

            <div className="profile-field">
              <label>Name</label>

              {editing ? (
                <input
                  type="text"
                  name="name"
                  value={profile.name}
                  onChange={handleChange}
                />
              ) : (
                <div className="info-box">
                  <span>👤</span>
                  <p>{profile.name}</p>
                </div>
              )}
            </div>

            <div className="profile-field">
              <label>Email</label>

              {editing ? (
                <input
                  type="email"
                  name="email"
                  value={profile.email}
                  onChange={handleChange}
                />
              ) : (
                <div className="info-box">
                  <span>✉️</span>
                  <p>{profile.email}</p>
                </div>
              )}
            </div>

            <div className="profile-field">
              <label>Institution</label>

              {editing ? (
                <input
                  type="text"
                  name="institution"
                  value={profile.institution}
                  onChange={handleChange}
                />
              ) : (
                <div className="info-box">
                  <span>🏛️</span>
                  <p>{profile.institution}</p>
                </div>
              )}
            </div>

            <div className="profile-field">
              <label>Department</label>

              {editing ? (
                <input
                  type="text"
                  name="department"
                  value={profile.department}
                  onChange={handleChange}
                />
              ) : (
                <div className="info-box">
                  <span>🎓</span>
                  <p>{profile.department}</p>
                </div>
              )}
            </div>

            <div className="profile-field">
              <label>Country</label>

              {editing ? (
                <input
                  type="text"
                  name="country"
                  value={profile.country}
                  onChange={handleChange}
                />
              ) : (
                <div className="info-box">
                  <span>🌐</span>
                  <p>{profile.country}</p>
                </div>
              )}
            </div>

            <div className="profile-field">
              <label>Skills</label>

              {editing ? (
                <input
                  type="text"
                  name="skills"
                  placeholder="Python, AI, Machine Learning"
                  value={profile.skills}
                  onChange={handleChange}
                />
              ) : (
                <div className="info-box">
                  <span>💡</span>
                  <p>
                    {profile.skills || "Not specified"}
                  </p>
                </div>
              )}
            </div>

          </div>

          {/* Research Interests */}
          <div className="research-section">

            <div className="profile-field full-width">

              <label>Research Interests</label>

              {editing ? (
                <textarea
                  name="research_interests"
                  placeholder="Artificial Intelligence, Machine Learning, NLP..."
                  value={profile.research_interests}
                  onChange={handleChange}
                  rows="4"
                />
              ) : (
                <div className="research-box">
                  <div className="research-icon">
                    🔬
                  </div>

                  <p>
                    {profile.research_interests ||
                      "No research interests specified yet."}
                  </p>
                </div>
              )}

            </div>

          </div>

          {/* Buttons */}
          <div className="profile-actions">

            <div className="left-actions">

              {!editing ? (
                <button
                  className="edit-button"
                  onClick={() => setEditing(true)}
                >
                  ✏️ Edit Profile
                </button>
              ) : (
                <>
                  <button
                    className="save-button"
                    onClick={handleSave}
                  >
                    ✓ Save Profile
                  </button>

                  <button
                    className="cancel-button"
                    onClick={() => setEditing(false)}
                  >
                    Cancel
                  </button>
                </>
              )}

            </div>

            <Link
              to="/researchers"
              className="back-button"
            >
              ← Back to Researchers
            </Link>

          </div>

        </div>

      </div>

    </div>
  );
}

export default ResearcherProfile;