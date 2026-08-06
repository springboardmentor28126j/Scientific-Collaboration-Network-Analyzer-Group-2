import { useEffect, useState } from "react";
import api from "../services/api";

import {
    ResponsiveContainer,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    Legend,
    CartesianGrid
} from "recharts";

function PublicationReport() {

    const [chartData, setChartData] = useState([]);

    const [summary, setSummary] = useState({
        total_papers: 0,
        published: 0,
        submitted: 0,
        draft: 0,
        archived: 0
    });

    useEffect(() => {
        loadChart();
    }, []);

    const loadChart = async () => {

        try {

            const res = await api.get(
                "/analytics/publication-status-report"
            );

            setChartData(res.data);

            let total = 0;
            let published = 0;
            let submitted = 0;
            let draft = 0;
            let archived = 0;

            res.data.forEach((item) => {

                published += item.Published;
                submitted += item.Submitted;
                draft += item.Draft;
                archived += item.Archived;

                total +=
                    item.Published +
                    item.Submitted +
                    item.Draft +
                    item.Archived;

            });

            setSummary({
                total_papers: total,
                published,
                submitted,
                draft,
                archived
            });

        } catch (err) {

            console.log(err);

        }

    };

    return (

        <div className="container-fluid p-4">

            <h2
                className="fw-bold mb-2"
                style={{ color: "#143d7a" }}
            >
                Publication Report
            </h2>

            <p className="text-muted mb-4">
                Analyze publication statistics by year and publication status.
            </p>

            {/* Summary Cards */}

            <div className="row g-4 mb-4">

                <div className="col-lg-3 col-md-6">

                    <div className="card shadow border-0 rounded-4">

                        <div className="card-body text-center">

                            <h6 className="text-muted">
                                Total Papers
                            </h6>

                            <h2 className="fw-bold text-primary">
                                {summary.total_papers}
                            </h2>

                        </div>

                    </div>

                </div>

                <div className="col-lg-3 col-md-6">

                    <div className="card shadow border-0 rounded-4">

                        <div className="card-body text-center">

                            <h6 className="text-muted">
                                Published
                            </h6>

                            <h2 className="fw-bold text-success">
                                {summary.published}
                            </h2>

                        </div>

                    </div>

                </div>

                <div className="col-lg-3 col-md-6">

                    <div className="card shadow border-0 rounded-4">

                        <div className="card-body text-center">

                            <h6 className="text-muted">
                                Submitted
                            </h6>

                            <h2 className="fw-bold text-info">
                                {summary.submitted}
                            </h2>

                        </div>

                    </div>

                </div>

                <div className="col-lg-3 col-md-6">

                    <div className="card shadow border-0 rounded-4">

                        <div className="card-body text-center">

                            <h6 className="text-muted">
                                Draft
                            </h6>

                            <h2 className="fw-bold text-warning">
                                {summary.draft}
                            </h2>

                        </div>

                    </div>

                </div>

            </div>

            {/* Chart */}

            <div className="card shadow border-0 rounded-4 mb-4">

                <div className="card-body">

                    <h4
                        className="fw-bold mb-4"
                        style={{ color: "#143d7a" }}
                    >
                        Publication Status Analysis
                    </h4>

                    <div
                        style={{
                            width: "100%",
                            height: 450
                        }}
                    >

                        <ResponsiveContainer width="100%" height="100%">

                            <BarChart data={chartData}>

                                <CartesianGrid strokeDasharray="3 3" />

                                <XAxis dataKey="publication_year" />

                                <YAxis />

                                <Tooltip />

                                <Legend />

                                <Bar
                                    dataKey="Published"
                                    fill="#28a745"
                                />

                                <Bar
                                    dataKey="Submitted"
                                    fill="#0d6efd"
                                />

                                <Bar
                                    dataKey="Draft"
                                    fill="#ffc107"
                                />

                                <Bar
                                    dataKey="Archived"
                                    fill="#6c757d"
                                />

                            </BarChart>

                        </ResponsiveContainer>

                    </div>

                </div>

            </div>

            {/* Summary Table */}

            <div className="card shadow border-0 rounded-4">

                <div className="card-body">

                    <h4
                        className="fw-bold mb-4"
                        style={{ color: "#143d7a" }}
                    >
                        Publication Summary
                    </h4>

                    <table className="table table-bordered table-striped">

                        <tbody>

                            <tr>

                                <th>Total Papers</th>

                                <td>{summary.total_papers}</td>

                            </tr>

                            <tr>

                                <th>Published</th>

                                <td>{summary.published}</td>

                            </tr>

                            <tr>

                                <th>Submitted</th>

                                <td>{summary.submitted}</td>

                            </tr>

                            <tr>

                                <th>Draft</th>

                                <td>{summary.draft}</td>

                            </tr>

                            <tr>

                                <th>Archived</th>

                                <td>{summary.archived}</td>

                            </tr>

                        </tbody>

                    </table>

                </div>

            </div>

        </div>

    );

}

export default PublicationReport;