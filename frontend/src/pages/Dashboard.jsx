import { useEffect, useState } from "react";
import api from "../services/api";

import MainLayout from "../components/MainLayout";
import CustomCard from "../components/CustomCard";

function Dashboard() {

    const [dashboard, setDashboard] = useState({
        total_papers: 0,
        total_researchers: 0,
        total_institutions: 0,
        total_collaborations: 0,
    });

    useEffect(() => {

        api
            .get("/analytics/dashboard")
            .then((res) => {

                setDashboard(res.data);

            })
            .catch((err) => {

                console.log(err);

            });

    }, []);

    return (

        <MainLayout>

            <h2 className="fw-bold mb-4">

                <i className="bi bi-speedometer2 text-primary me-2"></i>

                Dashboard Overview

            </h2>

            <div className="row">

                <div className="col-lg-3 col-md-6 mb-4">

                    <CustomCard>

                        <div className="text-center">

                            <i className="bi bi-people-fill text-primary fs-1"></i>

                            <h5 className="mt-3">

                                Researchers

                            </h5>

                            <h2>

                                {dashboard.total_researchers}

                            </h2>

                        </div>

                    </CustomCard>

                </div>

                <div className="col-lg-3 col-md-6 mb-4">

                    <CustomCard>

                        <div className="text-center">

                            <i className="bi bi-file-earmark-text-fill text-success fs-1"></i>

                            <h5 className="mt-3">

                                Papers

                            </h5>

                            <h2>

                                {dashboard.total_papers}

                            </h2>

                        </div>

                    </CustomCard>

                </div>

                <div className="col-lg-3 col-md-6 mb-4">

                    <CustomCard>

                        <div className="text-center">

                            <i className="bi bi-building text-warning fs-1"></i>

                            <h5 className="mt-3">

                                Institutions

                            </h5>

                            <h2>

                                {dashboard.total_institutions}

                            </h2>

                        </div>

                    </CustomCard>

                </div>

                <div className="col-lg-3 col-md-6 mb-4">

                    <CustomCard>

                        <div className="text-center">

                            <i className="bi bi-diagram-3-fill text-danger fs-1"></i>

                            <h5 className="mt-3">

                                Collaborations

                            </h5>

                            <h2>

                                {dashboard.total_collaborations}

                            </h2>

                        </div>

                    </CustomCard>

                </div>

            </div>

            <div className="row">

                <div className="col-lg-8">

                    <CustomCard>

                        <h4>

                            🚀 Welcome

                        </h4>

                        <hr />

                        <p>

                            Welcome to the Scientific Collaboration Network Analyzer.

                            Manage Researchers, Institutions, Research Papers,

                            Collaborations and Analytics from one centralized dashboard.

                        </p>

                    </CustomCard>

                </div>

                <div className="col-lg-4">

                    <CustomCard>

                        <h4>

                            ⭐ Platform Highlights

                        </h4>

                        <hr />

                        <ul>

                            <li>Research Management</li>

                            <li>Institution Collaboration</li>

                            <li>Project Management</li>

                            <li>Timeline Tracking</li>

                            <li>Notifications</li>

                            <li>Analytics</li>

                        </ul>

                    </CustomCard>

                </div>

            </div>

        </MainLayout>

    );

}

export default Dashboard;