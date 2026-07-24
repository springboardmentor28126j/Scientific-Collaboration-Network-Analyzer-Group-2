import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

import DashboardNavbar from "../components/DashboardNavbar";
import ResearcherSidebar from "../components/ResearcherSidebar";
import Footer from "../components/Footer";

import "../styles/dashboard.css";
import "../styles/profile.css";

function AddConference() {

    const navigate = useNavigate();

    const [banner, setBanner] = useState(null);
    const [brochure, setBrochure] = useState(null);

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
        status: "Upcoming"
    });

    const handleChange = (e) => {
        setConference({
            ...conference,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {

        e.preventDefault();

        try {

            const token = localStorage.getItem("token");

            const formData = new FormData();

            Object.keys(conference).forEach((key) => {
                formData.append(key, conference[key]);
            });

            if (banner)
                formData.append("banner", banner);

            if (brochure)
                formData.append("brochure", brochure);

            await api.post(
                "/conferences/",
                formData,
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                        "Content-Type": "multipart/form-data"
                    }
                }
            );

            alert("Conference Added Successfully");

            navigate("/my-conferences");

        } catch (err) {

            console.log(err);

            alert("Upload Failed");

        }

    };

    return (
        <>
            <DashboardNavbar />

            <div className="dashboard-container">

                <ResearcherSidebar />

                <div className="dashboard-content">

                    <h2>Add Conference</h2>

                    <div className="profile-card">

                        <form onSubmit={handleSubmit}>

                            <input
                                type="text"
                                name="conference_name"
                                placeholder="Conference Name"
                                onChange={handleChange}
                                required
                            />

                            <input
                                type="text"
                                name="organizer"
                                placeholder="Organizer"
                                onChange={handleChange}
                                required
                            />

                            <input
                                type="text"
                                name="venue"
                                placeholder="Venue"
                                onChange={handleChange}
                                required
                            />

                            <input
                                type="text"
                                name="country"
                                placeholder="Country"
                                onChange={handleChange}
                                required
                            />

                            <label>Conference Date</label>

                            <input
                                type="date"
                                name="conference_date"
                                onChange={handleChange}
                                required
                            />

                            <label>Submission Deadline</label>

                            <input
                                type="date"
                                name="submission_deadline"
                                onChange={handleChange}
                                required
                            />

                            <label>Registration Deadline</label>

                            <input
                                type="date"
                                name="registration_deadline"
                                onChange={handleChange}
                                required
                            />

                            <input
                                type="number"
                                name="registration_fee"
                                placeholder="Registration Fee"
                                onChange={handleChange}
                            />

                            <input
                                type="text"
                                name="conference_type"
                                placeholder="Conference Type"
                                onChange={handleChange}
                            />

                            <input
                                type="text"
                                name="website"
                                placeholder="Website"
                                onChange={handleChange}
                            />

                            <textarea
                                rows="5"
                                name="description"
                                placeholder="Description"
                                onChange={handleChange}
                            />

                            <input
                                type="text"
                                name="topics"
                                placeholder="Topics"
                                onChange={handleChange}
                            />

                            <select
                                name="status"
                                onChange={handleChange}
                            >
                                <option>Upcoming</option>
                                <option>Open</option>
                                <option>Completed</option>
                            </select>

                            <label>Conference Banner</label>

                            <input
                                type="file"
                                accept="image/*"
                                onChange={(e) =>
                                    setBanner(e.target.files[0])
                                }
                            />

                            <label>Conference Brochure (PDF)</label>

                            <input
                                type="file"
                                accept=".pdf"
                                onChange={(e) =>
                                    setBrochure(e.target.files[0])
                                }
                            />

                            <button
                                className="edit-profile-btn"
                                type="submit"
                            >
                                Add Conference
                            </button>

                        </form>

                    </div>

                </div>

            </div>

            <Footer />

        </>
    );

}

export default AddConference;