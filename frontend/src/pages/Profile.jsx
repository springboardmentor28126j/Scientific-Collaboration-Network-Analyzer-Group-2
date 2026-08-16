import { useEffect, useState } from "react";
import {
    getMyResearcherProfile,
    getMyResearcherStats,
} from "../services/researcherService";

export default function Profile() {
    const [researcher, setResearcher] = useState(null);
    const [stats, setStats] = useState({
        publications: 0,
        citations: 0,
        collaborators: 0,
    });

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        loadProfile();
    }, []);

    const loadProfile = async () => {
        try {
            setLoading(true);
            setError("");

            const [profileData, statsData] = await Promise.all([
                getMyResearcherProfile(),
                getMyResearcherStats(),
            ]);

            setResearcher(profileData);
            setStats(statsData);
        } catch (err) {
            console.error("Failed to load profile:", err);

            setError(
                err.response?.data?.detail ||
                "Failed to load your profile."
            );
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="container py-5 text-center">
                <p>Loading profile...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="container py-5">
                <div className="alert alert-danger">
                    {error}
                </div>
            </div>
        );
    }

    if (!researcher) {
        return (
            <div className="container py-5">
                <div className="alert alert-danger">
                    Researcher profile not found.
                </div>
            </div>
        );
    }

    const fullName =
        `${researcher.first_name || ""} ${researcher.last_name || ""}`.trim() ||
        "Unknown Researcher";

    return (
        <div className="container py-5">

            {/* Header */}
            <div className="card shadow-sm mb-4">
                <div className="card-body">

                    <div className="d-flex align-items-center">

                        <div
                            className="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center me-4"
                            style={{
                                width: "80px",
                                height: "80px",
                                fontSize: "30px",
                            }}
                        >
                            {fullName.charAt(0).toUpperCase()}
                        </div>

                        <div>
                            <h1 className="mb-1">
                                {fullName}
                            </h1>

                            <p className="text-muted mb-0">
                                Researcher
                            </p>
                        </div>

                    </div>

                    <hr />

                    <div className="row">

                        <div className="col-md-4 mb-2">
                            <strong>Experience:</strong>{" "}
                            {researcher.experience || 0} years
                        </div>

                        <div className="col-md-4 mb-2">
                            <strong>Phone:</strong>{" "}
                            {researcher.phone || "Not provided"}
                        </div>

                        <div className="col-md-4 mb-2">
                            <strong>Researcher ID:</strong>{" "}
                            {researcher.id}
                        </div>

                    </div>

                </div>
            </div>

            {/* Statistics */}
            <div className="row mb-4">

                <div className="col-md-4 mb-3">
                    <div className="card shadow-sm text-center h-100">
                        <div className="card-body">
                            <h2>{stats.publications}</h2>
                            <p className="text-muted mb-0">
                                Publications
                            </p>
                        </div>
                    </div>
                </div>

                <div className="col-md-4 mb-3">
                    <div className="card shadow-sm text-center h-100">
                        <div className="card-body">
                            <h2>{stats.citations}</h2>
                            <p className="text-muted mb-0">
                                Citations
                            </p>
                        </div>
                    </div>
                </div>

                <div className="col-md-4 mb-3">
                    <div className="card shadow-sm text-center h-100">
                        <div className="card-body">
                            <h2>{stats.collaborators}</h2>
                            <p className="text-muted mb-0">
                                Collaborators
                            </p>
                        </div>
                    </div>
                </div>

            </div>

            {/* About */}
            <div className="card shadow-sm mb-4">
                <div className="card-body">

                    <h4>About</h4>

                    <p className="mb-0">
                        {researcher.bio ||
                            "No biography provided."}
                    </p>

                </div>
            </div>

            {/* Research Information */}
            <div className="card shadow-sm mb-4">
                <div className="card-body">

                    <h4>Research Information</h4>

                    <div className="mb-4">
                        <strong>Skills</strong>

                        <p className="mt-2">
                            {researcher.skills ||
                                "No skills provided."}
                        </p>
                    </div>

                    <div>
                        <strong>Research Interests</strong>

                        <p className="mt-2">
                            {researcher.interests ||
                                "No research interests provided."}
                        </p>
                    </div>

                </div>
            </div>

            {/* Social Profiles */}
            <div className="card shadow-sm mb-4">
                <div className="card-body">

                    <h4 className="mb-3">
                        Social & Research Profiles
                    </h4>

                    <p>
                        <strong>ORCID:</strong>{" "}
                        {researcher.orcid || "Not provided"}
                    </p>

                    <p>
                        <strong>Google Scholar:</strong>{" "}
                        {researcher.google_scholar || "Not provided"}
                    </p>

                    <p>
                        <strong>ResearchGate:</strong>{" "}
                        {researcher.research_gate || "Not provided"}
                    </p>

                    <p className="mb-0">
                        <strong>LinkedIn:</strong>{" "}
                        {researcher.linkedin || "Not provided"}
                    </p>

                </div>
            </div>

            {/* Publications */}
            <div className="card shadow-sm">
                <div className="card-body">

                    <h4>Publications</h4>

                    {researcher.publications &&
                    researcher.publications.length > 0 ? (

                        <div className="list-group mt-3">

                            {researcher.publications.map(
                                (publication) => (
                                    <div
                                        key={publication.id}
                                        className="list-group-item"
                                    >
                                        <strong>
                                            {publication.title}
                                        </strong>

                                        {publication.publication_year && (
                                            <span className="text-muted">
                                                {" "}
                                                (
                                                {
                                                    publication.publication_year
                                                }
                                                )
                                            </span>
                                        )}
                                    </div>
                                )
                            )}

                        </div>

                    ) : (
                        <p className="text-muted mt-3 mb-0">
                            No publications yet.
                        </p>
                    )}

                </div>
            </div>

        </div>
    );
}