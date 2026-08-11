import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { createResearcher } from '../../services/researcherService';

export default function CreateResearcher() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    name: '',
    title: '',
    institution: '',
    domain: '',
    email: '',
    bio: '',
    hIndex: 10,
    i10Index: 12,
    totalCitations: 0,
    totalPapers: 0
  });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await createResearcher(form);
      alert('Researcher profile created successfully.');
      navigate('/researchers');
    } catch (err) {
      console.error(err);
      alert('Failed to create researcher profile.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ background: 'linear-gradient(135deg, #0f172a 0%, #172554 100%)', minHeight: '100vh', color: '#f8fafc', padding: '2.5rem 1rem' }}>
      <div className="container" style={{ maxWidth: '800px' }}>
        <Link to="/researchers" className="btn btn-outline-secondary btn-sm text-light mb-4">
          ← Back to Researchers
        </Link>

        <div className="p-4 p-md-5 rounded-4 shadow-lg" style={{ backgroundColor: 'rgba(255, 255, 255, 0.05)', border: '1px solid rgba(255, 255, 255, 0.1)', backdropFilter: 'blur(12px)' }}>
          <h3 className="fw-bold mb-4" style={{ color: '#38bdf8' }}>Create Researcher Profile</h3>

          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label className="form-label small text-light opacity-90 fw-semibold">Full Name</label>
              <input
                className="form-control text-white border-0 py-2 px-3"
                name="name"
                value={form.name}
                onChange={handleChange}
                placeholder="e.g. Dr. Aravind Sharma"
                style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', border: '1px solid rgba(255,255,255,0.1)' }}
                required
              />
            </div>

            <div className="row g-3 mb-3">
              <div className="col-md-6">
                <label className="form-label small text-light opacity-90 fw-semibold">Title / Designation</label>
                <input
                  className="form-control text-white border-0 py-2 px-3"
                  name="title"
                  value={form.title}
                  onChange={handleChange}
                  placeholder="e.g. Senior Professor"
                  style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>

              <div className="col-md-6">
                <label className="form-label small text-light opacity-90 fw-semibold">Institution / University</label>
                <input
                  className="form-control text-white border-0 py-2 px-3"
                  name="institution"
                  value={form.institution}
                  onChange={handleChange}
                  placeholder="e.g. IIT Bombay"
                  style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>
            </div>

            <div className="row g-3 mb-3">
              <div className="col-md-6">
                <label className="form-label small text-light opacity-90 fw-semibold">Research Domain</label>
                <input
                  className="form-control text-white border-0 py-2 px-3"
                  name="domain"
                  value={form.domain}
                  onChange={handleChange}
                  placeholder="e.g. Artificial Intelligence"
                  style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>

              <div className="col-md-6">
                <label className="form-label small text-light opacity-90 fw-semibold">Email</label>
                <input
                  type="email"
                  className="form-control text-white border-0 py-2 px-3"
                  name="email"
                  value={form.email}
                  onChange={handleChange}
                  placeholder="researcher@university.edu"
                  style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>
            </div>

            <div className="mb-3">
              <label className="form-label small text-light opacity-90 fw-semibold">Biography</label>
              <textarea
                className="form-control text-white border-0 py-2 px-3"
                rows="3"
                name="bio"
                value={form.bio}
                onChange={handleChange}
                placeholder="Brief academic biography..."
                style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', border: '1px solid rgba(255,255,255,0.1)' }}
              />
            </div>

            <div className="d-flex gap-3 mt-4">
              <button className="btn btn-primary fw-bold px-4" type="submit" disabled={loading} style={{ backgroundColor: '#0284c7', border: 'none' }}>
                {loading ? 'Submitting...' : 'Create Profile'}
              </button>
              <button type="button" className="btn btn-outline-light px-4" onClick={() => navigate('/researchers')}>
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
