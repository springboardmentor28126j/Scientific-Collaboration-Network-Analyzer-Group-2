import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";

import api from "../services/api";

import DashboardNavbar from "../components/DashboardNavbar";
import ResearcherSidebar from "../components/ResearcherSidebar";
import Footer from "../components/Footer";

function ConferenceDetails() {

    const { id } = useParams();

    const navigate = useNavigate();

    const [conference, setConference] = useState(null);

    useEffect(() => {

        loadConference();

    }, []);

    const loadConference = async () => {

        try {

            const res = await api.get(
                `/conferences/${id}`
            );

            setConference(res.data);

        }

        catch (err) {

            console.log(err);

        }

    };

    if (!conference) {

        return <h2 style={{ textAlign: "center" }}>Loading...</h2>;

    }

    return (

        <>

            <DashboardNavbar />

            <div className="dashboard-container">

                <ResearcherSidebar />

                <div className="dashboard-content">

                    <h2>Conference Details</h2>

                    <div className="profile-card">

                        <h3>{conference.conference_name}</h3>

                        <hr />

                        <p><strong>Organizer :</strong> {conference.organizer}</p>

                        <p><strong>Venue :</strong> {conference.venue}</p>

                        <p><strong>Country :</strong> {conference.country}</p>

                        <p><strong>Conference Date :</strong> {conference.conference_date}</p>

                        <p><strong>Submission Deadline :</strong> {conference.submission_deadline}</p>

                        <p><strong>Registration Deadline :</strong> {conference.registration_deadline}</p>

                        <p><strong>Registration Fee :</strong> ₹{conference.registration_fee}</p>

                        <p><strong>Conference Type :</strong> {conference.conference_type}</p>

                        <p><strong>Status :</strong> {conference.status}</p>

                        <p><strong>Topics :</strong> {conference.topics}</p>

                        <p><strong>Description :</strong></p>

                        <p>{conference.description}</p>

                        {

                            conference.website &&

                            <p>

                                <strong>Website :</strong>{" "}

                                <a

                                    href={conference.website}

                                    target="_blank"

                                    rel="noreferrer"

                                >

                                    Visit Website

                                </a>

                            </p>

                        }

                        {

                            conference.banner_image &&

                            <>

                                <h4>Conference Banner</h4>

                                <img

                                    src={`http://127.0.0.1:8000/${conference.banner_image}`}

                                    alt="Banner"

                                    width="350"

                                />

                            </>

                        }

                        {

                            conference.brochure_pdf &&

                            <>

                                <br />

                                <br />

                                <a

                                    href={`http://127.0.0.1:8000/${conference.brochure_pdf}`}

                                    target="_blank"

                                    rel="noreferrer"

                                >

                                    Download Brochure

                                </a>

                            </>

                        }

                        <br />
                        <br />

                        <button

                            className="edit-profile-btn"

                            onClick={() =>
                                navigate("/my-conferences")
                            }

                        >

                            Back

                        </button>

                    </div>

                </div>

            </div>

            <Footer />

        </>

    );

}

export default ConferenceDetails;