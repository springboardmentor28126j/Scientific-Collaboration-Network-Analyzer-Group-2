import { useState } from "react";

export default function ResearcherForm({
    initialValues,
    onSubmit,
    loading,
}) {

    const [form, setForm] = useState(
        initialValues || {
            first_name: "",
            last_name: "",
            bio: "",
            phone: "",
            experience: 0,
            orcid: "",
            google_scholar: "",
            research_gate: "",
            linkedin: "",
        }
    );

    const handleChange = (e) => {
        setForm({
            ...form,
            [e.target.name]: e.target.value,
        });
    };

    const submit = (e) => {
        e.preventDefault();
        onSubmit(form);
    };

    return (

        <form onSubmit={submit}>

            <div className="mb-3">
                <label className="form-label">
                    First Name
                </label>

                <input
                    className="form-control"
                    name="first_name"
                    value={form.first_name}
                    onChange={handleChange}
                    required
                />
            </div>

            <div className="mb-3">
                <label className="form-label">
                    Last Name
                </label>

                <input
                    className="form-control"
                    name="last_name"
                    value={form.last_name}
                    onChange={handleChange}
                    required
                />
            </div>

            <div className="mb-3">

                <label>Bio</label>

                <textarea
                    className="form-control"
                    rows="4"
                    name="bio"
                    value={form.bio}
                    onChange={handleChange}
                />

            </div>

            <div className="row">

                <div className="col-md-6 mb-3">

                    <label>Phone</label>

                    <input
                        className="form-control"
                        name="phone"
                        value={form.phone}
                        onChange={handleChange}
                    />

                </div>

                <div className="col-md-6 mb-3">

                    <label>Experience</label>

                    <input
                        type="number"
                        className="form-control"
                        name="experience"
                        value={form.experience}
                        onChange={handleChange}
                    />

                </div>

            </div>

            <div className="mb-3">

                <label>ORCID</label>

                <input
                    className="form-control"
                    name="orcid"
                    value={form.orcid}
                    onChange={handleChange}
                />

            </div>

            <div className="mb-3">

                <label>Google Scholar</label>

                <input
                    className="form-control"
                    name="google_scholar"
                    value={form.google_scholar}
                    onChange={handleChange}
                />

            </div>

            <div className="mb-3">

                <label>ResearchGate</label>

                <input
                    className="form-control"
                    name="research_gate"
                    value={form.research_gate}
                    onChange={handleChange}
                />

            </div>

            <div className="mb-4">

                <label>LinkedIn</label>

                <input
                    className="form-control"
                    name="linkedin"
                    value={form.linkedin}
                    onChange={handleChange}
                />

            </div>

            <button
                className="btn btn-primary"
                disabled={loading}
            >
                {loading ? "Saving..." : "Save Researcher"}
            </button>

        </form>
    );
}
