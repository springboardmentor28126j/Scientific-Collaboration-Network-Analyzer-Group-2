import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getInstitutions } from '../../services/institutionService';

export default function Institutions() {
  const [searchTerm, setSearchTerm] = useState('');
  const [institutionsList, setInstitutionsList] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchInstitutions();
  }, []);

  const fetchInstitutions = async () => {
    try {
      const data = await getInstitutions();
      setInstitutionsList(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const filtered = institutionsList.filter(inst => {
    const name = inst.name || '';
    const location = `${inst.city || ''} ${inst.location || ''} ${inst.country || ''}`;
    return name.toLowerCase().includes(searchTerm.toLowerCase()) ||
           location.toLowerCase().includes(searchTerm.toLowerCase());
  });

  return (
    <div style={{ background: 'linear-gradient(135deg, #0f172a 0%, #172554 100%)', minHeight: '100vh', color: '#f8fafc', padding: '2.5rem 1rem' }}>
      <div className="container" style={{ maxWidth: '1100px' }}>
        
        {/* Header */}
        <div className="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-3">
          <div>
            <h2 className="fw-bold mb-1" style={{ color: '#38bdf8' }}>Institutions Directory</h2>
            <p className="text-light opacity-75 mb-0">Explore collaborating universities and research centers.</p>
          </div>
          <Link to="/institutions/create" className="btn btn-primary fw-bold px-4 shadow-sm" style={{ backgroundColor: '#2563eb', border: 'none' }}>
            + Add Institution
          </Link>
        </div>

        {/* Filter / Search Bar */}
        <div className="p-3 mb-4 rounded-4 shadow-lg" style={{ backgroundColor: 'rgba(255, 255, 255, 0.05)', border: '1px solid rgba(255, 255, 255, 0.1)', backdropFilter: 'blur(10px)' }}>
          <input 
            type="text" 
            className="form-control text-white border-0 shadow-none py-2 px-3" 
            placeholder="Search institution or location..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ backgroundColor: 'rgba(15, 23, 42, 0.6)', border: '1px solid rgba(255,255,255,0.1)' }}
          />
        </div>

        {/* Loading */}
        {loading ? (
          <div className="text-center py-5">
            <div className="spinner-border text-info" role="status"></div>
          </div>
        ) : (
          /* Institutions Grid */
          <div className="row g-4">
            {filtered.map((inst) => (
              <div key={inst.id} className="col-md-6">
                <div 
                  className="p-4 rounded-4 shadow-lg h-100 d-flex flex-column justify-content-between" 
                  style={{ 
                    backgroundColor: 'rgba(255, 255, 255, 0.05)', 
                    border: '1px solid rgba(255, 255, 255, 0.08)', 
                    backdropFilter: 'blur(8px)',
                    transition: 'transform 0.2s ease'
                  }}
                >
                  <div>
                    <h5 className="fw-bold mb-2" style={{ color: '#38bdf8' }}>{inst.name}</h5>
                    <p className="text-light opacity-75 small mb-3">📍 {inst.city ? `${inst.city}, ${inst.country || 'India'}` : inst.location || 'India'}</p>
                  </div>

                  <div className="d-flex justify-content-between align-items-center pt-3" style={{ borderTop: '1px solid rgba(255,255,255,0.1)' }}>
                    <div>
                      <span className="text-light opacity-50 small d-block">Researchers</span>
                      <strong className="fs-6 text-white">{inst.authorsCount || 100}+</strong>
                    </div>
                    <div className="d-flex gap-2">
                      <Link to={`/institutions/${inst.id}`} className="btn btn-sm btn-outline-info">View</Link>
                      <Link to={`/institutions/${inst.id}/edit`} className="btn btn-sm btn-outline-warning">Edit</Link>
                    </div>
                  </div>
                </div>
              </div>
            ))}

            {filtered.length === 0 && (
              <div className="col-12 text-center py-5 rounded-4" style={{ backgroundColor: 'rgba(255,255,255,0.02)', border: '1px dashed rgba(255,255,255,0.1)' }}>
                <p className="text-light opacity-50 mb-0">No institutions found matching your search.</p>
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
}