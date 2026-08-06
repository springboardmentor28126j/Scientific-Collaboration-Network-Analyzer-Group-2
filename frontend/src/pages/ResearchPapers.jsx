import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import Footer from "../components/Footer";
import Pagination from "../components/Pagination";
import api from "../services/api";

import "../styles/researchpapers.css";

function ResearchPapers() {

    const [papers, setPapers] = useState([]);
    const [search, setSearch] = useState("");
    const [loading, setLoading] = useState(true);

    const [currentPage, setCurrentPage] = useState(1);

    const papersPerPage = 5;

    useEffect(() => {

        api.get("/papers/")
            .then((res) => {

                setPapers(res.data);

            })

            .catch((err) => {

                console.log(err);

            })

            .finally(() => {

                setLoading(false);

            });

    }, []);

    const filteredPapers = papers.filter((paper) => {

        const title = (paper.title || "").toLowerCase();
        const authors = (paper.authors || "").toLowerCase();
        const source = (paper.source || "").toLowerCase();
        const doi = (paper.doi || "").toLowerCase();

        return (

            title.includes(search.toLowerCase()) ||

            authors.includes(search.toLowerCase()) ||

            source.includes(search.toLowerCase()) ||

            doi.includes(search.toLowerCase())

        );

    });

    const indexOfLastPaper =
        currentPage * papersPerPage;

    const indexOfFirstPaper =
        indexOfLastPaper - papersPerPage;

    const currentPapers =
        filteredPapers.slice(
            indexOfFirstPaper,
            indexOfLastPaper
        );

    const totalPages =
        Math.ceil(filteredPapers.length / papersPerPage);

    if (loading) {

        return (

            <>
                <Navbar />

                <div className="dashboard-container">

                    <Sidebar />

                    <div className="papers-content">

                        <div className="loading-container">

                            <div className="spinner"></div>

                            <div className="loading-text">

                                Loading Research Papers...

                            </div>

                        </div>

                    </div>

                </div>

                <Footer />

            </>

        );

    }

    return (

        <>
            <Navbar />

            <div className="dashboard-container">

                <Sidebar />

                <div className="papers-content">

                    <div className="card shadow border-0 rounded-4">

                        <div className="card-body">

                            <div className="d-flex justify-content-between align-items-center mb-4">

                                <h3 className="fw-bold text-primary mb-0">

                                    📄 Research Papers

                                </h3>

                                <span className="badge bg-primary fs-6">

                                    {filteredPapers.length} Papers

                                </span>

                            </div>

                            <input

                                type="text"

                                className="form-control shadow-sm rounded-pill mb-4"

                                placeholder="🔍 Search by Title, Author, Source or DOI..."

                                style={{
                                    height: "48px"
                                }}

                                value={search}

                                onChange={(e) => {

                                    setSearch(e.target.value);

                                    setCurrentPage(1);

                                }}

                            />

                            <div className="table-responsive shadow-sm rounded-4">

                                <table className="table table-hover align-middle mb-0">

                                    <thead className="table-primary">

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

                                        {

                                            currentPapers.length > 0 ?

                                                (

                                                    currentPapers.map((paper) => (

                                                        <tr key={paper.id}>

                                                            <td>{paper.id}</td>

                                                            <td>{paper.title || "-"}</td>

                                                            <td>{paper.authors || "-"}</td>

                                                            <td>{paper.publication_year || "-"}</td>

                                                            <td>{paper.source || "-"}</td>

                                                            <td>{paper.doi || "-"}</td>

                                                        </tr>

                                                    ))

                                                )

                                                :

                                                (

                                                    <tr>

                                                        <td

                                                            colSpan="6"

                                                            className="text-center text-danger fw-bold py-4"

                                                        >

                                                            ❌ No Research Papers Found

                                                        </td>

                                                    </tr>

                                                )

                                        }

                                    </tbody>

                                </table>

                            </div>

                            <div className="d-flex justify-content-center mt-4">

                                <Pagination

                                    currentPage={currentPage}

                                    totalPages={totalPages}

                                    onPageChange={setCurrentPage}

                                />

                            </div>

                        </div>

                    </div>

                </div>

            </div>

            <Footer />

        </>

    );

}

export default ResearchPapers;