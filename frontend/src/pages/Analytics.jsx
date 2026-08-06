import { useEffect, useState } from "react";
import api from "../services/api";

function Analytics() {

    const [topResearchers, setTopResearchers] = useState([]);
    const [topInstitutions, setTopInstitutions] = useState([]);

    useEffect(() => {
        loadAnalytics();
    }, []);

    const loadAnalytics = async () => {

        try {

            const researchers = await api.get("/analytics/top-researchers");
            const institutions = await api.get("/analytics/top-institutions");

            setTopResearchers(researchers.data);
            setTopInstitutions(institutions.data);

        } catch (err) {

            console.log(err);

        }

    };

    return (

        <div className="container mt-4">

            <h2 className="mb-4">
                📊 Analytics Dashboard
            </h2>

            <div className="row">

                {/* Top Researchers */}

                <div className="col-md-6">

                    <div className="card shadow">

                        <div className="card-header bg-primary text-white">

                            <h5 className="mb-0">
                                🏆 Top Researchers
                            </h5>

                        </div>

                        <div className="card-body">

                            <table className="table table-bordered">

                                <thead>

                                    <tr>

                                        <th>Name</th>
                                        <th>Institution</th>
                                        <th>Papers</th>

                                    </tr>

                                </thead>

                                <tbody>

                                    {topResearchers.map((r) => (

                                        <tr key={r.full_name}>

                                            <td>{r.full_name}</td>

                                            <td>{r.institution}</td>

                                            <td>{r.total_publications}</td>

                                        </tr>

                                    ))}

                                </tbody>

                            </table>

                        </div>

                    </div>

                </div>


                {/* Top Institutions */}

                <div className="col-md-6">

                    <div className="card shadow">

                        <div className="card-header bg-success text-white">

                            <h5 className="mb-0">
                                🏛 Top Institutions
                            </h5>

                        </div>

                        <div className="card-body">

                            <table className="table table-bordered">

                                <thead>

                                    <tr>

                                        <th>Institution</th>

                                        <th>Researchers</th>

                                    </tr>

                                </thead>

                                <tbody>

                                    {topInstitutions.map((i) => (

                                        <tr key={i.institution}>

                                            <td>{i.institution}</td>

                                            <td>{i.researchers}</td>

                                        </tr>

                                    ))}

                                </tbody>

                            </table>

                        </div>

                    </div>

                </div>

            </div>

        </div>

    );

}

export default Analytics;