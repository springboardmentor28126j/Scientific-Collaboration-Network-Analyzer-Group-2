import React, { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { getPublication, downloadPublication } from "../../services/publicationService";

export default function PublicationDetails() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [publication, setPublication] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPublication();
  }, [id]);

  const loadPublication = async () => {
    try {
      const data = await getPublication(id);
      setPublication(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    try {
      const response = await downloadPublication(id);
      const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
      const link = document.createElement("a");
      link.href = url;
      link.download = publication?.file_name || `Publication_${id}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
      alert("Download failed.");
    }
  };

  if (loading) {
    return (
      <div style={{ backgroundColor: '#0f172a', minHeight: '100vh', color: '#f8fafc' }} className="d-flex align-items-center justify-content-center">
        <div className="spinner-border text-info" role="status"></div>
      </div>
    );
  }

  if (!publication) {
    return (
      <div style={{ backgroundColor: '#0f172a', minHeight: '100vh', color: '#f8fafc' }} className="container py-5">
        <div className="alert alert-danger">Publication not found.</div>
        <Link to="/publications" className="btn btn-outline-light">Back to Publications</Link>
      </div>
    );
  }

  return (
    <div style={{ backgroundColor: '#0f172a', minHeight: '100vh', color: '#f8fafc', padding: '2.5rem 1rem' }}>
      <div className="container" style={{ maxWidth: '900px' }}>
        <button className="btn btn-outline-secondary text-light btn-sm mb-4" onClick={() => navigate('/publications')}>
          ← Back to Publications
        </button>

        <div className="p-4 p-md-5 rounded-4 shadow-lg" style={{ backgroundColor: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)' }}>
          <div className="d-flex gap-2 mb-3">
            <span className="badge bg-primary">Year: {publication.publication_year || publication.year || 2024}</span>
            <span className="badge bg-success">Citations: {publication.citation_count || publication.citations || 0}</span>
            {publication.publication_type && <span className="badge bg-info text-dark">{publication.publication_type}</span>}
          </div>

          <h2 className="fw-bold text-white mb-3">{publication.title}</h2>
          
          <p className="text-info fw-semibold mb-2">
            ✍️ Authors: {Array.isArray(publication.authors) ? publication.authors.join(', ') : (publication.authors || 'N/A')}
          </p>
          <p className="text-light opacity-75 small mb-4">
            📖 Journal: <em>{publication.journal || 'N/A'}</em> | DOI: {publication.doi || 'N/A'}
          </p>

          <hr style={{ borderColor: 'rgba(255,255,255,0.1)' }} />

          <h5 className="fw-bold text-white mt-4 mb-2">Abstract</h5>
          <p className="text-light opacity-75 lh-lg">{publication.abstract || 'No abstract provided.'}</p>

          <div className="d-flex gap-3 mt-4 pt-3 flex-wrap" style={{ borderTop: '1px solid rgba(255,255,255,0.1)' }}>
            <button className="btn btn-primary fw-bold" onClick={handleDownload} style={{ backgroundColor: '#2563eb', border: 'none' }}>
              📄 Download PDF
            </button>
            <Link to={`/publications/${publication.id}/edit`} className="btn btn-warning fw-bold">
              ✏️ Edit Paper
            </Link>
            <button className="btn btn-outline-info fw-bold" onClick={() => alert('Citation copied to clipboard!')}>
              🔗 Cite Paper
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}