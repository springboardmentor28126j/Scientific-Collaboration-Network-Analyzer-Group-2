import { useState } from "react";

import api from "../services/api";

function EditProfileModal({

    user,
    onClose,
    onUpdate

}) {

    const [form, setForm] = useState({

        full_name: user.full_name,
        phone_number: user.phone_number,
        institution: user.institution,
        department: user.department,
        designation: user.designation,
        specialization: user.specialization,
        research_interests: user.research_interests,
        country: user.country,
        state: user.state,
        city: user.city,
        website: user.website || ""

    });

    const handleChange = (e) => {

        setForm({

            ...form,

            [e.target.name]: e.target.value

        });

    };

    const saveProfile = async () => {

        try {

            const token = localStorage.getItem("token");

            const response = await api.put(

                "/auth/update-profile",

                form,

                {

                    headers: {

                        Authorization: `Bearer ${token}`

                    }

                }

            );

            alert("✅ Profile Updated Successfully");

            onUpdate(response.data);

            onClose();

        }

        catch {

            alert("❌ Failed to update profile");

        }

    };

    return (

        <div className="modal-overlay">

            <div className="modal">

                <h2>Edit Profile</h2>

                <input
                    name="full_name"
                    value={form.full_name}
                    onChange={handleChange}
                    placeholder="Full Name"
                />

                <input
                    name="phone_number"
                    value={form.phone_number}
                    onChange={handleChange}
                    placeholder="Phone Number"
                />

                <input
                    name="institution"
                    value={form.institution}
                    onChange={handleChange}
                    placeholder="Institution"
                />

                <input
                    name="department"
                    value={form.department}
                    onChange={handleChange}
                    placeholder="Department"
                />

                <input
                    name="designation"
                    value={form.designation}
                    onChange={handleChange}
                    placeholder="Designation"
                />

                <input
                    name="specialization"
                    value={form.specialization}
                    onChange={handleChange}
                    placeholder="Specialization"
                />

                <input
                    name="research_interests"
                    value={form.research_interests}
                    onChange={handleChange}
                    placeholder="Research Interests"
                />

                <input
                    name="country"
                    value={form.country}
                    onChange={handleChange}
                    placeholder="Country"
                />

                <input
                    name="state"
                    value={form.state}
                    onChange={handleChange}
                    placeholder="State"
                />

                <input
                    name="city"
                    value={form.city}
                    onChange={handleChange}
                    placeholder="City"
                />

                <input
                    name="website"
                    value={form.website}
                    onChange={handleChange}
                    placeholder="Website"
                />

                <div className="modal-buttons">

                    <button

                        className="save-btn"

                        onClick={saveProfile}

                    >

                        Save

                    </button>

                    <button

                        className="cancel-btn"

                        onClick={onClose}

                    >

                        Cancel

                    </button>

                </div>

            </div>

        </div>

    );

}

export default EditProfileModal;