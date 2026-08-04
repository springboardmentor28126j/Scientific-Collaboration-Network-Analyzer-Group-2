import { useEffect, useState } from "react";

function CitationForm({
  initialData = {},
  publications = [],
  onSubmit,
  loading = false,
}) {
  const [formData, setFormData] = useState({
    publication_id: "",
    title: "",
    authors: "",
    journal: "",
    year: "",
    volume: "",
    issue: "",
    pages: "",
    doi: "",
    url: "",
    citation_style: "APA",
  });

  useEffect(() => {
    if (initialData) {
      setFormData({
        publication_id: initialData.publication_id || "",
        title: initialData.title || "",
        authors: initialData.authors || "",
        journal: initialData.journal || "",
        year: initialData.year || "",
        volume: initialData.volume || "",
        issue: initialData.issue || "",
        pages: initialData.pages || "",
        doi: initialData.doi || "",
        url: initialData.url || "",
        citation_style:
          initialData.citation_style || "APA",
      });
    }
  }, [initialData]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="card shadow">

      <div className="card-header bg-primary text-white">
        <h4 className="mb-0">
          Citation Information
        </h4>
      </div>

      <div className="card-body">

        <form onSubmit={handleSubmit}>

          <div className="row">

            <div className="col-md-12 mb-3">
              <label className="form-label">
                Publication
              </label>

              <select
                className="form-select"
                name="publication_id"
                value={formData.publication_id}
                onChange={handleChange}
                required
              >
                <option value="">
                  Select Publication
                </option>

                {publications.map((publication) => (
                  <option
                    key={publication.id}
                    value={publication.id}
                  >
                    {publication.title}
                  </option>
                ))}
              </select>

            </div>

            <div className="col-md-12 mb-3">
              <label className="form-label">
                Title
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

            <div className="col-md-12 mb-3">
              <label className="form-label">
                Authors
              </label>

              <input
                type="text"
                className="form-control"
                name="authors"
                value={formData.authors}
                onChange={handleChange}
                placeholder="John Doe, Jane Smith"
                required
              />
            </div>

            <div className="col-md-6 mb-3">
              <label className="form-label">
                Journal
              </label>

              <input
                type="text"
                className="form-control"
                name="journal"
                value={formData.journal}
                onChange={handleChange}
              />
            </div>

            <div className="col-md-6 mb-3">
              <label className="form-label">
                Year
              </label>

              <input
                type="number"
                className="form-control"
                name="year"
                value={formData.year}
                onChange={handleChange}
                required
              />
            </div>

            <div className="col-md-4 mb-3">
              <label className="form-label">
                Volume
              </label>

              <input
                type="text"
                className="form-control"
                name="volume"
                value={formData.volume}
                onChange={handleChange}
              />
            </div>

            <div className="col-md-4 mb-3">
              <label className="form-label">
                Issue
              </label>

              <input
                type="text"
                className="form-control"
                name="issue"
                value={formData.issue}
                onChange={handleChange}
              />
            </div>

            <div className="col-md-4 mb-3">
              <label className="form-label">
                Pages
              </label>

              <input
                type="text"
                className="form-control"
                name="pages"
                value={formData.pages}
                onChange={handleChange}
              />
            </div>

            <div className="col-md-6 mb-3">
              <label className="form-label">
                DOI
              </label>

              <input
                type="text"
                className="form-control"
                name="doi"
                value={formData.doi}
                onChange={handleChange}
              />
            </div>

            <div className="col-md-6 mb-3">
              <label className="form-label">
                URL
              </label>

              <input
                type="url"
                className="form-control"
                name="url"
                value={formData.url}
                onChange={handleChange}
              />
            </div>

            <div className="col-md-6 mb-3">
              <label className="form-label">
                Citation Style
              </label>

              <select
                className="form-select"
                name="citation_style"
                value={formData.citation_style}
                onChange={handleChange}
              >
                <option value="APA">APA</option>
                <option value="IEEE">IEEE</option>
                <option value="MLA">MLA</option>
                <option value="Chicago">Chicago</option>
                <option value="Harvard">Harvard</option>
              </select>
            </div>

          </div>

          <div className="mt-4">
            <button
              type="submit"
              className="btn btn-success"
              disabled={loading}
            >
              {loading
                ? "Saving..."
                : "Save Citation"}
            </button>
          </div>

        </form>

      </div>

    </div>
  );
}

export default CitationForm;
