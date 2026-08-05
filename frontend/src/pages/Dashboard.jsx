import React, { useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

export default function Dashboard() {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  
  const [showModal, setShowModal] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [isDragging, setIsDragging] = useState(false);

  // Toast Notification State
  const [toast, setToast] = useState({ show: false, message: '', type: 'info' });

  const triggerToast = (message, type = 'success') => {
    setToast({ show: true, message, type });
    setTimeout(() => {
      setToast({ show: false, message: '', type: 'info' });
    }, 3500);
  };

  const publicationData = [
    { year: '2020', publications: 420 },
    { year: '2021', publications: 580 },
    { year: '2022', publications: 790 },
    { year: '2023', publications: 1100 },
    { year: '2024', publications: 1450 },
  ];

  const topResearchers = [
    { rank: 1, name: "Prof. Priya Nair", institution: "IISc Bangalore", citations: 1240, hIndex: 24 },
    { rank: 2, name: "Dr. Aravind Sharma", institution: "IIT Bombay", citations: 980, hIndex: 18 },
    { rank: 3, name: "Dr. Sneha Patel", institution: "BITS Pilani", citations: 750, hIndex: 15 },
    { rank: 4, name: "Dr. Rajesh Kumar", institution: "IIT Delhi", citations: 620, hIndex: 12 },
  ];

  const handleFileChange = (file) => {
    if (file && (file.name.endsWith('.csv') || file.name.endsWith('.json'))) {
      setSelectedFile(file);
      setUploadStatus('');
    } else {
      triggerToast("Kripya sirf CSV ya JSON file upload karein.", "error");
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const handleUploadSubmit = () => {
    if (!selectedFile) return;
    setUploadStatus('uploading');

    setTimeout(() => {
      setUploadStatus('success');
      triggerToast(`Dataset '${selectedFile.name}' processed successfully!`, 'success');
      setTimeout(() => {
        setShowModal(false);
        setSelectedFile(null);
        setUploadStatus('');
      }, 1200);
    }, 1200);
  };

  return (
    <div style={{ background: 'linear-gradient(135deg, #0f172a 0%, #172554 100%)', minHeight: '100vh', color: '#f8fafc' }}>
      
      <div className="container py-4">

        {/* Header Title */}
        <div className="text-center my-4 pb-3" style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.12)' }}>
          <h2 className="fw-bold mb-1" style={{ color: '#38bdf8', letterSpacing: '-0.5px' }}>
            Scientific Collaboration Network
          </h2>
          <p className="text-light opacity-75 small mb-0">Analytics, publication trends, and researcher network density</p>
        </div>

        {/* Metric Cards */}
        <div className="row g-3 mb-4">
          <div className="col-md-3">
            <div className="p-3 rounded-3" style={{ backgroundColor: 'rgba(30, 41, 59, 0.7)', borderLeft: '4px solid #38bdf8', borderTop: '1px solid rgba(255,255,255,0.05)', borderRight: '1px solid rgba(255,255,255,0.05)', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
              <span className="text-uppercase small fw-bold text-light opacity-75">Total Authors</span>
              <h3 className="fw-bold text-white mt-1 mb-0">1,248</h3>
            </div>
          </div>
          <div className="col-md-3">
            <div className="p-3 rounded-3" style={{ backgroundColor: 'rgba(30, 41, 59, 0.7)', borderLeft: '4px solid #34d399', borderTop: '1px solid rgba(255,255,255,0.05)', borderRight: '1px solid rgba(255,255,255,0.05)', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
              <span className="text-uppercase small fw-bold text-light opacity-75">Publications</span>
              <h3 className="fw-bold text-white mt-1 mb-0">3,890</h3>
            </div>
          </div>
          <div className="col-md-3">
            <div className="p-3 rounded-3" style={{ backgroundColor: 'rgba(30, 41, 59, 0.7)', borderLeft: '4px solid #a855f7', borderTop: '1px solid rgba(255,255,255,0.05)', borderRight: '1px solid rgba(255,255,255,0.05)', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
              <span className="text-uppercase small fw-bold text-light opacity-75">Collaborations</span>
              <h3 className="fw-bold text-white mt-1 mb-0">5,120</h3>
            </div>
          </div>
          <div className="col-md-3">
            <div className="p-3 rounded-3" style={{ backgroundColor: 'rgba(30, 41, 59, 0.7)', borderLeft: '4px solid #f59e0b', borderTop: '1px solid rgba(255,255,255,0.05)', borderRight: '1px solid rgba(255,255,255,0.05)', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
              <span className="text-uppercase small fw-bold text-light opacity-75">Network Density</span>
              <h3 className="fw-bold text-white mt-1 mb-0">0.78</h3>
            </div>
          </div>
        </div>

        {/* Chart & Quick Actions */}
        <div className="row g-4 mb-4">
          <div className="col-lg-7">
            <div className="p-4 rounded-3 h-100" style={{ backgroundColor: 'rgba(30, 41, 59, 0.7)', border: '1px solid rgba(255, 255, 255, 0.08)' }}>
              <h6 className="fw-bold text-light text-uppercase mb-3" style={{ letterSpacing: '0.5px' }}>Yearly Publication Growth</h6>
              <div style={{ width: '100%', height: 260 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={publicationData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" vertical={false} />
                    <XAxis dataKey="year" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff', borderRadius: '6px' }} />
                    <Bar dataKey="publications" fill="#0284c7" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          <div className="col-lg-5">
            <div className="p-4 rounded-3 h-100 d-flex flex-column justify-content-between" style={{ backgroundColor: 'rgba(30, 41, 59, 0.7)', border: '1px solid rgba(255, 255, 255, 0.08)' }}>
              <div>
                <h6 className="fw-bold text-light text-uppercase mb-3" style={{ letterSpacing: '0.5px' }}>Quick Actions</h6>
                
                <div className="d-grid gap-3">
                  <button 
                    className="btn text-start p-3 rounded-2" 
                    style={{ backgroundColor: '#1e293b', border: '1px solid rgba(56, 189, 248, 0.3)', color: '#f8fafc', transition: 'all 0.2s' }}
                    onClick={() => navigate('/researchers')}
                  >
                    <div className="fw-bold text-info">Search Researchers</div>
                    <div className="small text-light opacity-75">Filter network by domain, institution, or citations</div>
                  </button>

                  <button 
                    className="btn text-start p-3 rounded-2" 
                    style={{ backgroundColor: '#1e293b', border: '1px solid rgba(56, 189, 248, 0.3)', color: '#f8fafc', transition: 'all 0.2s' }}
                    onClick={() => setShowModal(true)}
                  >
                    <div className="fw-bold text-info">Upload Dataset</div>
                    <div className="small text-light opacity-75">Import CSV/JSON co-authorship datasets</div>
                  </button>

                  <button 
                    className="btn text-start p-3 rounded-2" 
                    style={{ backgroundColor: '#1e293b', border: '1px solid rgba(56, 189, 248, 0.3)', color: '#f8fafc', transition: 'all 0.2s' }}
                    onClick={() => navigate('/reports')}
                  >
                    <div className="fw-bold text-info">Export Analytics Report</div>
                    <div className="small text-light opacity-75">Access report dashboard and download PDF/CSV</div>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Leaderboard Table */}
        <div className="p-4 rounded-3 mb-4" style={{ backgroundColor: 'rgba(30, 41, 59, 0.85)', border: '1px solid rgba(255, 255, 255, 0.08)' }}>
          <h6 className="fw-bold text-light text-uppercase mb-3" style={{ letterSpacing: '0.5px' }}>Top Impact Researchers</h6>
          <div className="table-responsive">
            <table className="table align-middle mb-0" style={{ color: '#f8fafc', borderColor: 'rgba(255,255,255,0.1)' }}>
              <thead>
                <tr className="small" style={{ color: '#94a3b8', borderBottom: '1px solid rgba(255,255,255,0.15)' }}>
                  <th className="pb-3" style={{ background: 'transparent' }}>RANK</th>
                  <th className="pb-3" style={{ background: 'transparent' }}>RESEARCHER</th>
                  <th className="pb-3" style={{ background: 'transparent' }}>INSTITUTION</th>
                  <th className="pb-3" style={{ background: 'transparent' }}>CITATIONS</th>
                  <th className="pb-3" style={{ background: 'transparent' }}>H-INDEX</th>
                </tr>
              </thead>
              <tbody>
                {topResearchers.map((r) => (
                  <tr key={r.rank} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                    <td className="fw-bold py-3" style={{ color: '#38bdf8', background: 'transparent' }}>#{r.rank}</td>
                    <td className="fw-semibold py-3" style={{ color: '#ffffff', background: 'transparent' }}>{r.name}</td>
                    <td className="py-3" style={{ color: '#cbd5e1', background: 'transparent' }}>{r.institution}</td>
                    <td className="py-3" style={{ background: 'transparent' }}>
                      <span className="badge px-3 py-2 fw-semibold" style={{ backgroundColor: 'rgba(52, 211, 153, 0.15)', color: '#34d399', border: '1px solid rgba(52, 211, 153, 0.3)' }}>
                        {r.citations}
                      </span>
                    </td>
                    <td className="fw-bold py-3" style={{ color: '#fbbf24', background: 'transparent' }}>{r.hIndex}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

      </div>

      {/* UPLOAD MODAL */}
      {showModal && (
        <div className="modal show d-block" tabIndex="-1" style={{ backgroundColor: 'rgba(0, 0, 0, 0.8)', backdropFilter: 'blur(4px)' }}>
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content text-white rounded-3" style={{ backgroundColor: '#1e293b', border: '1px solid rgba(255,255,255,0.1)' }}>
              
              <div className="modal-header border-0 pb-0">
                <h6 className="modal-title fw-bold text-uppercase" style={{ letterSpacing: '0.5px' }}>Upload Dataset File</h6>
                <button type="button" className="btn-close btn-close-white" onClick={() => setShowModal(false)}></button>
              </div>

              <div className="modal-body py-4">
                <input 
                  type="file" 
                  ref={fileInputRef} 
                  style={{ display: 'none' }} 
                  accept=".csv,.json" 
                  onChange={(e) => e.target.files[0] && handleFileChange(e.target.files[0])} 
                />

                <div 
                  className="p-4 rounded-3 text-center"
                  style={{
                    border: `2px dashed ${isDragging ? '#38bdf8' : 'rgba(255,255,255,0.2)'}`,
                    backgroundColor: isDragging ? 'rgba(56, 189, 248, 0.08)' : '#0f172a',
                    cursor: 'pointer'
                  }}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current.click()}
                >
                  <div className="fw-bold mb-1">Drag and drop file here</div>
                  <p className="text-light opacity-50 small mb-3">Accepts CSV or JSON formats</p>
                  <button className="btn btn-sm btn-outline-info rounded-1 px-3">Browse Files</button>
                </div>

                {selectedFile && (
                  <div className="mt-3 p-3 rounded-2 d-flex align-items-center justify-content-between" style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)' }}>
                    <div>
                      <div className="fw-bold text-info small">{selectedFile.name}</div>
                      <div className="text-light opacity-50 small">{(selectedFile.size / 1024).toFixed(2)} KB</div>
                    </div>
                    <button className="btn btn-sm text-danger" onClick={() => setSelectedFile(null)}>Remove</button>
                  </div>
                )}

                {uploadStatus === 'uploading' && (
                  <div className="mt-3 text-center text-info small">
                    <div className="spinner-border spinner-border-sm me-2" role="status"></div>
                    Processing dataset...
                  </div>
                )}

                {uploadStatus === 'success' && (
                  <div className="mt-3 alert alert-success bg-dark text-success border-success mb-0 py-2 text-center small">
                    Dataset uploaded and parsed successfully.
                  </div>
                )}
              </div>

              <div className="modal-footer border-0 pt-0">
                <button type="button" className="btn btn-sm btn-secondary rounded-1 px-3" onClick={() => setShowModal(false)}>Cancel</button>
                <button 
                  type="button" 
                  className="btn btn-sm btn-info text-dark fw-bold rounded-1 px-4" 
                  disabled={!selectedFile || uploadStatus === 'uploading'}
                  onClick={handleUploadSubmit}
                >
                  Submit
                </button>
              </div>

            </div>
          </div>
        </div>
      )}

      {/* TOAST NOTIFICATION POPUP */}
      {toast.show && (
        <div className="position-fixed bottom-0 end-0 p-3" style={{ zIndex: 1100 }}>
          <div 
            className="toast show align-items-center text-white border-0 shadow-lg rounded-3 p-2" 
            style={{ backgroundColor: toast.type === 'error' ? '#dc2626' : '#059669', minWidth: '280px' }}
          >
            <div className="d-flex justify-content-between align-items-center">
              <div className="d-flex align-items-center gap-2">
                <span className="fw-bold">{toast.type === 'error' ? '✕' : '✓'}</span>
                <span className="small fw-semibold">{toast.message}</span>
              </div>
              <button 
                type="button" 
                className="btn-close btn-close-white opacity-75" 
                onClick={() => setToast({ ...toast, show: false })}
              ></button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}