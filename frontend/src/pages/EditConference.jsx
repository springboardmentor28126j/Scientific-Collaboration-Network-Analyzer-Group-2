import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import api from "../services/api";

import DashboardNavbar from "../components/DashboardNavbar";
import ResearcherSidebar from "../components/ResearcherSidebar";
import Footer from "../components/Footer";

function EditConference() {

    const { id } = useParams();

    const navigate = useNavigate();

    const [conference, setConference] = useState({

        conference_name: "",
        organizer: "",
        venue: "",
        country: "",
        conference_date: "",
        submission_deadline: "",
        registration_deadline: "",
        registration_fee: "",
        conference_type: "",
        website: "",
        description: "",
        topics: "",
        status: ""

    });

    useEffect(() => {

        loadConference();

    }, []);

    const loadConference = async () => {

        try {

            const token = localStorage.getItem("token");

            const res = await api.get(

                `/conferences/${id}`,

                {

                    headers: {

                        Authorization: `Bearer ${token}`

                    }

                }

            );

            setConference(res.data);

        }

        catch (err) {

            console.log(err);

            alert("Unable to load conference.");

        }

    };

    const handleChange = (e) => {

        setConference({

            ...conference,

            [e.target.name]: e.target.value

        });

    };

    const updateConference = async (e) => {

        e.preventDefault();

        try {

            const token = localStorage.getItem("token");

            await api.put(

                `/conferences/${id}`,

                new URLSearchParams({

                    conference_name: conference.conference_name,

                    organizer: conference.organizer,

                    venue: conference.venue,

                    country: conference.country,

                    conference_date: conference.conference_date,

                    submission_deadline: conference.submission_deadline,

                    registration_deadline: conference.registration_deadline,

                    registration_fee: conference.registration_fee,

                    conference_type: conference.conference_type,

                    website: conference.website,

                    description: conference.description,

                    topics: conference.topics,

                    status: conference.status

                }),

                {

                    headers: {

                        Authorization: `Bearer ${token}`,

                        "Content-Type":
                            "application/x-www-form-urlencoded"

                    }

                }

            );

            alert("Conference Updated Successfully!");

            navigate("/my-conferences");

        }

        catch (err) {

            console.log(err);

            alert("Unable to update conference.");

        }

    };
        return (

        <>
            <DashboardNavbar />

            <div className="dashboard-container">

                <ResearcherSidebar />

                <div className="dashboard-content">

                    <h2>✏ Edit Conference</h2>

                    <form
                        className="profile-card"
                        onSubmit={updateConference}
                    >

                        <label>Conference Name</label>
                        <input
                            type="text"
                            name="conference_name"
                            value={conference.conference_name}
                            onChange={handleChange}
                            required
                        />

                        <label>Organizer</label>
                        <input
                            type="text"
                            name="organizer"
                            value={conference.organizer}
                            onChange={handleChange}
                            required
                        />

                        <label>Venue</label>
                        <input
                            type="text"
                            name="venue"
                            value={conference.venue}
                            onChange={handleChange}
                            required
                        />

                        <label>Country</label>
                        <input
                            type="text"
                            name="country"
                            value={conference.country}
                            onChange={handleChange}
                            required
                        />

                        <label>Conference Date</label>
                        <input
                            type="date"
                            name="conference_date"
                            value={conference.conference_date}
                            onChange={handleChange}
                            required
                        />

                        <label>Submission Deadline</label>
                        <input
                            type="date"
                            name="submission_deadline"
                            value={conference.submission_deadline}
                            onChange={handleChange}
                            required
                        />

                        <label>Registration Deadline</label>
                        <input
                            type="date"
                            name="registration_deadline"
                            value={conference.registration_deadline}
                            onChange={handleChange}
                            required
                        />

                        <label>Registration Fee</label>
                        <input
                            type="number"
                            name="registration_fee"
                            value={conference.registration_fee}
                            onChange={handleChange}
                            required
                        />

                        <label>Conference Type</label>
                        <input
                            type="text"
                            name="conference_type"
                            value={conference.conference_type}
                            onChange={handleChange}
                            required
                        />

                        <label>Website</label>
                        <input
                            type="text"
                            name="website"
                            value={conference.website || ""}
                            onChange={handleChange}
                        />

                        <label>Description</label>
                        <textarea
                            name="description"
                            rows="4"
                            value={conference.description || ""}
                            onChange={handleChange}
                        />

                        <label>Topics</label>
                        <textarea
                            name="topics"
                            rows="3"
                            value={conference.topics || ""}
                            onChange={handleChange}
                        />

                        <label>Status</label>

                        <select
                            name="status"
                            value={conference.status}
                            onChange={handleChange}
                        >

                            <option value="upcoming">Upcoming</option>
                            <option value="ongoing">Ongoing</option>
                            <option value="completed">Completed</option>
                            <option value="cancelled">Cancelled</option>

                        </select>

                        <br />

                        <button
                            type="submit"
                            className="edit-profile-btn"
                        >
                            💾 Save Changes
                        </button>

                        &nbsp;

                        <button
                            type="button"
                            className="delete-profile-btn"
                            onClick={() =>
                                navigate("/my-conferences")
                            }
                        >
                            Cancel
                        </button>

                    </form>

                </div>

            </div>

            <Footer />

        </>

    );

}

export default EditConference;