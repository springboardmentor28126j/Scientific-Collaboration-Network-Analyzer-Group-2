import { useEffect, useState } from "react";

function ConferenceForm({
  initialData = null,
  onSubmit,
  loading = false,
}) {
  const [formData, setFormData] = useState({
    title: "",
    location: "",
    conference_date: "",
    description: "",
  });

  useEffect(() => {
    if (!initialData) return;

    setFormData({
      title: initialData.title || "",
      location: initialData.location || "",
      conference_date: initialData.conference_date || "",
      description: initialData.description || "",
    });
  }, [initialData]);

  const handleChange = (e) => {
    const { name, value } = e.target;

    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="card shadow">
      <div className="card-header bg-primary text-white">
        <h4 className="mb-0">Conference Information</h4>
      </div>

      <div className="card-body">
        <form onSubmit={handleSubmit}>

          <div className="mb-3">
            <label className="form-label">
              Conference Title
            </label>

            <input
              type="text"
              className="form-control"
              name="title"
              value={formData.title}
              onChange={handleChange}
              required
            />
          </div>

          <div className="mb-3">
            <label className="form-label">
              Location
            </label>

            <input
              type="text"
              className="form-control"
              name="location"
              value={formData.location}
              onChange={handleChange}
            />
          </div>

          <div className="mb-3">
            <label className="form-label">
              Conference Date
            </label>

            <input
              type="date"
              className="form-control"
              name="conference_date"
              value={formData.conference_date}
              onChange={handleChange}
            />
          </div>

          <div className="mb-3">
            <label className="form-label">
              Description
            </label>

            <textarea
              rows="5"
              className="form-control"
              name="description"
              value={formData.description}
              onChange={handleChange}
            />
          </div>

          <div className="mt-4">
            <button
              type="submit"
              className="btn btn-success"
              disabled={loading}
            >
              {loading ? "Saving..." : "Save Conference"}
            </button>
          </div>

        </form>
      </div>
    </div>
  );
}

export default ConferenceForm;
