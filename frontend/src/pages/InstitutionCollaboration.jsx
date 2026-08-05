import { useEffect, useState } from "react";
import api from "../services/api";
import PageHeader from "../components/PageHeader";
import CustomCard from "../components/CustomCard";

function InstitutionCollaboration() {

    const [institutions, setInstitutions] = useState([]);

    const [senderInstitution, setSenderInstitution] = useState("");
    const [receiverInstitution, setReceiverInstitution] = useState("");
    const [projectTitle, setProjectTitle] = useState("");
    const [purpose, setPurpose] = useState("");

    useEffect(() => {
        loadInstitutions();
    }, []);

    const loadInstitutions = async () => {

        try {

            const res = await api.get("/institutions/");

            console.log("Institutions:", res.data);

            setInstitutions(res.data);

        } catch (err) {

            console.error(err);

            alert("Unable to load institutions.");

        }

    };

    const sendRequest = async () => {

        if (
            !senderInstitution ||
            !receiverInstitution ||
            !projectTitle.trim() ||
            !purpose.trim()
        ) {

            alert("Please fill all fields.");
            return;

        }

        if (senderInstitution === receiverInstitution) {

            alert("Sender and Receiver institutions cannot be the same.");
            return;

        }

        const payload = {

            sender_institution_id: Number(senderInstitution),
            receiver_institution_id: Number(receiverInstitution),
            project_title: projectTitle,
            purpose: purpose

        };

        console.log("Sending Payload:", payload);

        try {

            const res = await api.post(
                "/institution-collaboration-requests/",
                payload
            );

            console.log("Backend Response:", res.data);

            alert("✅ Collaboration Request Sent Successfully");

            setSenderInstitution("");
            setReceiverInstitution("");
            setProjectTitle("");
            setPurpose("");

        } catch (err) {

            console.error(err);

            if (err.response) {

                console.log(err.response.data);

                alert(
                    JSON.stringify(
                        err.response.data,
                        null,
                        2
                    )
                );

            }
            else {

                alert("Network Error");

            }

        }

    };

    return (

        <div className="container-fluid">

            <PageHeader
                title="Institution Collaboration"
                icon="bi-buildings-fill"
            />

            <CustomCard>

                <h5 className="mb-3">

                    Create Collaboration Request

                </h5>

                <div className="row">

                    <div className="col-md-6">

                        <label className="fw-bold">
                            Sender Institution
                        </label>

                        <select
                            className="form-select"
                            value={senderInstitution}
                            onChange={(e) =>
                                setSenderInstitution(e.target.value)
                            }
                        >

                            <option value="">
                                Select Institution
                            </option>

                            {institutions.map((inst) => (

                                <option
                                    key={inst.id}
                                    value={inst.id}
                                >
                                    {inst.institution_name}
                                </option>

                            ))}

                        </select>

                    </div>

                    <div className="col-md-6">

                        <label className="fw-bold">
                            Receiver Institution
                        </label>

                        <select
                            className="form-select"
                            value={receiverInstitution}
                            onChange={(e) =>
                                setReceiverInstitution(e.target.value)
                            }
                        >

                            <option value="">
                                Select Institution
                            </option>

                            {institutions.map((inst) => (

                                <option
                                    key={inst.id}
                                    value={inst.id}
                                >
                                    {inst.institution_name}
                                </option>

                            ))}

                        </select>

                    </div>

                </div>

                <div className="mt-3">

                    <label className="fw-bold">

                        Project Title

                    </label>

                    <input
                        type="text"
                        className="form-control"
                        value={projectTitle}
                        onChange={(e) =>
                            setProjectTitle(e.target.value)
                        }
                    />

                </div>

                <div className="mt-3">

                    <label className="fw-bold">

                        Purpose

                    </label>

                    <textarea
                        rows="4"
                        className="form-control"
                        value={purpose}
                        onChange={(e) =>
                            setPurpose(e.target.value)
                        }
                    />

                </div>

                <button
                    className="btn btn-primary mt-3"
                    onClick={sendRequest}
                >

                    <i className="bi bi-send me-2"></i>

                    Send Request

                </button>

            </CustomCard>

        </div>

    );

}

export default InstitutionCollaboration;