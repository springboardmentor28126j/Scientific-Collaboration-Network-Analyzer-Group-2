import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { getResearchers } from '../../services/researcherService';

export default function Researchers() {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [researchersData, setResearchersData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchResearchers();
  }, []);

  const fetchResearchers = async () => {
    try {
      const data = await getResearchers();
      setResearchersData(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const filteredResearchers = researchersData.filter(r => {
    const name = r.name || '';
    const institution = r.institution || '';
    const domain = r.domain || '';
    return name.toLowerCase().includes(searchTerm.toLowerCase()) || 
           institution.toLowerCase().includes(searchTerm.toLowerCase()) ||
           domain.toLowerCase().includes(searchTerm.toLowerCase());
  });

  return (
    <div style={{ backgroundColor: '#0f172a', minHeight: '100vh', color: '#f8fafc', padding: '2rem 1rem' }}>
      <div className="container-fluid px-md-5">
        <div className="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-3">
          <div>
            <h2 className="fw-bold text-white mb-1">Researchers Directory</h2>
            <p className="text-light opacity-75 mb-0">Explore network researchers, affiliations, and citation metrics.</p>
          </div>
          <div className="d-flex gap-3 align-items-center">
            <input 
              type="text" 
              placeholder="Search by name, institution, or domain..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="form-control text-white border-0 py-2 px-3"
              style={{ maxWidth: '300px', backgroundColor: 'rgba(255,255,255,0.1)' }}
            />
            <Link to="/researchers/create" className="btn btn-primary fw-bold text-nowrap" style={{ backgroundColor: '#2563eb', border: 'none' }}>
              + Add Researcher
            </Link>
          </div>
        </div>

        {/* Loading */}
        {loading ? (
          <div className="text-center py-5">
            <div className="spinner-border text-info" role="status"></div>
          </div>
        ) : (
          <div className="row g-4">
            {filteredResearchers.map((r) => (
              <div key={r.id} className="col-md-6 col-lg-4">
                <div className="p-4 rounded-4 shadow-lg h-100 d-flex flex-column justify-content-between" style={{ backgroundColor: 'rgba(255, 255, 255, 0.05)', backdropFilter: 'blur(10px)', border: '1px solid rgba(255,255,255,0.1)' }}>
                  <div>
                    <div className="d-flex justify-content-between align-items-start mb-3">
                      <div>
                        <h5 className="fw-bold text-white mb-1">{r.name}</h5>
                        <span className="badge bg-info text-dark fw-semibold">{r.domain}</span>
                      </div>
                      <span className="text-light small opacity-75">h-index: <strong className="text-warning">{r.hIndex}</strong></span>
                    </div>
                    <p className="small text-light opacity-75 mb-3">🏢 {r.institution}</p>
                  </div>

                  <div className="d-flex justify-content-between align-items-center pt-3" style={{ borderTop: '1px solid rgba(255,255,255,0.1)' }}>
                    <div>
                      <span className="d-block text-light opacity-50 small">Citations</span>
                      <strong className="text-success fs-6">{r.citations || r.totalCitations || 0}</strong>
                    </div>
                    <div className="d-flex gap-2">
                      <button 
                        className="btn btn-outline-info btn-sm fw-semibold"
                        onClick={() => navigate(`/researchers/${r.id}`)}
                      >
                        Profile →
                      </button>
                      <button 
                        className="btn btn-outline-warning btn-sm fw-semibold"
                        onClick={() => navigate(`/researchers/${r.id}/edit`)}
                      >
                        Edit
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}