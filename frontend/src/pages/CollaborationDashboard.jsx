import { useEffect, useState } from "react";
import api from "../services/api";

function CollaborationDashboard() {

    const [dashboard, setDashboard] = useState(null);

    useEffect(() => {
        loadDashboard();
    }, []);

    const loadDashboard = async () => {
        try {
            const res = await api.get("/analytics/project-dashboard");
            setDashboard(res.data);
        } catch (err) {
            console.log(err);
        }
    };

    if (!dashboard) {
        return <h3 className="text-center mt-5">Loading...</h3>;
    }

    return (

        <div className="container mt-4">

            <h2 className="mb-4">Collaboration Dashboard</h2>

            <div className="row">

                <div className="col-md-3 mb-3">
                    <div className="card text-center shadow">
                        <div className="card-body">
                            <h5>Total Projects</h5>
                            <h2>{dashboard.total_projects}</h2>
                        </div>
                    </div>
                </div>

                <div className="col-md-3 mb-3">
                    <div className="card text-center shadow">
                        <div className="card-body">
                            <h5>Members</h5>
                            <h2>{dashboard.total_members}</h2>
                        </div>
                    </div>
                </div>

                <div className="col-md-3 mb-3">
                    <div className="card text-center shadow">
                        <div className="card-body">
                            <h5>Milestones</h5>
                            <h2>{dashboard.total_milestones}</h2>
                        </div>
                    </div>
                </div>

                <div className="col-md-3 mb-3">
                    <div className="card text-center shadow">
                        <div className="card-body">
                            <h5>Tasks</h5>
                            <h2>{dashboard.total_tasks}</h2>
                        </div>
                    </div>
                </div>

            </div>

            <div className="row mt-3">

                <div className="col-md-4">
                    <div className="card shadow">
                        <div className="card-body">
                            <h5>Completed Tasks</h5>
                            <h3 className="text-success">
                                {dashboard.completed_tasks}
                            </h3>
                        </div>
                    </div>
                </div>

                <div className="col-md-4">
                    <div className="card shadow">
                        <div className="card-body">
                            <h5>Pending Tasks</h5>
                            <h3 className="text-danger">
                                {dashboard.pending_tasks}
                            </h3>
                        </div>
                    </div>
                </div>

                <div className="col-md-4">
                    <div className="card shadow">
                        <div className="card-body">
                            <h5>Project Progress</h5>

                            <div className="progress mt-3">

                                <div
                                    className="progress-bar bg-success"
                                    style={{
                                        width:
                                            dashboard.project_progress + "%"
                                    }}
                                >
                                    {dashboard.project_progress}%
                                </div>

                            </div>

                        </div>
                    </div>
                </div>

            </div>

        </div>

    );

}

export default CollaborationDashboard;