import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getConference } from '../../services/conferenceService';

export default function ConferenceDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [conference, setConference] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadConference();
  }, [id]);

  const loadConference = async () => {
    try {
      const data = await getConference(id);
      setConference(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ backgroundColor: '#0f172a', minHeight: '100vh', color: '#f8fafc' }} className="d-flex align-items-center justify-content-center">
        <div className="spinner-border text-info" role="status"></div>
      </div>
    );
  }

  if (!conference) {
    return (
      <div style={{ backgroundColor: '#0f172a', minHeight: '100vh', color: '#f8fafc' }} className="container py-5">
        <div className="alert alert-danger">Conference not found.</div>
        <Link to="/conferences" className="btn btn-outline-light">Back to Conferences</Link>
      </div>
    );
  }

  return (
    <div style={{ background: 'linear-gradient(135deg, #0f172a 0%, #172554 100%)', minHeight: '100vh', color: '#f8fafc', padding: '2.5rem 1rem' }}>
      <div className="container" style={{ maxWidth: '800px' }}>
        <button className="btn btn-outline-secondary btn-sm text-light mb-4" onClick={() => navigate('/conferences')}>
          ← Back to Conferences
        </button>

        <div className="p-4 p-md-5 rounded-4 shadow-lg" style={{ backgroundColor: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)' }}>
          <span className="badge px-3 py-2 fw-bold mb-3 d-inline-block" style={{ backgroundColor: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8', border: '1px solid rgba(56, 189, 248, 0.3)' }}>
            {conference.acronym}
          </span>

          <h2 className="fw-bold text-white mb-3">{conference.name}</h2>
          <p className="text-light opacity-75 mb-3">📍 Location: {conference.location}</p>
          <p className="text-success fw-bold mb-4">⭐ Impact Score: {conference.impactScore}</p>

          <div className="d-flex gap-3 pt-3" style={{ borderTop: '1px solid rgba(255,255,255,0.1)' }}>
            <Link to={`/conferences/${conference.id}/edit`} className="btn btn-warning fw-bold px-4">
              ✏️ Edit Venue
            </Link>
            <button className="btn btn-outline-info fw-bold" onClick={() => alert(`Opening website for ${conference.acronym}`)}>
              🌐 Visit Official Site
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
