import { useEffect, useState } from "react";
import api from "../services/api";

import {
    ResponsiveContainer,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Cell
} from "recharts";

function ResearchReport() {

    const [researchers, setResearchers] = useState([]);

    useEffect(() => {
        loadResearchers();
    }, []);

    const loadResearchers = async () => {

        try {

            const res = await api.get("/analytics/top-researchers");

            setResearchers(res.data);

        }

        catch (err) {

            console.log(err);

        }

    };

    const colors = [
        "#0d6efd",
        "#198754",
        "#ffc107",
        "#dc3545",
        "#6f42c1"
    ];

    return (

        <div className="container-fluid p-4">

            <h2
                className="fw-bold"
                style={{ color: "#143d7a" }}
            >
                Research Report
            </h2>

            <p className="text-muted">
                Top Researchers based on Publications
            </p>

            <div className="row mb-4">

                <div className="col-md-4">

                    <div className="card shadow border-0 rounded-4">

                        <div className="card-body text-center">

                            <h6 className="text-muted">
                                Researchers Displayed
                            </h6>

                            <h2 className="fw-bold text-primary">
                                {researchers.length}
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
                        Top Researchers
                    </h4>

                    <div
                        style={{
                            width: "100%",
                            height: 420
                        }}
                    >

                        <ResponsiveContainer>

                            <BarChart
                                data={researchers}
                                layout="vertical"
                                margin={{
                                    top: 20,
                                    right: 30,
                                    left: 70,
                                    bottom: 10
                                }}
                            >

                                <CartesianGrid strokeDasharray="3 3" />

                                <XAxis
                                    type="number"
                                />

                                <YAxis
                                    type="category"
                                    dataKey="full_name"
                                />

                                <Tooltip />

                                <Bar
                                    dataKey="total_publications"
                                    radius={[0, 10, 10, 0]}
                                >

                                    {researchers.map((entry, index) => (

                                        <Cell
                                            key={index}
                                            fill={colors[index % colors.length]}
                                        />

                                    ))}

                                </Bar>

                            </BarChart>

                        </ResponsiveContainer>

                    </div>

                </div>

            </div>

            <div className="card shadow border-0 rounded-4 mt-4">

                <div className="card-body">

                    <h4
                        className="fw-bold mb-3"
                        style={{ color: "#143d7a" }}
                    >
                        Researcher Details
                    </h4>

                    <table className="table table-hover align-middle">

                        <thead className="table-primary">

                            <tr>

                                <th>#</th>
                                <th>Name</th>
                                <th>Institution</th>
                                <th>Total Publications</th>

                            </tr>

                        </thead>

                        <tbody>

                            {researchers.map((researcher, index) => (

                                <tr key={index}>

                                    <td>{index + 1}</td>

                                    <td>
                                        {researcher.full_name}
                                    </td>

                                    <td>
                                        {researcher.institution}
                                    </td>

                                    <td>

                                        <span className="badge bg-success fs-6">

                                            {researcher.total_publications}

                                        </span>

                                    </td>

                                </tr>

                            ))}

                        </tbody>

                    </table>

                </div>

            </div>

        </div>

    );

}

export default ResearchReport;