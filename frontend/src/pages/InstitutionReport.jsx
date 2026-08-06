import { useEffect, useState } from "react";
import api from "../services/api";

import {
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell,
    Tooltip,
    Legend
} from "recharts";

function InstitutionReport() {

    const [data, setData] = useState([]);

    const [summary, setSummary] = useState({
        totalInstitutions: 0,
        totalResearchers: 0
    });

    const COLORS = [
        "#2563eb",
        "#16a34a",
        "#ea580c",
        "#9333ea",
        "#dc2626",
        "#0891b2"
    ];

    useEffect(() => {

        loadData();

    }, []);

    const loadData = async () => {

        try {

            const res = await api.get("/analytics/institution-report");

            setData(res.data);

            let totalResearchers = 0;

            res.data.forEach(item => {
                totalResearchers += item.researchers;
            });

            setSummary({
                totalInstitutions: res.data.length,
                totalResearchers
            });

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
                Institution Report
            </h2>

            <p className="text-muted">
                Institution ranking based on registered researchers.
            </p>

            <div className="row mt-4 mb-4">

                <div className="col-md-6">

                    <div className="card shadow border-0 rounded-4">

                        <div className="card-body">

                            <h6 className="text-muted">
                                Total Institutions
                            </h6>

                            <h2 className="fw-bold text-primary">
                                {summary.totalInstitutions}
                            </h2>

                        </div>

                    </div>

                </div>

                <div className="col-md-6">

                    <div className="card shadow border-0 rounded-4">

                        <div className="card-body">

                            <h6 className="text-muted">
                                Total Researchers
                            </h6>

                            <h2 className="fw-bold text-success">
                                {summary.totalResearchers}
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
                        Institution Distribution
                    </h4>

                    <div
                        style={{
                            width: "100%",
                            height: 450
                        }}
                    >

                        <ResponsiveContainer>

                            <PieChart>

                                <Pie
                                    data={data}
                                    dataKey="researchers"
                                    nameKey="institution"
                                    outerRadius={160}
                                    label
                                >

                                    {

                                        data.map((entry, index) => (

                                            <Cell
                                                key={index}
                                                fill={
                                                    COLORS[
                                                        index % COLORS.length
                                                    ]
                                                }
                                            />

                                        ))

                                    }

                                </Pie>

                                <Tooltip />

                                <Legend />

                            </PieChart>

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
                        Institution Summary
                    </h4>

                    <table className="table table-bordered table-hover">

                        <thead className="table-primary">

                            <tr>

                                <th>Institution</th>

                                <th>Total Researchers</th>

                            </tr>

                        </thead>

                        <tbody>

                            {

                                data.map((item, index) => (

                                    <tr key={index}>

                                        <td>
                                            {item.institution}
                                        </td>

                                        <td>
                                            {item.researchers}
                                        </td>

                                    </tr>

                                ))

                            }

                        </tbody>

                    </table>

                </div>

            </div>

        </div>

    );

}

export default InstitutionReport;