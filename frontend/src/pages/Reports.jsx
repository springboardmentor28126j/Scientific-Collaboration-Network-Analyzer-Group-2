import React, { useEffect, useState } from 'react';

export default function Reports() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    fetchSummary();
  }, []);

  const fetchSummary = async () => {
    try {
      const res = await fetch('http://localhost:8000/reports/summary');
      const data = await res.json();
      setSummary(data);
    } catch (err) {
      console.error('Failed to fetch report summary:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (type) => {
    try {
      setDownloading(true);
      const url = `http://localhost:8000/reports/export/${type}`;
      const response = await fetch(url);
      if (!response.ok) throw new Error('Download failed');

      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = `SCNA_Report.${type}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(downloadUrl);
    } catch (err) {
      alert(`Failed to download ${type.toUpperCase()} report.`);
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div style={{ background: 'linear-gradient(135deg, #0f172a 0%, #172554 100%)', minHeight: '100vh', color: '#f8fafc', padding: '2.5rem 1rem' }}>
      <div className="container" style={{ maxWidth: '1100px' }}>
        
        {/* Header */}
        <div className="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-3">
          <div>
            <h2 className="fw-bold mb-1" style={{ color: '#38bdf8' }}>Reports & Analytics</h2>
            <p className="text-light opacity-75 mb-0">System Insights, Metrics, & Data Export</p>
          </div>
          <div className="d-flex gap-2">
            <button 
              className="btn btn-outline-success d-flex align-items-center gap-2 fw-semibold px-3 py-2"
              onClick={() => handleExport('csv')}
              disabled={downloading}
              style={{ borderColor: '#34d399', color: '#34d399' }}
            >
              📊 Export CSV
            </button>
            <button 
              className="btn btn-primary d-flex align-items-center gap-2 fw-semibold px-3 py-2"
              onClick={() => handleExport('pdf')}
              disabled={downloading}
              style={{ backgroundColor: '#2563eb', border: 'none' }}
            >
              📄 Download PDF Report
            </button>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-5">
            <div className="spinner-border text-info" role="status"></div>
            <p className="mt-3 text-light opacity-75">Loading Analytics Data...</p>
          </div>
        ) : (
          <>
            {/* Top Metric Cards */}
            <div className="row g-3 mb-4">
              <div className="col-md-3">
                <div className="p-3 rounded-4 shadow-lg h-100" style={{ backgroundColor: 'rgba(255, 255, 255, 0.05)', borderLeft: '4px solid #38bdf8', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
                  <span className="text-light opacity-75 small fw-semibold d-block">TOTAL RESEARCHERS</span>
                  <h3 className="fw-bold mt-2 mb-0" style={{ color: '#38bdf8' }}>{summary?.total_researchers || 0}</h3>
                </div>
              </div>
              <div className="col-md-3">
                <div className="p-3 rounded-4 shadow-lg h-100" style={{ backgroundColor: 'rgba(255, 255, 255, 0.05)', borderLeft: '4px solid #34d399', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
                  <span className="text-light opacity-75 small fw-semibold d-block">PUBLICATIONS</span>
                  <h3 className="fw-bold mt-2 mb-0" style={{ color: '#34d399' }}>{summary?.total_publications || 0}</h3>
                </div>
              </div>
              <div className="col-md-3">
                <div className="p-3 rounded-4 shadow-lg h-100" style={{ backgroundColor: 'rgba(255, 255, 255, 0.05)', borderLeft: '4px solid #fbbf24', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
                  <span className="text-light opacity-75 small fw-semibold d-block">INSTITUTIONS</span>
                  <h3 className="fw-bold mt-2 mb-0" style={{ color: '#fbbf24' }}>{summary?.total_institutions || 0}</h3>
                </div>
              </div>
              <div className="col-md-3">
                <div className="p-3 rounded-4 shadow-lg h-100" style={{ backgroundColor: 'rgba(255, 255, 255, 0.05)', borderLeft: '4px solid #f43f5e', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
                  <span className="text-light opacity-75 small fw-semibold d-block">TOTAL CITATIONS</span>
                  <h3 className="fw-bold mt-2 mb-0" style={{ color: '#f43f5e' }}>{summary?.total_citations || 0}</h3>
                </div>
              </div>
            </div>

            {/* Data Section */}
            <div className="row g-4">
              
              {/* Top Research Domains Card (Fixed Transparent Theme) */}
              <div className="col-md-7">
                <div className="p-4 rounded-4 shadow-lg h-100" style={{ backgroundColor: 'rgba(255, 255, 255, 0.05)', border: '1px solid rgba(255,255,255,0.1)' }}>
                  <h5 className="fw-bold text-white mb-3">Top Research Domains</h5>
                  <div className="table-responsive">
                    <table className="table align-middle text-white mb-0" style={{ backgroundColor: 'transparent' }}>
                      <thead>
                        <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.2)', backgroundColor: 'transparent' }}>
                          <th className="bg-transparent text-light opacity-75 fw-semibold py-2">Domain Name</th>
                          <th className="bg-transparent text-end text-light opacity-75 fw-semibold py-2">Publications</th>
                        </tr>
                      </thead>
                      <tbody>
                        {summary?.top_domains?.map((d, i) => (
                          <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.08)', backgroundColor: 'transparent' }}>
                            <td className="bg-transparent fw-semibold py-3" style={{ color: '#38bdf8' }}>{d.domain}</td>
                            <td className="bg-transparent text-end py-3">
                              <span className="badge px-3 py-2 fw-bold" style={{ backgroundColor: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8', border: '1px solid rgba(56, 189, 248, 0.3)' }}>
                                {d.count}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>

              {/* Recent Activity Card */}
              <div className="col-md-5">
                <div className="p-4 rounded-4 shadow-lg h-100" style={{ backgroundColor: 'rgba(255, 255, 255, 0.05)', border: '1px solid rgba(255,255,255,0.1)' }}>
                  <h5 className="fw-bold text-white mb-3">Recent Activity Highlights</h5>
                  <ul className="list-group list-group-flush bg-transparent">
                    {summary?.recent_activities?.map((act, idx) => (
                      <li key={idx} className="list-group-item bg-transparent px-0 py-2 text-white" style={{ borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
                        <div className="small text-light opacity-50">{act.date}</div>
                        <div className="fw-semibold text-light opacity-90">{act.event}</div>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

            </div>
          </>
        )}

      </div>
    </div>
  );
}