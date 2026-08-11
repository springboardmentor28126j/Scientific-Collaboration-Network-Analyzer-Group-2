import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getInstitution } from '../../services/institutionService';

export default function InstitutionDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [institution, setInstitution] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadInstitution();
  }, [id]);

  const loadInstitution = async () => {
    try {
      const data = await getInstitution(id);
      setInstitution(data);
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

  if (!institution) {
    return (
      <div style={{ backgroundColor: '#0f172a', minHeight: '100vh', color: '#f8fafc' }} className="container py-5">
        <div className="alert alert-danger">Institution not found.</div>
        <Link to="/institutions" className="btn btn-outline-light">Back to Institutions</Link>
      </div>
    );
  }

  return (
    <div style={{ background: 'linear-gradient(135deg, #0f172a 0%, #172554 100%)', minHeight: '100vh', color: '#f8fafc', padding: '2.5rem 1rem' }}>
      <div className="container" style={{ maxWidth: '900px' }}>
        <button className="btn btn-outline-secondary btn-sm text-light mb-4" onClick={() => navigate('/institutions')}>
          ← Back to Institutions
        </button>

        <div className="p-4 p-md-5 rounded-4 shadow-lg" style={{ backgroundColor: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)' }}>
          <h2 className="fw-bold text-white mb-2">{institution.name}</h2>
          <p className="text-info fw-semibold mb-3">Abbreviation: {institution.abbreviation || 'N/A'}</p>

          <table className="table table-dark table-borderless text-light opacity-90 mb-4" style={{ backgroundColor: 'transparent' }}>
            <tbody>
              <tr><th>Location:</th><td>{institution.city || ''} {institution.state || ''}, {institution.country || 'India'}</td></tr>
              <tr><th>Email:</th><td>{institution.email || 'N/A'}</td></tr>
              <tr><th>Phone:</th><td>{institution.phone || 'N/A'}</td></tr>
              <tr><th>Website:</th><td><a href={`https://${institution.website}`} target="_blank" rel="noreferrer" className="text-info">{institution.website || 'N/A'}</a></td></tr>
              <tr><th>Address:</th><td>{institution.address || 'N/A'}</td></tr>
            </tbody>
          </table>

          <div className="d-flex gap-3 pt-3" style={{ borderTop: '1px solid rgba(255,255,255,0.1)' }}>
            <Link to={`/institutions/${institution.id}/edit`} className="btn btn-warning fw-bold px-4">
              ✏️ Edit Institution
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
