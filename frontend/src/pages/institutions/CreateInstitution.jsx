import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { createInstitution } from '../../services/institutionService';

export default function CreateInstitution() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    name: '',
    abbreviation: '',
    city: '',
    state: '',
    country: 'India',
    email: '',
    phone: '',
    website: '',
    address: ''
  });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await createInstitution(form);
      alert('Institution created successfully.');
      navigate('/institutions');
    } catch (err) {
      console.error(err);
      alert('Failed to create institution.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ background: 'linear-gradient(135deg, #0f172a 0%, #172554 100%)', minHeight: '100vh', color: '#f8fafc', padding: '2.5rem 1rem' }}>
      <div className="container" style={{ maxWidth: '800px' }}>
        <Link to="/institutions" className="btn btn-outline-secondary btn-sm text-light mb-4">
          ← Back to Institutions
        </Link>

        <div className="p-4 p-md-5 rounded-4 shadow-lg" style={{ backgroundColor: 'rgba(255, 255, 255, 0.05)', border: '1px solid rgba(255, 255, 255, 0.1)', backdropFilter: 'blur(12px)' }}>
          <h3 className="fw-bold mb-4" style={{ color: '#38bdf8' }}>Register New Institution</h3>

          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label className="form-label small text-light opacity-90 fw-semibold">Institution Name</label>
              <input
                className="form-control text-white border-0 py-2 px-3"
                name="name"
                value={form.name}
                onChange={handleChange}
                placeholder="e.g. Indian Institute of Technology Bombay"
                style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', border: '1px solid rgba(255,255,255,0.1)' }}
                required
              />
            </div>

            <div className="row g-3 mb-3">
              <div className="col-md-6">
                <label className="form-label small text-light opacity-90 fw-semibold">Abbreviation</label>
                <input
                  className="form-control text-white border-0 py-2 px-3"
                  name="abbreviation"
                  value={form.abbreviation}
                  onChange={handleChange}
                  placeholder="e.g. IITB"
                  style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>

              <div className="col-md-6">
                <label className="form-label small text-light opacity-90 fw-semibold">Website</label>
                <input
                  className="form-control text-white border-0 py-2 px-3"
                  name="website"
                  value={form.website}
                  onChange={handleChange}
                  placeholder="www.iitb.ac.in"
                  style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>
            </div>

            <div className="row g-3 mb-3">
              <div className="col-md-4">
                <label className="form-label small text-light opacity-90 fw-semibold">City</label>
                <input
                  className="form-control text-white border-0 py-2 px-3"
                  name="city"
                  value={form.city}
                  onChange={handleChange}
                  style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>

              <div className="col-md-4">
                <label className="form-label small text-light opacity-90 fw-semibold">State</label>
                <input
                  className="form-control text-white border-0 py-2 px-3"
                  name="state"
                  value={form.state}
                  onChange={handleChange}
                  style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>

              <div className="col-md-4">
                <label className="form-label small text-light opacity-90 fw-semibold">Country</label>
                <input
                  className="form-control text-white border-0 py-2 px-3"
                  name="country"
                  value={form.country}
                  onChange={handleChange}
                  style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>
            </div>

            <div className="row g-3 mb-4">
              <div className="col-md-6">
                <label className="form-label small text-light opacity-90 fw-semibold">Email</label>
                <input
                  type="email"
                  className="form-control text-white border-0 py-2 px-3"
                  name="email"
                  value={form.email}
                  onChange={handleChange}
                  style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>

              <div className="col-md-6">
                <label className="form-label small text-light opacity-90 fw-semibold">Phone</label>
                <input
                  className="form-control text-white border-0 py-2 px-3"
                  name="phone"
                  value={form.phone}
                  onChange={handleChange}
                  style={{ backgroundColor: 'rgba(15, 23, 42, 0.7)', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>
            </div>

            <div className="d-flex gap-3">
              <button className="btn btn-primary fw-bold px-4" type="submit" disabled={loading} style={{ backgroundColor: '#0284c7', border: 'none' }}>
                {loading ? 'Submitting...' : 'Register Institution'}
              </button>
              <button type="button" className="btn btn-outline-light px-4" onClick={() => navigate('/institutions')}>
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
