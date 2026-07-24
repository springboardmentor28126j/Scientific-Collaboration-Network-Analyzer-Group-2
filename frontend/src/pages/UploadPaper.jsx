import { useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../services/api";

import DashboardNavbar from "../components/DashboardNavbar";
import ResearcherSidebar from "../components/ResearcherSidebar";
import Footer from "../components/Footer";

import "../styles/dashboard.css";
import "../styles/profile.css";

function UploadPaper() {

    const navigate = useNavigate();

const [pdf, setPdf] = useState(null);

const [paper, setPaper] = useState({
    title: "",
    authors: "",
    abstract: "",
    publication_year: "",
    source: "",
    doi: "",
    keywords: "",
    status: "Draft"
});

    const handleChange = (e) => {
        setPaper({
            ...paper,
            [e.target.name]: e.target.value
        });
    };

   const handleSubmit = async (e) => {

    e.preventDefault();

    try {

        const token = localStorage.getItem("token");

        const formData = new FormData();

        formData.append("title", paper.title);
        formData.append("authors", paper.authors);
        formData.append("abstract", paper.abstract);
        formData.append("publication_year", paper.publication_year);
        formData.append("source", paper.source);
        formData.append("doi", paper.doi);
        formData.append("keywords", paper.keywords);
        formData.append("status", paper.status);

        if (pdf) {
            formData.append("pdf", pdf);
        }

        await api.post(
            "/papers/",
            formData,
            {
                headers: {
                    Authorization: `Bearer ${token}`,
                    "Content-Type": "multipart/form-data"
                }
            }
        );

        alert("✅ Paper uploaded successfully!");

        navigate("/my-papers");

    } catch (error) {

        console.log(error);

        alert("❌ Failed to upload paper.");

    }

};
    return (
        <>
            <DashboardNavbar />

            <div className="dashboard-container">

                <ResearcherSidebar />

                <div className="dashboard-content">

                    <h2>📄 Upload Research Paper</h2>

                    <div className="profile-card">

                        <form onSubmit={handleSubmit}>

                            <label>Paper Title</label>
                            <input
                                type="text"
                                name="title"
                                placeholder="Enter Paper Title"
                                value={paper.title}
                                onChange={handleChange}
                                required
                            />

                            <label>Authors</label>
                            <input
                                type="text"
                                name="authors"
                                placeholder="Enter Author Names"
                                value={paper.authors}
                                onChange={handleChange}
                                required
                            />

                            <label>Abstract</label>
                            <textarea
                                name="abstract"
                                placeholder="Write Paper Abstract..."
                                rows="6"
                                value={paper.abstract}
                                onChange={handleChange}
                                required
                            />

                            <label>Publication Year</label>
                            <input
                                type="number"
                                name="publication_year"
                                placeholder="2026"
                                value={paper.publication_year}
                                onChange={handleChange}
                                required
                            />

                            <label>Source</label>
                            <input
                                type="text"
                                name="source"
                                placeholder="IEEE / Springer / ACM"
                                value={paper.source}
                                onChange={handleChange}
                                required
                            />

                            <label>DOI</label>
                            <input
                                type="text"
                                name="doi"
                                placeholder="10.xxxx/xxxxx"
                                value={paper.doi}
                                onChange={handleChange}
                                required
                            />

                            <label>Keywords</label>
                            <input
                                type="text"
                                name="keywords"
                                placeholder="AI, Machine Learning, NLP..."
                                value={paper.keywords}
                                onChange={handleChange}
                            />

            <label>Status</label>

<select
    name="status"
    value={paper.status}
    onChange={handleChange}
>
    <option value="Draft">Draft</option>
    <option value="Published">Published</option>
</select>

<label>Research Paper (PDF)</label>

<input
    type="file"
    accept=".pdf"
    onChange={(e) => setPdf(e.target.files[0])}
/>

                            <button
                                className="edit-profile-btn"
                                type="submit"
                            >
                                🚀 Upload Paper
                            </button>

                        </form>

                    </div>

                </div>

            </div>

            <Footer />

        </>
    );

}

export default UploadPaper;