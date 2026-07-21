import { useEffect, useState } from "react";

import DashboardNavbar from "../components/DashboardNavbar";
import ResearcherSidebar from "../components/ResearcherSidebar";
import Footer from "../components/Footer";

import api from "../services/api";

import "../styles/dashboard.css";
import "../styles/myPapers.css";
import "../styles/profile.css";

function MyPapers() {

    const [papers, setPapers] = useState([]);
    const [editingPaper, setEditingPaper] = useState(null);

    useEffect(() => {

        fetchMyPapers();

    }, []);

    const fetchMyPapers = async () => {

        try {

            const token = localStorage.getItem("token");

            const response = await api.get(
                "/papers/my-papers",
                {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                }
            );

            setPapers(response.data);

        } catch (error) {

            console.log(error);

        }

    };

    const handleEdit = (paper) => {

        setEditingPaper({ ...paper });

    };

    const handleUpdate = async () => {

        try {

            const token = localStorage.getItem("token");

            await api.put(

                `/papers/${editingPaper.id}`,

                editingPaper,

                {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                }

            );

            alert("✅ Paper updated successfully");

            setEditingPaper(null);

            fetchMyPapers();

        } catch (error) {

            console.log(error);

            alert("❌ Failed to update paper");

        }

    };

    const handleDelete = async (paperId) => {

        const confirmDelete = window.confirm(
            "Are you sure you want to delete this paper?"
        );

        if (!confirmDelete) return;

        try {

            const token = localStorage.getItem("token");

            await api.delete(

                `/papers/${paperId}`,

                {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                }

            );

            alert("✅ Paper deleted successfully");

            fetchMyPapers();

        } catch (error) {

            console.log(error);

            alert("❌ Failed to delete paper");

        }

    };

    return (

        <>

            <DashboardNavbar />

            <div className="dashboard-container">

                <ResearcherSidebar />

                <div className="dashboard-content">

                    <h2>📄 My Research Papers</h2>

                    {

                        papers.length === 0 ?

                        (

                            <div className="empty">

                                No Papers Found

                            </div>

                        )

                        :

                        papers.map((paper) => (

                            <div
                                key={paper.id}
                                className="paper-card"
                            >

                                <h3>{paper.title}</h3>

                                <p>

                                    <b>Authors :</b> {paper.authors}

                                </p>

                                <p>

                                    <b>Year :</b> {paper.publication_year}

                                </p>

                                <p>

                                    <b>Source :</b> {paper.source}

                                </p>

                               <p>
    <b>Status :</b>

    <span
        className={
            paper.status === "Published"
                ? "status published"
                : "status"
        }
    >
        {paper.status}
    </span>
</p>

                                <div className="paper-buttons">

                                    <button
                                        onClick={() => handleEdit(paper)}
                                    >
                                        ✏ Edit
                                    </button>

                                    <button
                                        className="delete"
                                        onClick={() => handleDelete(paper.id)}
                                    >
                                        🗑 Delete
                                    </button>

                                </div>

                            </div>

                        ))

                    }

                    {
                        editingPaper && (

                            <div className="modal-overlay">

                                <div className="modal">

                                    <h2>Edit Research Paper</h2>

                                    <label>Paper Title</label>

                                    <input
                                        value={editingPaper.title}
                                        onChange={(e) =>
                                            setEditingPaper({
                                                ...editingPaper,
                                                title: e.target.value
                                            })
                                        }
                                    />

                                    <label>Authors</label>

                                    <input
                                        value={editingPaper.authors}
                                        onChange={(e) =>
                                            setEditingPaper({
                                                ...editingPaper,
                                                authors: e.target.value
                                            })
                                        }
                                    />

                                    <label>Abstract</label>

                                    <textarea
                                        rows="5"
                                        value={editingPaper.abstract}
                                        onChange={(e) =>
                                            setEditingPaper({
                                                ...editingPaper,
                                                abstract: e.target.value
                                            })
                                        }
                                    />
                                                                        <label>Publication Year</label>

                                    <input
                                        type="number"
                                        value={editingPaper.publication_year}
                                        onChange={(e) =>
                                            setEditingPaper({
                                                ...editingPaper,
                                                publication_year: e.target.value
                                            })
                                        }
                                    />

                                    <label>Source</label>

                                    <input
                                        value={editingPaper.source}
                                        onChange={(e) =>
                                            setEditingPaper({
                                                ...editingPaper,
                                                source: e.target.value
                                            })
                                        }
                                    />

                                    <label>DOI</label>

                                    <input
                                        value={editingPaper.doi}
                                        onChange={(e) =>
                                            setEditingPaper({
                                                ...editingPaper,
                                                doi: e.target.value
                                            })
                                        }
                                    />

                                    <label>Keywords</label>

                                    <input
                                        value={editingPaper.keywords || ""}
                                        onChange={(e) =>
                                            setEditingPaper({
                                                ...editingPaper,
                                                keywords: e.target.value
                                            })
                                        }
                                    />

                                    <label>Status</label>

                                    <select
                                        value={editingPaper.status}
                                        onChange={(e) =>
                                            setEditingPaper({
                                                ...editingPaper,
                                                status: e.target.value
                                            })
                                        }
                                    >
                                        <option value="Draft">Draft</option>
                                        <option value="Published">Published</option>
                                    </select>

                                    <div className="modal-buttons">

                                        <button
                                            className="save-btn"
                                            onClick={handleUpdate}
                                        >
                                            Save Changes
                                        </button>

                                        <button
                                            className="cancel-btn"
                                            onClick={() => setEditingPaper(null)}
                                        >
                                            Cancel
                                        </button>

                                    </div>

                                </div>

                            </div>

                        )

                    }

                </div>

            </div>

            <Footer />

        </>

    );

}

export default MyPapers;