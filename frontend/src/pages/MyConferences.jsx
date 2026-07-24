import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../services/api";

import DashboardNavbar from "../components/DashboardNavbar";
import ResearcherSidebar from "../components/ResearcherSidebar";
import Footer from "../components/Footer";

function MyConferences() {

    const navigate = useNavigate();

    const [conferences, setConferences] = useState([]);

    useEffect(() => {

        loadConferences();

    }, []);

    const loadConferences = async () => {

        try {

            const token = localStorage.getItem("token");

            const res = await api.get(
                "/conferences/my-conferences",
                {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                }
            );

            setConferences(res.data);

        }
        catch (error) {

            console.log(error);

        }

    };

    const deleteConference = async (id) => {

        const confirmDelete = window.confirm(
            "Are you sure you want to delete this conference?"
        );

        if (!confirmDelete) return;

        try {

            const token = localStorage.getItem("token");

            await api.delete(
                `/conferences/${id}`,
                {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                }
            );

            alert("Conference deleted successfully.");

            loadConferences();

        }
        catch (error) {

            console.log(error);

            alert("Unable to delete conference.");

        }

    };

    return (

        <>
            <DashboardNavbar />

            <div className="dashboard-container">

                <ResearcherSidebar />

                <div className="dashboard-content">

                    <h2>📅 My Conferences</h2>

                    <table className="table">

                        <thead>

                            <tr>

                                <th>Name</th>
                                <th>Venue</th>
                                <th>Date</th>
                                <th>Status</th>
                                <th>Actions</th>

                            </tr>

                        </thead>

                        <tbody>

                            {
                                conferences.length > 0 ?

                                    conferences.map((c) => (

                                        <tr key={c.id}>

                                            <td>{c.conference_name}</td>

                                            <td>{c.venue}</td>

                                            <td>{c.conference_date}</td>

                                            <td>{c.status}</td>

                                            <td>

                                                <button
                                                    className="edit-profile-btn"
                                                    onClick={() =>
                                                        navigate(`/conference/${c.id}`)
                                                    }
                                                >
                                                    👁 View
                                                </button>

                                                &nbsp;

                                                <button
                                                    className="edit-profile-btn"
                                                    onClick={() =>
                                                        navigate(`/edit-conference/${c.id}`)
                                                    }
                                                >
                                                    ✏ Edit
                                                </button>

                                                &nbsp;

                                                <button
                                                    className="delete-profile-btn"
                                                    onClick={() =>
                                                        deleteConference(c.id)
                                                    }
                                                >
                                                    🗑 Delete
                                                </button>

                                            </td>

                                        </tr>

                                    ))

                                    :

                                    <tr>

                                        <td
                                            colSpan="5"
                                            style={{
                                                textAlign: "center"
                                            }}
                                        >
                                            No Conferences Found
                                        </td>

                                    </tr>

                            }

                        </tbody>

                    </table>

                </div>

            </div>

            <Footer />

        </>

    );

}

export default MyConferences;