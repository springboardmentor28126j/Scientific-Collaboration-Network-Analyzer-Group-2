import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import Footer from "../components/Footer";
import api from "../services/api";

import "../styles/researchpapers.css";

function ResearchPapers() {

  const [papers, setPapers] = useState([]);
  const [search, setSearch] = useState("");

  useEffect(() => {
    api.get("/papers/")
      .then((res) => {
        setPapers(res.data);
      })
      .catch((err) => {
        console.log(err);
      });
  }, []);

  const filteredPapers = papers.filter((paper) =>
    paper.title.toLowerCase().includes(search.toLowerCase()) ||
    paper.authors.toLowerCase().includes(search.toLowerCase()) ||
    paper.source.toLowerCase().includes(search.toLowerCase()) ||
    paper.doi.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <>
      <Navbar />

      <div className="dashboard-container">

        <Sidebar />

        <div className="papers-content">

          <h2>📄 Research Papers</h2>

          <input
            type="text"
            className="search-box"
            placeholder="🔍 Search by Title, Author, Source or DOI..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />

          <table className="papers-table">

            <thead>

              <tr>
                <th>ID</th>
                <th>Title</th>
                <th>Authors</th>
                <th>Year</th>
                <th>Source</th>
                <th>DOI</th>
              </tr>

            </thead>

            <tbody>

              {filteredPapers.length > 0 ? (

                filteredPapers.map((paper) => (

                  <tr key={paper.id}>

                    <td>{paper.id}</td>
                    <td>{paper.title}</td>
                    <td>{paper.authors}</td>
                    <td>{paper.publication_year}</td>
                    <td>{paper.source}</td>
                    <td>{paper.doi}</td>

                  </tr>

                ))

              ) : (

                <tr>
                  <td colSpan="6" style={{ textAlign: "center" }}>
                    No Research Papers Found
                  </td>
                </tr>

              )}

            </tbody>

          </table>

        </div>

      </div>

      <Footer />

    </>
  );
}

export default ResearchPapers;