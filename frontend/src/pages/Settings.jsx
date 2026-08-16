import { useEffect, useState } from "react";
import {
  getMyResearcherProfile,
  updateResearcher,
} from "../services/researcherService";
import { getCurrentUser } from "../utils/auth";

export default function Settings() {
  const [researcher, setResearcher] = useState(null);
  const [formData, setFormData] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const currentUser = getCurrentUser();

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getMyResearcherProfile();

      setResearcher(data);

      setFormData({
        first_name: data.first_name || "",
        last_name: data.last_name || "",
        phone: data.phone || "",
        bio: data.bio || "",
        experience: data.experience ?? 0,
        skills: data.skills || "",
        interests: data.interests || "",
        orcid: data.orcid || "",
        google_scholar: data.google_scholar || "",
        research_gate: data.research_gate || "",
        linkedin: data.linkedin || "",
      });
    } catch (err) {
      console.error("Failed to load researcher profile:", err);

      setError(
        err.response?.data?.detail ||
          "Failed to load your profile."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      setSaving(true);
      setMessage("");
      setError("");

      const updated = await updateResearcher(
        researcher.id,
        {
          ...formData,
          experience: Number(formData.experience) || 0,
        }
      );

      setResearcher(updated);
      window.dispatchEvent(new Event("researcherProfileUpdated"));

      setMessage("Profile updated successfully.");

      window.scrollTo({
        top: 0,
        behavior: "smooth",
      });
    } catch (err) {
      console.error("Failed to update profile:", err);

      setError(
        err.response?.data?.detail ||
          "Failed to update your profile."
      );
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="container py-5">
        <div className="text-center">
          <p>Loading settings...</p>
        </div>
      </div>
    );
  }

  if (!researcher) {
    return (
      <div className="container py-5">
        <div className="alert alert-danger">
          {error || "Researcher profile not found."}
        </div>
      </div>
    );
  }

  return (
    <div className="container py-5">
      <div className="mb-4">
        <h1>Settings</h1>
        <p className="text-muted">
          Manage your profile and research information.
        </p>
      </div>

      {message && (
        <div className="alert alert-success">
          {message}
        </div>
      )}

      {error && (
        <div className="alert alert-danger">
          {error}
        </div>
      )}

      {/* Account Information */}
      <div className="card mb-4">
        <div className="card-body">
          <h4 className="mb-3">Account Information</h4>

          <div className="mb-3">
            <label className="form-label">
              Email
            </label>

            <input
              type="email"
              className="form-control"
              value={currentUser?.email || ""}
              disabled
            />

            <small className="text-muted">
              Email address is managed through your account.
            </small>
          </div>

          <div className="mb-3">
            <label className="form-label">
              Role
            </label>

            <input
              type="text"
              className="form-control"
              value={currentUser?.role || ""}
              disabled
            />
          </div>
        </div>
      </div>

      {/* Personal Information */}
      <div className="card mb-4">
        <div className="card-body">
          <h4 className="mb-3">
            Personal Information
          </h4>

          <div className="row">
            <div className="col-md-6 mb-3">
              <label className="form-label">
                First Name
              </label>

              <input
                type="text"
                name="first_name"
                className="form-control"
                value={formData.first_name}
                onChange={handleChange}
              />
            </div>

            <div className="col-md-6 mb-3">
              <label className="form-label">
                Last Name
              </label>

              <input
                type="text"
                name="last_name"
                className="form-control"
                value={formData.last_name}
                onChange={handleChange}
              />
            </div>
          </div>

          <div className="mb-3">
            <label className="form-label">
              Phone
            </label>

            <input
              type="text"
              name="phone"
              className="form-control"
              value={formData.phone}
              onChange={handleChange}
            />
          </div>

          <div className="mb-3">
            <label className="form-label">
              Bio
            </label>

            <textarea
              name="bio"
              className="form-control"
              rows="4"
              value={formData.bio}
              onChange={handleChange}
            />
          </div>

          <div className="mb-3">
            <label className="form-label">
              Experience (Years)
            </label>

            <input
              type="number"
              min="0"
              name="experience"
              className="form-control"
              value={formData.experience}
              onChange={handleChange}
            />
          </div>
        </div>
      </div>

      {/* Research Information */}
      <div className="card mb-4">
        <div className="card-body">
          <h4 className="mb-3">
            Research Information
          </h4>

          <div className="mb-3">
            <label className="form-label">
              Skills
            </label>

            <textarea
              name="skills"
              className="form-control"
              rows="3"
              placeholder="Example: Python, Machine Learning, SQL"
              value={formData.skills}
              onChange={handleChange}
            />
          </div>

          <div className="mb-3">
            <label className="form-label">
              Research Interests
            </label>

            <textarea
              name="interests"
              className="form-control"
              rows="3"
              placeholder="Example: Artificial Intelligence, Data Science"
              value={formData.interests}
              onChange={handleChange}
            />
          </div>

          <div className="mb-3">
            <label className="form-label">
              ORCID
            </label>

            <input
              type="text"
              name="orcid"
              className="form-control"
              value={formData.orcid}
              onChange={handleChange}
            />
          </div>

          <div className="mb-3">
            <label className="form-label">
              Google Scholar
            </label>

            <input
              type="url"
              name="google_scholar"
              className="form-control"
              value={formData.google_scholar}
              onChange={handleChange}
            />
          </div>

          <div className="mb-3">
            <label className="form-label">
              ResearchGate
            </label>

            <input
              type="url"
              name="research_gate"
              className="form-control"
              value={formData.research_gate}
              onChange={handleChange}
            />
          </div>

          <div className="mb-3">
            <label className="form-label">
              LinkedIn
            </label>

            <input
              type="url"
              name="linkedin"
              className="form-control"
              value={formData.linkedin}
              onChange={handleChange}
            />
          </div>
        </div>
      </div>

      {/* Save */}
      <div className="d-flex justify-content-end">
        <button
          type="button"
          className="btn btn-primary px-4"
          onClick={handleSubmit}
          disabled={saving}
        >
          {saving ? "Saving..." : "Save Changes"}
        </button>
      </div>
    </div>
  );
}