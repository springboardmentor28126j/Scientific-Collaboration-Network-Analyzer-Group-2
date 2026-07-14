import { useEffect, useState } from "react";

import DashboardNavbar from "../components/DashboardNavbar";
import Footer from "../components/Footer";
import ResearcherSidebar from "../components/ResearcherSidebar";

import api from "../services/api";

import "../styles/dashboard.css";

function ResearcherDashboard() {

    const [user, setUser] = useState(null);

    useEffect(() => {

        const fetchUser = async () => {

            try {

                const token = localStorage.getItem("token");

                const response = await api.get("/auth/me", {

                    headers: {

                        Authorization: `Bearer ${token}`

                    }

                });

                setUser(response.data);

            }

            catch (error) {

                console.log(error);

            }

        };

        fetchUser();

    }, []);

    return (

        <>

           <DashboardNavbar />
           
            <div className="dashboard-container">

                <ResearcherSidebar />

                <div className="dashboard-content">

                    {user ? (

                        <>

                            <h2>
                                Welcome, {user.full_name} 👋
                            </h2>

                            <div className="cards">

                                <div className="card papers-card">

                                    <h3>📄 My Papers</h3>

                                    <h1>0</h1>

                                </div>

                                <div className="card collaborations-card">

                                    <h3>🤝 Collaborations</h3>

                                    <h1>0</h1>

                                </div>

                                <div className="card researchers-card">

                                    <h3>📊 Citations</h3>

                                    <h1>0</h1>

                                </div>

                                <div className="card institutions-card">

                                    <h3>👀 Profile Views</h3>

                                    <h1>0</h1>

                                </div>

                            </div>

                            <div className="welcome-box">

                                <h3>Your Profile</h3>

                                <p><b>Email:</b> {user.email}</p>

                                <p><b>Institution:</b> {user.institution}</p>

                                <p><b>Department:</b> {user.department}</p>

                                <p><b>Designation:</b> {user.designation}</p>

                                <p><b>Specialization:</b> {user.specialization}</p>

                            </div>

                            <div className="info-box">

                                <h3>Recent Activity</h3>

                                <ul>

                                    <li>No activity yet.</li>

                                    <li>Upload your first research paper.</li>

                                    <li>Start collaborating with researchers.</li>

                                </ul>

                            </div>

                        </>

                    ) : (

                        <h2>Loading...</h2>

                    )}

                </div>

            </div>

            <Footer />

        </>

    );

}

export default ResearcherDashboard;