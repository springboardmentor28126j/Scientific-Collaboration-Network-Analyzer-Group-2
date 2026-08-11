import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { createPublication, uploadPublication } from "../../services/publicationService";

export default function CreatePublication() {
  const navigate = useNavigate();
  const [pdf, setPdf] = useState(null);
  const [loading, setLoading] = useState(false);

  const [form, setForm] = useState({
    title: "",
    abstract: "",
    doi: "",
    journal: "",
    conference: "",
    publication_year: new Date().getFullYear(),
    publication_type: "Journal Article",
    status: "Published",
    url: "",
    citation_count: 0,
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm({
      ...form,
      [name]: name === "citation_count" || name === "publication_year" ? Number(value) : value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const publication = await createPublication(form);
      if (pdf && publication?.id) {
        await uploadPublication(publication.id, pdf);
      }
      alert("Publication created successfully.");
      navigate("/publications");
    } catch (err) {
      console.error(err);
      alert("Failed to create publication.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ background: 'linear-gradient(135deg, #0f172a 0%, #172554 100%)', minHeight: '100vh', color: '#f8fafc', padding: '2.5rem 1rem' }}>
      <div className="container" style={{ maxWidth: '800px' }}>
        
        <Link to="/publications" className="btn btn-outline-secondary btn-sm text-light mb-4">
          ← Back to Publications
        </Link>

        <div className="p-4 p-md-5 rounded-4 shadow-lg" style={{ backgroundColor: 'rgba(255, 255, 255, 0.05)', border: '1px solid rgba(255, 255, 255, 0.1)', backdropFilter: 'blur(12px)' }}>
          <h3 className="fw-bold mb-4" style={{ color: '#38bdf8' }}>Create New Publication</h3>

          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label className="form-label small text-light opacity-90 fw-semibold">Publication Title</label>
              <input
                className="form-control text-white border-0 py-2 px-3"
                name="title"
                value={form.title}
                onChange={handleChange}
                placeholder="Enter paper title"
                style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', border: '1px solid rgba(255,255,255,0.1)' }}
                required
              />
            </div>

            <div className="mb-3">
              <label className="form-label small text-light opacity-90 fw-semibold">Abstract</label>
              <textarea
                className="form-control text-white border-0 py-2 px-3"
                rows="4"
                name="abstract"
                value={form.abstract}
                onChange={handleChange}
                placeholder="Brief summary of research..."
                style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', border: '1px solid rgba(255,255,255,0.1)' }}
                required
              />
            </div>

            <div className="row g-3 mb-3">
              <div className="col-md-6">
                <label className="form-label small text-light opacity-90 fw-semibold">DOI</label>
                <input
                  className="form-control text-white border-0 py-2 px-3"
                  name="doi"
                  value={form.doi}
                  onChange={handleChange}
                  placeholder="10.1000/182"
                  style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>

              <div className="col-md-6">
                <label className="form-label small text-light opacity-90 fw-semibold">Journal</label>
                <input
                  className="form-control text-white border-0 py-2 px-3"
                  name="journal"
                  value={form.journal}
                  onChange={handleChange}
                  placeholder="e.g. IEEE TKDE"
                  style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>
            </div>

            <div className="row g-3 mb-3">
              <div className="col-md-6">
                <label className="form-label small text-light opacity-90 fw-semibold">Conference</label>
                <input
                  className="form-control text-white border-0 py-2 px-3"
                  name="conference"
                  value={form.conference}
                  onChange={handleChange}
                  placeholder="e.g. KDD 2024"
                  style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>

              <div className="col-md-6">
                <label className="form-label small text-light opacity-90 fw-semibold">Publication Year</label>
                <input
                  type="number"
                  className="form-control text-white border-0 py-2 px-3"
                  name="publication_year"
                  value={form.publication_year}
                  onChange={handleChange}
                  style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>
            </div>

            <div className="row g-3 mb-3">
              <div className="col-md-6">
                <label className="form-label small text-light opacity-90 fw-semibold">Publication Type</label>
                <select
                  className="form-select text-white border-0 py-2 px-3"
                  name="publication_type"
                  value={form.publication_type}
                  onChange={handleChange}
                  style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)' }}
                >
                  <option value="Journal Article">Journal Article</option>
                  <option value="Conference Paper">Conference Paper</option>
                  <option value="Survey Article">Survey Article</option>
                  <option value="Review">Review</option>
                </select>
              </div>

              <div className="col-md-6">
                <label className="form-label small text-light opacity-90 fw-semibold">Citation Count</label>
                <input
                  type="number"
                  className="form-control text-white border-0 py-2 px-3"
                  name="citation_count"
                  value={form.citation_count}
                  onChange={handleChange}
                  style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>
            </div>

            <div className="mb-4">
              <label className="form-label small text-light opacity-90 fw-semibold">Upload PDF Document</label>
              <input
                type="file"
                accept=".pdf"
                className="form-control text-white border-0 py-2 px-3"
                onChange={(e) => setPdf(e.target.files[0])}
                style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', border: '1px solid rgba(255,255,255,0.1)' }}
              />
            </div>

            <div className="d-flex gap-3">
              <button className="btn btn-primary fw-bold px-4" type="submit" disabled={loading} style={{ backgroundColor: '#0284c7', border: 'none' }}>
                {loading ? 'Creating...' : 'Save Publication'}
              </button>
              <button type="button" className="btn btn-outline-light px-4" onClick={() => navigate("/publications")}>
                Cancel
              </button>
            </div>
          </form>
        </div>

      </div>
    </div>
  );
}
