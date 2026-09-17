import { useEffect, useState } from "react";
import axios from "axios";
import "./Citations.css";

function Citations() {
  const [citations, setCitations] = useState([]);

  const [formData, setFormData] = useState({
    publication_id: "",
    cited_publication_id: "",
    doi: "",
  });

  const fetchCitations = async () => {
    try {
      const response = await axios.get(
        "http://127.0.0.1:8000/citations/"
      );

      setCitations(response.data);
    } catch (error) {
      console.error("Error fetching citations:", error);
    }
  };

useEffect(() => {
  const timer = setTimeout(() => {
    fetchCitations();
  }, 0);

  return () => clearTimeout(timer);
}, []);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const addCitation = async (e) => {
    e.preventDefault();

    try {
      await axios.post(
        "http://127.0.0.1:8000/citations/",
        null,
        {
          params: {
            publication_id: formData.publication_id,
            cited_publication_id: formData.cited_publication_id,
            doi: formData.doi,
          },
        }
      );

      alert("Citation added successfully!");

      setFormData({
        publication_id: "",
        cited_publication_id: "",
        doi: "",
      });

      fetchCitations();
    } catch (error) {
      alert(
        error.response?.data?.detail ||
          "Failed to add citation."
      );
    }
  };

  const deleteCitation = async (citationId) => {
    if (!window.confirm("Are you sure you want to delete this citation?")) {
      return;
    }

    try {
      await axios.delete(
        `http://127.0.0.1:8000/citations/${citationId}`
      );

      alert("Citation deleted successfully!");

      fetchCitations();
    } catch (error) {
      alert(
        error.response?.data?.detail ||
          "Failed to delete citation."
      );
    }
  };

  return (
    <div className="citations-page">
      <div className="citations-header">
        <h1>Citation & Reference Management</h1>
        <p>
          Manage publication citations, references, and DOI information.
        </p>
      </div>

      <div className="citation-form-card">
        <h2>Add Citation</h2>

        <form onSubmit={addCitation}>
          <div className="citation-form-grid">
            <div>
              <label>Publication ID</label>
              <input
                type="number"
                name="publication_id"
                value={formData.publication_id}
                onChange={handleChange}
                placeholder="Enter publication ID"
                required
              />
            </div>

            <div>
              <label>Cited Publication ID</label>
              <input
                type="number"
                name="cited_publication_id"
                value={formData.cited_publication_id}
                onChange={handleChange}
                placeholder="Enter cited publication ID"
                required
              />
            </div>

            <div>
              <label>DOI</label>
              <input
                type="text"
                name="doi"
                value={formData.doi}
                onChange={handleChange}
                placeholder="Enter DOI"
              />
            </div>
          </div>

          <button type="submit" className="add-citation-btn">
            Add Citation
          </button>
        </form>
      </div>

      <div className="citations-table-card">
        <h2>Citation Records</h2>

        {citations.length === 0 ? (
          <p className="no-citations">
            No citation records found.
          </p>
        ) : (
          <div className="table-container">
            <table className="citations-table">
              <thead>
                <tr>
                  <th>Citation ID</th>
                  <th>Publication ID</th>
                  <th>Cited Publication ID</th>
                  <th>DOI</th>
                  <th>Action</th>
                </tr>
              </thead>

              <tbody>
                {citations.map((citation) => (
                  <tr key={citation.citation_id}>
                    <td>{citation.citation_id}</td>
                    <td>{citation.publication_id}</td>
                    <td>{citation.cited_publication_id}</td>
                    <td>{citation.doi || "—"}</td>
                    <td>
                      <button
                        className="delete-citation-btn"
                        onClick={() =>
                          deleteCitation(citation.citation_id)
                        }
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default Citations;