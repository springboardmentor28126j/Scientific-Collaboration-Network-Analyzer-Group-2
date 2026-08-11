import React, { useEffect, useState } from "react";
import { useNavigate, useParams, Link } from "react-router-dom";
import { getPublication, updatePublication, uploadPublication } from "../../services/publicationService";

export default function EditPublication() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [pdf, setPdf] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [form, setForm] = useState({
    title: "",
    abstract: "",
    doi: "",
    journal: "",
    conference: "",
    publication_year: "",
    publication_type: "",
    status: "",
    url: "",
    citation_count: 0,
  });

  useEffect(() => {
    loadPublication();
  }, [id]);

  const loadPublication = async () => {
    try {
      const pub = await getPublication(id);
      if (pub) {
        setForm({
          title: pub.title || "",
          abstract: pub.abstract || "",
          doi: pub.doi || "",
          journal: pub.journal || "",
          conference: pub.conference || "",
          publication_year: pub.publication_year || pub.year || "",
          publication_type: pub.publication_type || "Journal Article",
          status: pub.status || "Published",
          url: pub.url || "",
          citation_count: pub.citation_count || pub.citations || 0,
        });
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm({
      ...form,
      [name]: name === "publication_year" || name === "citation_count" ? Number(value) : value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);

    try {
      await updatePublication(id, form);
      if (pdf) {
        await uploadPublication(id, pdf);
      }
      alert("Publication updated successfully.");
      navigate("/publications");
    } catch (err) {
      console.error(err);
      alert("Failed to update publication.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div style={{ backgroundColor: '#0f172a', minHeight: '100vh', color: '#f8fafc' }} className="d-flex align-items-center justify-content-center">
        <div className="spinner-border text-info" role="status"></div>
      </div>
    );
  }

  return (
    <div style={{ background: 'linear-gradient(135deg, #0f172a 0%, #172554 100%)', minHeight: '100vh', color: '#f8fafc', padding: '2.5rem 1rem' }}>
      <div className="container" style={{ maxWidth: '800px' }}>
        
        <Link to="/publications" className="btn btn-outline-secondary btn-sm text-light mb-4">
          ← Back to Publications
        </Link>

        <div className="p-4 p-md-5 rounded-4 shadow-lg" style={{ backgroundColor: 'rgba(255, 255, 255, 0.05)', border: '1px solid rgba(255, 255, 255, 0.1)', backdropFilter: 'blur(12px)' }}>
          <h3 className="fw-bold mb-4" style={{ color: '#38bdf8' }}>Edit Publication #{id}</h3>

          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label className="form-label small text-light opacity-90 fw-semibold">Title</label>
              <input
                className="form-control text-white border-0 py-2 px-3"
                name="title"
                value={form.title}
                onChange={handleChange}
                style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', border: '1px solid rgba(255,255,255,0.1)' }}
                required
              />
            </div>

            <div className="mb-3">
              <label className="form-label small text-light opacity-90 fw-semibold">Abstract</label>
              <textarea
                rows="4"
                className="form-control text-white border-0 py-2 px-3"
                name="abstract"
                value={form.abstract}
                onChange={handleChange}
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

              <div className="col-md-6">
                <label className="form-label small text-light opacity-90 fw-semibold">Replace PDF Document</label>
                <input
                  type="file"
                  accept=".pdf"
                  className="form-control text-white border-0 py-2 px-3"
                  onChange={(e) => setPdf(e.target.files[0])}
                  style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>
            </div>

            <div className="d-flex gap-3 mt-4">
              <button className="btn btn-warning fw-bold px-4" type="submit" disabled={saving}>
                {saving ? 'Updating...' : 'Update Publication'}
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
