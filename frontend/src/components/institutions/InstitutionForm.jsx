import { useEffect, useState } from "react";

function InstitutionForm({
  initialData = null,
  onSubmit,
  loading = false,
}) {
  const [formData, setFormData] = useState({
    name: "",
    abbreviation: "",
    website: "",
    email: "",
    phone: "",
    address: "",
    city: "",
    state: "",
    country: "",
  });

  useEffect(() => {
    if (!initialData) return;

    setFormData({
      name: initialData.name || "",
      abbreviation: initialData.abbreviation || "",
      website: initialData.website || "",
      email: initialData.email || "",
      phone: initialData.phone || "",
      address: initialData.address || "",
      city: initialData.city || "",
      state: initialData.state || "",
      country: initialData.country || "",
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
        <h4 className="mb-0">Institution Information</h4>
      </div>

      <div className="card-body">
        <form onSubmit={handleSubmit}>
          <div className="row">

            <div className="col-md-6 mb-3">
              <label className="form-label">
                Institution Name
              </label>
              <input
                type="text"
                name="name"
                className="form-control"
                value={formData.name}
                onChange={handleChange}
                autoComplete="off"
                required
              />
            </div>

            <div className="col-md-6 mb-3">
              <label className="form-label">
                Abbreviation
              </label>
              <input
                type="text"
                name="abbreviation"
                className="form-control"
                value={formData.abbreviation}
                onChange={handleChange}
                autoComplete="off"
              />
            </div>

            <div className="col-md-6 mb-3">
              <label className="form-label">
                Website
              </label>
              <input
                type="url"
                name="website"
                className="form-control"
                value={formData.website}
                onChange={handleChange}
                placeholder="https://example.com"
              />
            </div>

            <div className="col-md-6 mb-3">
              <label className="form-label">
                Email
              </label>
              <input
                type="email"
                name="email"
                className="form-control"
                value={formData.email}
                onChange={handleChange}
              />
            </div>

            <div className="col-md-6 mb-3">
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

            <div className="col-md-6 mb-3">
              <label className="form-label">
                Country
              </label>
              <input
                type="text"
                name="country"
                className="form-control"
                value={formData.country}
                onChange={handleChange}
                required
              />
            </div>

            <div className="col-md-12 mb-3">
              <label className="form-label">
                Address
              </label>
              <textarea
                rows={3}
                name="address"
                className="form-control"
                value={formData.address}
                onChange={handleChange}
              />
            </div>

            <div className="col-md-6 mb-3">
              <label className="form-label">
                City
              </label>
              <input
                type="text"
                name="city"
                className="form-control"
                value={formData.city}
                onChange={handleChange}
              />
            </div>

            <div className="col-md-6 mb-3">
              <label className="form-label">
                State
              </label>
              <input
                type="text"
                name="state"
                className="form-control"
                value={formData.state}
                onChange={handleChange}
              />
            </div>

          </div>

          <div className="mt-4">
            <button
              type="submit"
              className="btn btn-success"
              disabled={loading}
            >
              {loading ? "Saving..." : "Save Institution"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default InstitutionForm;
