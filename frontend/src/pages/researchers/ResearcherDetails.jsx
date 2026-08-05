import { useEffect, useState } from "react";
import { useNavigate, useParams, Link } from "react-router-dom";

import { getResearcher } from "../../services/researcherService";

function ResearcherDetails() {
    

    const { id } = useParams();
    const navigate = useNavigate();

    const [researcher, setResearcher] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadResearcher();
    }, []);

    const loadResearcher = async () => {
        try {

            const data = await getResearcher(id);

            setResearcher(data);

        } catch (error) {

            console.error(error);

            alert("Unable to load researcher.");

            navigate("/researchers");

        } finally {

            setLoading(false);

        }
    };

    if (loading) {
        return (
            <div className="container py-5 text-center">

                <div
                    className="spinner-border text-primary"
                    role="status"
                />

            </div>
        );
    }

    if (!researcher) {
        return null;
    }

    return (

        <div className="container py-4">

            {/* Back Button */}

            <button
                className="btn btn-outline-secondary mb-4"
                onClick={() => navigate("/researchers")}
            >
                ← Back to Researchers
            </button>

            {/* Profile Card */}

            <div className="card shadow-lg border-0">

                <div className="card-body p-5">

                    <div className="row">

                        <div className="col-md-3 text-center">

                            <img
                                src={`https://ui-avatars.com/api/?name=${researcher.first_name}+${researcher.last_name}&background=0D6EFD&color=fff&size=256`}
                                alt="Profile"
                                className="rounded-circle mb-3"
                                width="180"
                            />

                        </div>

                        <div className="col-md-9">

                            <h2 className="fw-bold">

                                {researcher.first_name} {researcher.last_name}

                            </h2>

                            <h5 className="text-muted">

                                Researcher

                            </h5>

                            <hr />

                            <p>

                                <strong>Experience:</strong>{" "}
                                {researcher.experience} Years

                            </p>

                            <p>

                                <strong>Phone:</strong>{" "}
                                {researcher.phone || "-"}

                            </p>

                            <p>

                                <strong>Bio:</strong>

                            </p>

                            <p className="text-muted">

                                {researcher.bio || "No bio available."}

                            </p>

                        </div>

                    </div>

                </div>

            </div>

            {/* Research Profiles */}

            <div className="card shadow-sm mt-4">

                <div className="card-header bg-primary text-white">

                    <h5 className="mb-0">

                        Research Profiles

                    </h5>

                </div>

                <div className="card-body">

                    <table className="table">

                        <tbody>

                            <tr>

                                <th width="220">

                                    ORCID

                                </th>

                                <td>

                                    {researcher.orcid ? (

                                        <a
                                            href={researcher.orcid}
                                            target="_blank"
                                            rel="noreferrer"
                                        >
                                            {researcher.orcid}
                                        </a>

                                    ) : (

                                        "Not Available"

                                    )}

                                </td>

                            </tr>

                            <tr>

                                <th>

                                    Google Scholar

                                </th>

                                <td>

                                    {researcher.google_scholar ? (

                                        <a
                                            href={researcher.google_scholar}
                                            target="_blank"
                                            rel="noreferrer"
                                        >
                                            Google Scholar
                                        </a>

                                    ) : (

                                        "Not Available"

                                    )}

                                </td>

                            </tr>

                            <tr>

                                <th>

                                    ResearchGate

                                </th>

                                <td>

                                    {researcher.research_gate ? (

                                        <a
                                            href={researcher.research_gate}
                                            target="_blank"
                                            rel="noreferrer"
                                        >
                                            ResearchGate
                                        </a>

                                    ) : (

                                        "Not Available"

                                    )}

                                </td>

                            </tr>

                            <tr>

                                <th>

                                    LinkedIn

                                </th>

                                <td>

                                    {researcher.linkedin ? (

                                        <a
                                            href={researcher.linkedin}
                                            target="_blank"
                                            rel="noreferrer"
                                        >
                                            LinkedIn
                                        </a>

                                    ) : (

                                        "Not Available"

                                    )}

                                </td>

                            </tr>

                        </tbody>

                    </table>

                </div>

            </div>

            {/* Publications */}

            <div className="card shadow-sm mt-4">

                <div className="card-header bg-success text-white">

                    <h5 className="mb-0">

                        Publications

                    </h5>

                </div>

                <div className="card-body">

                    {!researcher.publications ||
                    researcher.publications.length === 0 ? (

                        <div className="alert alert-warning">

                            No publications available.

                        </div>

                    ) : (

                        <div className="row">

                            {researcher.publications.map((publication) => (

                                <div
                                    className="col-lg-6 mb-3"
                                    key={publication.id}
                                >

                                    <div className="card h-100">

                                        <div className="card-body">

                                            <h5>

                                                {publication.title}

                                            </h5>

                                            <p>

                                                {publication.publication_type}

                                            </p>

                                            <p>

                                                {publication.publication_year}

                                            </p>

                                            <p>

                                                Citations:{" "}
                                                {publication.citation_count}

                                            </p>

                                            <Link
                                                to={`/publications/${publication.id}`}
                                                className="btn btn-primary btn-sm"
                                            >
                                                View Publication
                                            </Link>

                                        </div>

                                    </div>

                                </div>

                            ))}

                        </div>

                    )}

                </div>

            </div>

        </div>

    );

}
export default ResearcherDetails;
