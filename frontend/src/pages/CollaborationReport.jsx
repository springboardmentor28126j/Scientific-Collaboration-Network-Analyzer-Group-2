import { useEffect, useState } from "react";
import api from "../services/api";

import {
    ResponsiveContainer,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    CartesianGrid,
    Legend
} from "recharts";

function CollaborationReport() {

    const [chartData, setChartData] = useState([]);

    const [summary, setSummary] = useState({
        total: 0,
        Pending: 0,
        Accepted: 0,
        Rejected: 0
    });

    useEffect(() => {
        loadReport();
    }, []);

    const loadReport = async () => {

        try {

            const res = await api.get(
                "/analytics/collaboration-report"
            );

            setSummary(res.data);

            setChartData([
                {
                    status: "Pending",
                    count: res.data.Pending
                },
                {
                    status: "Accepted",
                    count: res.data.Accepted
                },
                {
                    status: "Rejected",
                    count: res.data.Rejected
                }
            ]);

        }

        catch (err) {

            console.log(err);

        }

    };

    return (

        <div className="container-fluid p-4">

            <h2
                className="fw-bold"
                style={{ color: "#143d7a" }}
            >
                Collaboration Report
            </h2>

            <p className="text-muted">
                Analyze collaboration request statistics.
            </p>

            <div className="row mt-4 mb-4">

                <div className="col-md-3">

                    <div className="card shadow border-0 rounded-4">

                        <div className="card-body">

                            <h6 className="text-muted">
                                Total Requests
                            </h6>

                            <h2 className="fw-bold text-primary">
                                {summary.total}
                            </h2>

                        </div>

                    </div>

                </div>

                <div className="col-md-3">

                    <div className="card shadow border-0 rounded-4">

                        <div className="card-body">

                            <h6 className="text-muted">
                                Pending
                            </h6>

                            <h2 className="fw-bold text-warning">
                                {summary.Pending}
                            </h2>

                        </div>

                    </div>

                </div>

                <div className="col-md-3">

                    <div className="card shadow border-0 rounded-4">

                        <div className="card-body">

                            <h6 className="text-muted">
                                Accepted
                            </h6>

                            <h2 className="fw-bold text-success">
                                {summary.Accepted}
                            </h2>

                        </div>

                    </div>

                </div>

                <div className="col-md-3">

                    <div className="card shadow border-0 rounded-4">

                        <div className="card-body">

                            <h6 className="text-muted">
                                Rejected
                            </h6>

                            <h2 className="fw-bold text-danger">
                                {summary.Rejected}
                            </h2>

                        </div>

                    </div>

                </div>

            </div>

            <div className="card shadow border-0 rounded-4">

                <div className="card-body">

                    <h4
                        className="fw-bold mb-4"
                        style={{ color: "#143d7a" }}
                    >
                        Collaboration Status
                    </h4>

                    <div
                        style={{
                            width: "100%",
                            height: 450
                        }}
                    >

                        <ResponsiveContainer>

                            <BarChart
                                data={chartData}
                            >

                                <CartesianGrid
                                    strokeDasharray="3 3"
                                />

                                <XAxis
                                    dataKey="status"
                                />

                                <YAxis />

                                <Tooltip />

                                <Legend />

                                <Bar
                                    dataKey="count"
                                    fill="#2563eb"
                                    radius={[6, 6, 0, 0]}
                                />

                            </BarChart>

                        </ResponsiveContainer>

                    </div>

                </div>

            </div>

            <div className="card shadow border-0 rounded-4 mt-4">

                <div className="card-body">

                    <h4
                        className="fw-bold mb-4"
                        style={{ color: "#143d7a" }}
                    >
                        Collaboration Summary
                    </h4>

                    <table className="table table-bordered table-hover">

                        <thead className="table-primary">

                            <tr>

                                <th>Status</th>

                                <th>Count</th>

                            </tr>

                        </thead>

                        <tbody>

                            <tr>

                                <td>Pending</td>

                                <td>{summary.Pending}</td>

                            </tr>

                            <tr>

                                <td>Accepted</td>

                                <td>{summary.Accepted}</td>

                            </tr>

                            <tr>

                                <td>Rejected</td>

                                <td>{summary.Rejected}</td>

                            </tr>

                            <tr className="table-light fw-bold">

                                <td>Total</td>

                                <td>{summary.total}</td>

                            </tr>

                        </tbody>

                    </table>

                </div>

            </div>

        </div>

    );

}

export default CollaborationReport;