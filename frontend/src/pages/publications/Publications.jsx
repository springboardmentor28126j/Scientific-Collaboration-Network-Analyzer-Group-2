import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getPublications } from '../../services/publicationService';

export default function Publications() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedYear, setSelectedYear] = useState('All');
  const [publicationsList, setPublicationsList] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPublications();
  }, []);

  const fetchPublications = async () => {
    try {
      const data = await getPublications();
      setPublicationsList(data);
    } catch (err) {
      console.error('Error fetching publications:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredPublications = publicationsList.filter(p => {
    const title = p.title || '';
    const authors = Array.isArray(p.authors) ? p.authors.join(', ') : (p.authors || '');
    const journal = p.journal || '';
    const year = (p.publication_year || p.year || '').toString();

    const matchesSearch = title.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          authors.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          journal.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesYear = selectedYear === 'All' || year === selectedYear;
    return matchesSearch && matchesYear;
  });

  return (
    <div style={{ background: 'linear-gradient(135deg, #0f172a 0%, #172554 100%)', minHeight: '100vh', color: '#f8fafc', padding: '2.5rem 1rem' }}>
      <div className="container" style={{ maxWidth: '1100px' }}>
        
        {/* Header */}
        <div className="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-3">
          <div>
            <h2 className="fw-bold mb-1" style={{ color: '#38bdf8' }}>Publications Directory</h2>
            <p className="text-light opacity-75 mb-0">Browse research papers, citation metrics, and co-authorship details.</p>
          </div>
          <Link to="/publications/create" className="btn btn-primary fw-bold px-4 shadow-sm" style={{ backgroundColor: '#2563eb', border: 'none' }}>
            + Add Publication
          </Link>
        </div>

        {/* Filter Bar */}
        <div className="p-3 mb-4 rounded-4 shadow-lg" style={{ backgroundColor: 'rgba(255, 255, 255, 0.05)', border: '1px solid rgba(255, 255, 255, 0.1)', backdropFilter: 'blur(10px)' }}>
          <div className="row g-3">
            <div className="col-md-7">
              <input 
                type="text" 
                className="form-control text-white border-0 shadow-none py-2 px-3" 
                placeholder="Search by title, author, or journal name..." 
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                style={{ backgroundColor: 'rgba(15, 23, 42, 0.6)', border: '1px solid rgba(255,255,255,0.1)' }}
              />
            </div>
            <div className="col-md-3">
              <select 
                className="form-select text-white border-0 shadow-none py-2 px-3"
                value={selectedYear}
                onChange={(e) => setSelectedYear(e.target.value)}
                style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)' }}
              >
                <option value="All" style={{ backgroundColor: '#0f172a' }}>All Years</option>
                <option value="2024" style={{ backgroundColor: '#0f172a' }}>2024</option>
                <option value="2023" style={{ backgroundColor: '#0f172a' }}>2023</option>
                <option value="2022" style={{ backgroundColor: '#0f172a' }}>2022</option>
              </select>
            </div>
            <div className="col-md-2">
              <button 
                className="btn btn-outline-light w-100 opacity-75 py-2" 
                onClick={() => { setSearchTerm(''); setSelectedYear('All'); }}
              >
                Reset
              </button>
            </div>
          </div>
        </div>

        {/* Loading Indicator */}
        {loading ? (
          <div className="text-center py-5">
            <div className="spinner-border text-info" role="status"></div>
            <p className="mt-2 text-light opacity-75">Loading publications...</p>
          </div>
        ) : (
          /* Publications List */
          <div className="d-flex flex-column gap-3">
            {filteredPublications.map((pub) => (
              <div key={pub.id} className="p-4 rounded-4 shadow-lg" style={{ backgroundColor: 'rgba(255, 255, 255, 0.05)', border: '1px solid rgba(255, 255, 255, 0.08)', backdropFilter: 'blur(8px)' }}>
                <div className="d-flex justify-content-between align-items-start flex-wrap gap-3">
                  <div style={{ flex: '1 1 300px' }}>
                    <h5 className="fw-bold mb-2" style={{ color: '#38bdf8' }}>{pub.title}</h5>
                    <p className="small mb-3" style={{ color: '#cbd5e1' }}>
                      <strong className="text-white">Authors:</strong> {Array.isArray(pub.authors) ? pub.authors.join(', ') : (pub.authors || 'N/A')} | <strong className="text-white">Journal:</strong> <em>{pub.journal || 'N/A'}</em>
                    </p>
                    <div className="d-flex gap-2 align-items-center flex-wrap">
                      <span className="badge px-3 py-2 fw-semibold" style={{ backgroundColor: 'rgba(255,255,255,0.1)', color: '#f8fafc', border: '1px solid rgba(255,255,255,0.15)' }}>
                        Year: {pub.publication_year || pub.year || 'N/A'}
                      </span>
                      <span className="badge px-3 py-2 fw-semibold" style={{ backgroundColor: 'rgba(52, 211, 153, 0.15)', color: '#34d399', border: '1px solid rgba(52, 211, 153, 0.3)' }}>
                        Citations: {pub.citation_count || pub.citations || 0}
                      </span>
                    </div>
                  </div>
                  
                  <div className="d-flex gap-2 align-self-center">
                    <Link to={`/publications/${pub.id}`} className="btn btn-sm btn-outline-info text-nowrap px-3 py-2 fw-semibold">
                      View Paper →
                    </Link>
                    <Link to={`/publications/${pub.id}/edit`} className="btn btn-sm btn-outline-warning text-nowrap px-3 py-2 fw-semibold">
                      Edit
                    </Link>
                  </div>
                </div>
              </div>
            ))}

            {filteredPublications.length === 0 && (
              <div className="text-center py-5 rounded-4" style={{ backgroundColor: 'rgba(255,255,255,0.02)', border: '1px dashed rgba(255,255,255,0.1)' }}>
                <p className="text-light opacity-50 mb-0">No publications found matching criteria.</p>
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
}
