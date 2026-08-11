import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { createConference } from '../../services/conferenceService';

export default function CreateConference() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    acronym: '',
    name: '',
    location: '',
    year: new Date().getFullYear(),
    impactScore: '9.0/10',
    website: ''
  });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await createConference(form);
      alert('Conference created successfully.');
      navigate('/conferences');
    } catch (err) {
      console.error(err);
      alert('Failed to create conference.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ background: 'linear-gradient(135deg, #0f172a 0%, #172554 100%)', minHeight: '100vh', color: '#f8fafc', padding: '2.5rem 1rem' }}>
      <div className="container" style={{ maxWidth: '700px' }}>
        <Link to="/conferences" className="btn btn-outline-secondary btn-sm text-light mb-4">
          ← Back to Conferences
        </Link>

        <div className="p-4 p-md-5 rounded-4 shadow-lg" style={{ backgroundColor: 'rgba(255, 255, 255, 0.05)', border: '1px solid rgba(255, 255, 255, 0.1)', backdropFilter: 'blur(12px)' }}>
          <h3 className="fw-bold mb-4" style={{ color: '#38bdf8' }}>Add New Conference / Venue</h3>

          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label className="form-label small text-light opacity-90 fw-semibold">Acronym</label>
              <input
                className="form-control text-white border-0 py-2 px-3"
                name="acronym"
                placeholder="e.g. KDD 2024"
                value={form.acronym}
                onChange={handleChange}
                style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', border: '1px solid rgba(255,255,255,0.1)' }}
                required
              />
            </div>

            <div className="mb-3">
              <label className="form-label small text-light opacity-90 fw-semibold">Full Conference Name</label>
              <input
                className="form-control text-white border-0 py-2 px-3"
                name="name"
                placeholder="e.g. ACM SIGKDD Conference on Knowledge Discovery and Data Mining"
                value={form.name}
                onChange={handleChange}
                style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', border: '1px solid rgba(255,255,255,0.1)' }}
                required
              />
            </div>

            <div className="row g-3 mb-3">
              <div className="col-md-6">
                <label className="form-label small text-light opacity-90 fw-semibold">Location</label>
                <input
                  className="form-control text-white border-0 py-2 px-3"
                  name="location"
                  placeholder="City, Country"
                  value={form.location}
                  onChange={handleChange}
                  style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>

              <div className="col-md-6">
                <label className="form-label small text-light opacity-90 fw-semibold">Impact Score</label>
                <input
                  className="form-control text-white border-0 py-2 px-3"
                  name="impactScore"
                  placeholder="e.g. 9.5/10"
                  value={form.impactScore}
                  onChange={handleChange}
                  style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>
            </div>

            <div className="d-flex gap-3 mt-4">
              <button className="btn btn-primary fw-bold px-4" type="submit" disabled={loading} style={{ backgroundColor: '#0284c7', border: 'none' }}>
                {loading ? 'Creating...' : 'Create Conference'}
              </button>
              <button type="button" className="btn btn-outline-light px-4" onClick={() => navigate('/conferences')}>
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
