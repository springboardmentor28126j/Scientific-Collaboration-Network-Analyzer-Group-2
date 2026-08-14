import { useState } from "react";
import DashboardNavbar from "../components/DashboardNavbar";
import Footer from "../components/Footer";
import api from "../services/api";

import "../styles/aiRecommendations.css";

function AIRecommendations() {

    const [interest, setInterest] = useState("");
    const [recommendations, setRecommendations] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const getRecommendations = async () => {

        if (!interest.trim()) {
            setError("Please enter a research interest or topic.");
            return;
        }

        try {

            setLoading(true);
            setError("");
            setRecommendations([]);

            const token = localStorage.getItem("token");

            const response = await api.get(
                "/papers/ai-recommendations",
                {
                    params: {
                        interest: interest.trim(),
                        top_n: 5
                    },
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                }
            );

            setRecommendations(response.data);

        } catch (err) {

            console.error(
                "Failed to get AI recommendations:",
                err
            );

            if (err.response?.status === 401) {
                setError(
                    "Your session has expired. Please login again."
                );
            } else {
                setError(
                    "Unable to get AI recommendations. Please try again."
                );
            }

        } finally {

            setLoading(false);

        }
    };

    const handleSubmit = (event) => {

        event.preventDefault();

        getRecommendations();

    };

    const getSimilarityClass = (score) => {

        if (score >= 70) {
            return "similarity-high";
        }

        if (score >= 40) {
            return "similarity-medium";
        }

        return "similarity-low";
    };

    return (
        <>
            <DashboardNavbar />

            <main className="ai-recommendations-container">

                <section className="ai-hero">

                    <div className="ai-icon">
                        🤖
                    </div>

                    <div>
                        <h1>
                            AI Research Paper Recommendations
                        </h1>

                        <p>
                            Discover research papers that are
                            semantically relevant to your research
                            interests using artificial intelligence.
                        </p>
                    </div>

                </section>


                <section className="ai-search-card">

                    <form onSubmit={handleSubmit}>

                        <label htmlFor="research-interest">
                            Research Interest
                        </label>

                        <div className="ai-search-row">

                            <input
                                id="research-interest"
                                type="text"
                                value={interest}
                                onChange={(event) =>
                                    setInterest(event.target.value)
                                }
                                placeholder="Example: emotion aware adaptive learning system"
                            />

                            <button
                                type="submit"
                                disabled={loading}
                                className="ai-search-button"
                            >
                                {loading
                                    ? "Analyzing..."
                                    : "✨ Get AI Recommendations"}
                            </button>

                        </div>

                    </form>

                    <div className="ai-hint">
                        💡 Try topics such as
                        <strong>
                            {" "}emotion recognition, machine learning,
                            {" "}adaptive education, or collaboration networks.
                        </strong>
                    </div>

                </section>


                {error && (

                    <div className="ai-error">
                        {error}
                    </div>

                )}


                {loading && (

                    <section className="ai-loading">

                        <div className="ai-spinner"></div>

                        <h3>
                            AI is analyzing research papers...
                        </h3>

                        <p>
                            Comparing your research interest with
                            the available papers.
                        </p>

                    </section>

                )}


                {!loading &&
                    recommendations.length > 0 && (

                        <section className="recommendations-section">

                            <div className="recommendations-heading">

                                <div>
                                    <h2>
                                        Recommended Papers
                                    </h2>

                                    <p>
                                        Based on semantic similarity
                                        with your research interest.
                                    </p>
                                </div>

                                <span className="result-count">
                                    {recommendations.length} papers
                                </span>

                            </div>


                            <div className="recommendation-grid">

                                {recommendations.map((paper, index) => (

                                    <article
                                        className="recommendation-card"
                                        key={paper.id}
                                    >

                                        <div className="paper-card-top">

                                            <span className="rank-badge">
                                                #{index + 1}
                                            </span>

                                            <span
                                                className={`similarity-badge ${getSimilarityClass(
                                                    paper.similarity
                                                )}`}
                                            >
                                                {paper.similarity}% match
                                            </span>

                                        </div>


                                        <h3>
                                            {paper.title}
                                        </h3>


                                        <p className="paper-authors">
                                            👤 {paper.authors}
                                        </p>


                                        <p className="paper-abstract">

                                            {paper.abstract
                                                ? paper.abstract
                                                : "No abstract available."}

                                        </p>


                                        <div className="paper-meta">

                                            <span>
                                                📅 {paper.publication_year}
                                            </span>

                                            <span>
                                                🏛️ {paper.source}
                                            </span>

                                        </div>


                                        {paper.keywords && (

                                            <div className="paper-keywords">

                                                {paper.keywords
                                                    .split(",")
                                                    .map((keyword, keywordIndex) => (

                                                        <span
                                                            key={keywordIndex}
                                                        >
                                                            {keyword.trim()}
                                                        </span>

                                                    ))}

                                            </div>

                                        )}


                                        {paper.doi && (

                                            <div className="paper-doi">

                                                <strong>
                                                    DOI:
                                                </strong>

                                                <span>
                                                    {paper.doi}
                                                </span>

                                            </div>

                                        )}

                                    </article>

                                ))}

                            </div>

                        </section>

                    )}


                {!loading &&
                    recommendations.length === 0 &&
                    !error && (

                        <section className="ai-empty">

                            <div className="empty-icon">
                                🔎
                            </div>

                            <h2>
                                Find Relevant Research
                            </h2>

                            <p>
                                Enter a research topic above and our
                                AI model will find the most relevant
                                papers from the research database.
                            </p>

                        </section>

                    )}

            </main>

            <Footer />
        </>
    );
}

export default AIRecommendations;