import { Link } from "react-router-dom";

function Reports() {

    const reports = [

        {
            title: "Publication Report",
            description: "View publication statistics and yearly analysis.",
            path: "/publication-report",
            color: "#2563eb",
            icon: "bi-bar-chart-line-fill"
        },

        {
            title: "Research Report",
            description: "Top researchers and publication insights.",
            path: "/reports/research",
            color: "#16a34a",
            icon: "bi-people-fill"
        },

        {
            title: "Institution Report",
            description: "Institution performance and rankings.",
            path: "/reports/institution",
            color: "#ea580c",
            icon: "bi-building-fill"
        },

        {
            title: "Collaboration Report",
            description: "Collaboration requests and status analysis.",
            path: "/reports/collaboration",
            color: "#9333ea",
            icon: "bi-diagram-3-fill"
        }

    ];

    return (

        <div className="container py-5">

            <h1 className="fw-bold mb-2">
                📊 Reports Dashboard
            </h1>

            <p className="text-muted mb-5">
                View analytics and graphical reports of the Scientific Collaboration Network.
            </p>

            <div className="row">

                {reports.map((report, index) => (

                    <div
                        className="col-lg-6 col-md-6 mb-4"
                        key={index}
                    >

                        <div
                            className="card shadow-lg border-0 rounded-4 h-100"
                            style={{
                                transition: "0.3s",
                                cursor: "pointer"
                            }}
                        >

                            <div className="card-body p-4">

                                <div
                                    className="d-flex align-items-center justify-content-center rounded-circle mb-3"
                                    style={{
                                        width: "70px",
                                        height: "70px",
                                        backgroundColor: report.color,
                                        color: "white",
                                        fontSize: "30px"
                                    }}
                                >

                                    <i className={`bi ${report.icon}`}></i>

                                </div>

                                <h3
                                    className="fw-bold"
                                    style={{
                                        color: report.color
                                    }}
                                >
                                    {report.title}
                                </h3>

                                <p
                                    className="text-muted mt-3"
                                    style={{
                                        minHeight: "55px"
                                    }}
                                >
                                    {report.description}
                                </p>

                                <Link
                                    to={report.path}
                                    className="btn btn-primary mt-3"
                                >
                                    <i className="bi bi-graph-up-arrow me-2"></i>
                                    View Report
                                </Link>

                            </div>

                        </div>

                    </div>

                ))}

            </div>

        </div>

    );

}

export default Reports;