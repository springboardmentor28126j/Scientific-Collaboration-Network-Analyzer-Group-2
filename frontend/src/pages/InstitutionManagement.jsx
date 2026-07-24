import { useEffect, useState } from "react";

import DashboardNavbar from "../components/DashboardNavbar";
import ResearcherSidebar from "../components/ResearcherSidebar";
import Footer from "../components/Footer";

import api from "../services/api";

function InstitutionManagement() {

    const [institutions, setInstitutions] = useState([]);
    const [country, setCountry] = useState("");

   const [form, setForm] = useState({

    institution_name: "",

    country: "",

    city: "",

    website: "",

    established_year: ""

});

    useEffect(() => {
        loadInstitutions();
    }, []);

    const loadInstitutions = async () => {

        try {

            const res = await api.get("/institutions");
            setInstitutions(res.data);

        } catch (err) {

            console.log(err);

        }

    };

    const searchInstitution = async () => {

        try {

            if (!country.trim()) {

                loadInstitutions();
                return;

            }

            const res = await api.get(
                `/institutions/search?country=${country}`
            );

            setInstitutions(res.data);

        } catch (err) {

            console.log(err);

        }

    };

    const handleChange = (e) => {

        setForm({
            ...form,
            [e.target.name]: e.target.value
        });

    };

    const addInstitution = async (e) => {

        e.preventDefault();

        try {

            await api.post("/institutions", form);

            alert("Institution Added Successfully ✅");

            setForm({

    institution_name: "",

    country: "",

    city: "",

    website: "",

    established_year: ""

});

            loadInstitutions();

        } catch (err) {

            console.log(err);

            alert("Unable to add institution.");

        }

    };

    return (

        <>
            <DashboardNavbar />

            <div className="dashboard-container">

                <ResearcherSidebar />

                <div className="dashboard-content">

                    <h2>🏛 Institution Management</h2>

                    {/* Add Institution */}

                    <div className="profile-card">

                        <h3>Add New Institution</h3>

                        <form onSubmit={addInstitution}>

                            <input
                                type="text"
                               name="institution_name"
                                placeholder="Institution Name"
                               value={form.institution_name}
                                onChange={handleChange}
                                required
                            />

                            <br /><br />

                            <input
                                type="text"
                                name="country"
                                placeholder="Country"
                                value={form.country}
                                onChange={handleChange}
                                required
                            />

                            <br /><br />

                            <input
                                type="text"
                                name="city"
                                placeholder="City"
                                value={form.city}
                                onChange={handleChange}
                                required
                            />

                            <br /><br />

                            <input
                                type="url"
                                name="website"
                                placeholder="Website (Optional)"
                                value={form.website}
                                onChange={handleChange}
                            />
                            <input
    type="number"
    name="established_year"
    placeholder="Established Year"
    value={form.established_year}
    onChange={handleChange}
/>

<br /><br />

                            <br /><br />

                            <button
                                className="edit-profile-btn"
                                type="submit"
                            >
                                ➕ Add Institution
                            </button>

                        </form>

                    </div>

                    <br />

                    {/* Search */}

                    <div className="profile-card">

                        <h3>Search Institution</h3>

                        <input
                            type="text"
                            placeholder="Enter Country"
                            value={country}
                            onChange={(e) => setCountry(e.target.value)}
                        />

                        <button
                            className="edit-profile-btn"
                            style={{ marginLeft: "10px" }}
                            onClick={searchInstitution}
                        >
                            🔍 Search
                        </button>

                        <button
                            className="edit-profile-btn"
                            style={{ marginLeft: "10px" }}
                            onClick={() => {
                                setCountry("");
                                loadInstitutions();
                            }}
                        >
                            Refresh
                        </button>

                    </div>

                    <br />

                    {/* Table */}

                    <table className="table">

                        <thead>

                            <tr>

                                <th>ID</th>
                                <th>Name</th>
                                <th>Country</th>
                                <th>City</th>
                                <th>Website</th>

                            </tr>

                        </thead>

                        <tbody>

                            {

                                institutions.length > 0 ?

                                    institutions.map((inst) => (

                                        <tr key={inst.id}>

                                            <td>{inst.id}</td>

                                            <td>{inst.institution_name}</td>

                                            <td>{inst.country}</td>

                                            <td>{inst.city}</td>

                                            <td>

                                                {

                                                    inst.website ?

                                                        <a
                                                            href={inst.website}
                                                            target="_blank"
                                                            rel="noreferrer"
                                                        >
                                                            Visit
                                                        </a>

                                                        :

                                                        "-"

                                                }

                                            </td>

                                        </tr>

                                    ))

                                    :

                                    <tr>

                                        <td
                                            colSpan="5"
                                            style={{ textAlign: "center" }}
                                        >
                                            No Institutions Found
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

export default InstitutionManagement;