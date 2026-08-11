import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getConference, updateConference } from '../../services/conferenceService';

export default function EditConference() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    acronym: '',
    name: '',
    location: '',
    impactScore: ''
  });

  useEffect(() => {
    loadConference();
  }, [id]);

  const loadConference = async () => {
    try {
      const data = await getConference(id);
      if (data) {
        setForm({
          acronym: data.acronym || '',
          name: data.name || '',
          location: data.location || '',
          impactScore: data.impactScore || '9.0/10'
        });
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await updateConference(id, form);
      alert('Conference updated successfully.');
      navigate('/conferences');
    } catch (err) {
      console.error(err);
      alert('Failed to update conference.');
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
      <div className="container" style={{ maxWidth: '700px' }}>
        <Link to="/conferences" className="btn btn-outline-secondary btn-sm text-light mb-4">
          ← Back to Conferences
        </Link>

        <div className="p-4 p-md-5 rounded-4 shadow-lg" style={{ backgroundColor: 'rgba(255, 255, 255, 0.05)', border: '1px solid rgba(255, 255, 255, 0.1)', backdropFilter: 'blur(12px)' }}>
          <h3 className="fw-bold mb-4" style={{ color: '#38bdf8' }}>Edit Conference #{id}</h3>

          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label className="form-label small text-light opacity-90 fw-semibold">Acronym</label>
              <input
                className="form-control text-white border-0 py-2 px-3"
                name="acronym"
                value={form.acronym}
                onChange={handleChange}
                style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', border: '1px solid rgba(255,255,255,0.1)' }}
                required
              />
            </div>

            <div className="mb-3">
              <label className="form-label small text-light opacity-90 fw-semibold">Conference Name</label>
              <input
                className="form-control text-white border-0 py-2 px-3"
                name="name"
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
                  value={form.impactScore}
                  onChange={handleChange}
                  style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>
            </div>

            <div className="d-flex gap-3 mt-4">
              <button className="btn btn-warning fw-bold px-4" type="submit" disabled={saving}>
                {saving ? 'Updating...' : 'Update Conference'}
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
