import { useEffect, useState } from "react";

import DashboardNavbar from "../components/DashboardNavbar";
import Footer from "../components/Footer";
import InstitutionSidebar from "../components/InstitutionSidebar";

import api from "../services/api";

import "../styles/dashboard.css";

function InstitutionDashboard() {

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

                <InstitutionSidebar />

                <div className="dashboard-content">

                    {user ? (

                        <>

                            <h2>
                                🏛 Welcome, {user.full_name}
                            </h2>

                            <div className="cards">

                                <div className="card researchers-card">

                                    <h3>👨‍🔬 Researchers</h3>

                                    <h1>0</h1>

                                </div>

                                <div className="card papers-card">

                                    <h3>📄 Research Papers</h3>

                                    <h1>0</h1>

                                </div>

                                <div className="card collaborations-card">

                                    <h3>🤝 Collaborations</h3>

                                    <h1>0</h1>

                                </div>

                                <div className="card institutions-card">

                                    <h3>📊 Projects</h3>

                                    <h1>0</h1>

                                </div>

                            </div>

                            <div className="welcome-box">

                                <h3>Institution Details</h3>

                                <p><b>Email:</b> {user.email}</p>

                                <p><b>Institution:</b> {user.institution}</p>

                                <p><b>Website:</b> {user.website || "Not Added"}</p>

                                <p><b>Institution Type:</b> {user.institution_type || "Not Added"}</p>

                                <p><b>Established Year:</b> {user.established_year || "Not Added"}</p>

                                <p><b>Location:</b> {user.city}, {user.state}, {user.country}</p>

                            </div>

                            <div className="info-box">

                                <h3>Recent Activity</h3>

                                <ul>

                                    <li>No activity yet.</li>

                                    <li>Add researchers to your institution.</li>

                                    <li>Publish your first research paper.</li>

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

export default InstitutionDashboard;