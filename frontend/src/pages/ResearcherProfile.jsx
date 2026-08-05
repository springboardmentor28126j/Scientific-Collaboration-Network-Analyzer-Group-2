import { useEffect, useState } from "react";

import DashboardNavbar from "../components/DashboardNavbar";
import ResearcherSidebar from "../components/ResearcherSidebar";
import EditProfileModal from "../components/EditProfileModal";
import CollaborationRequestModal from "../components/CollaborationRequestModal";
import Footer from "../components/Footer";

import api from "../services/api";

import "../styles/dashboard.css";
import "../styles/profile.css";

function ResearcherProfile() {

    const [user, setUser] = useState(null);

    const [showModal, setShowModal] = useState(false);

    const [showCollaborationModal, setShowCollaborationModal] = useState(false);

    useEffect(() => {

        const fetchProfile = async () => {

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

        fetchProfile();

    }, []);

    if (!user) {

        return <h2 style={{ padding: "40px" }}>Loading...</h2>;

    }

    return (

        <>

            <DashboardNavbar />

            <div className="dashboard-container">

                <ResearcherSidebar />

                <div className="dashboard-content">

                    <h2 className="fw-bold mb-4">

                        👤 My Profile

                    </h2>

                    {/* Statistics */}

                    <div className="row mb-4">

                        <div className="col-md-4 mb-3">

                            <div className="card border-0 shadow rounded-4">

                                <div className="card-body text-center">

                                    <i className="bi bi-file-earmark-text-fill text-primary fs-1"></i>

                                    <h2 className="mt-3">12</h2>

                                    <p className="text-muted mb-0">

                                        Total Papers

                                    </p>

                                </div>

                            </div>

                        </div>

                        <div className="col-md-4 mb-3">

                            <div className="card border-0 shadow rounded-4">

                                <div className="card-body text-center">

                                    <i className="bi bi-people-fill text-success fs-1"></i>

                                    <h2 className="mt-3">5</h2>

                                    <p className="text-muted mb-0">

                                        Collaborations

                                    </p>

                                </div>

                            </div>

                        </div>

                        <div className="col-md-4 mb-3">

                            <div className="card border-0 shadow rounded-4">

                                <div className="card-body text-center">

                                    <i className="bi bi-folder-fill text-warning fs-1"></i>

                                    <h2 className="mt-3">3</h2>

                                    <p className="text-muted mb-0">

                                        Projects

                                    </p>

                                </div>

                            </div>

                        </div>

                    </div>

                    {/* Profile */}

                    <div className="profile-card">

                        <div className="profile-header">

                            <div className="profile-avatar">

                                {user.full_name.charAt(0).toUpperCase()}

                            </div>

                            <div>

                                <h2>{user.full_name}</h2>

                                <p>{user.designation}</p>

                            </div>

                        </div>

                        <div className="profile-grid">

                            <div>

                                <strong>Email</strong>

                                <span>{user.email}</span>

                            </div>

                            <div>

                                <strong>Phone</strong>

                                <span>{user.phone_number || "-"}</span>

                            </div>

                            <div>

                                <strong>Institution</strong>

                                <span>{user.institution}</span>

                            </div>

                            <div>

                                <strong>Department</strong>

                                <span>{user.department}</span>

                            </div>

                            <div>

                                <strong>Designation</strong>

                                <span>{user.designation}</span>

                            </div>

                            <div>

                                <strong>Specialization</strong>

                                <span>{user.specialization}</span>

                            </div>

                            <div>

                                <strong>Research Interests</strong>

                                <span>{user.research_interests}</span>

                            </div>

                            <div>

                                <strong>Country</strong>

                                <span>{user.country}</span>

                            </div>

                            <div>

                                <strong>State</strong>

                                <span>{user.state}</span>

                            </div>

                            <div>

                                <strong>City</strong>

                                <span>{user.city}</span>

                            </div>

                            <div>

                                <strong>Website</strong>

                                <span>{user.website || "-"}</span>

                            </div>

                        </div>

                        <div
                            style={{
                                display: "flex",
                                gap: "15px",
                                marginTop: "25px"
                            }}
                        >

                            <button

                                className="edit-profile-btn"

                                onClick={() => setShowModal(true)}

                            >

                                ✏ Edit Profile

                            </button>

                            <button

                                className="btn btn-primary rounded-pill px-4"

                                onClick={() =>
                                    setShowCollaborationModal(true)
                                }

                            >

                                🤝 Collaborate

                            </button>

                        </div>

                    </div>

                </div>

            </div>

            {

                showModal && (

                    <EditProfileModal

                        user={user}

                        onClose={() => setShowModal(false)}

                        onUpdate={(updatedUser) =>
                            setUser(updatedUser)
                        }

                    />

                )

            }

            {

                showCollaborationModal && (

                    <CollaborationRequestModal

                        onClose={() =>
                            setShowCollaborationModal(false)
                        }

                    />

                )

            }

            <Footer />

        </>

    );

}

export default ResearcherProfile;