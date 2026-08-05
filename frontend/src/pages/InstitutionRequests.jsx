import { useEffect, useState } from "react";
import api from "../services/api";
import PageHeader from "../components/PageHeader";
import CustomCard from "../components/CustomCard";

function InstitutionRequests() {

    const [requests, setRequests] = useState([]);
    const [institutionName, setInstitutionName] = useState("");

    useEffect(() => {
        loadCurrentInstitution();
    }, []);

    const loadCurrentInstitution = async () => {

        try {

            const token = localStorage.getItem("token");

            const res = await api.get(
                "/auth/me",
                {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                }
            );

            console.log("Current User:", res.data);

            setInstitutionName(res.data.institution);

            loadRequests(res.data.institution);

        } catch (err) {

            console.log(err);

        }

    };

    const loadRequests = async (institution) => {

        try {

            const res = await api.get(
                "/institution-collaboration-requests/"
            );

            console.log("All Requests:", res.data);

            const filtered = res.data.filter(

                (req) =>
                    req.receiver_institution_name === institution

            );

            console.log("Filtered Requests:", filtered);

            setRequests(filtered);

        } catch (err) {

            console.log(err);

        }

    };

    const updateStatus = async (id, status) => {

        try {

            await api.put(

                `/institution-collaboration-requests/${id}`,

                {
                    status
                }

            );

            loadCurrentInstitution();

        } catch (err) {

            console.log(err);

        }

    };

    return (

        <div className="container-fluid">

            <PageHeader
                title="Institution Collaboration Requests"
                icon="bi-building"
            />

            <h5 className="mb-4 text-primary">

                Logged Institution :
                {" "}
                {institutionName}

            </h5>

            <div className="row">

                {requests.length === 0 ? (

                    <div className="col-12">

                        <CustomCard>

                            <div className="text-center">

                                <h4 className="text-muted">

                                    No Collaboration Requests

                                </h4>

                            </div>

                        </CustomCard>

                    </div>

                ) : (

                    requests.map((request) => (

                        <div
                            className="col-lg-6 mb-4"
                            key={request.id}
                        >

                            <CustomCard>

                                <div className="d-flex justify-content-between align-items-center">

                                    <div>

                                        <h5 className="fw-bold">

                                            {request.project_title}

                                        </h5>

                                        <small>

                                            Request #{request.id}

                                        </small>

                                    </div>

                                    <span

                                        className={
                                            request.status === "Accepted"

                                                ? "badge bg-success"

                                                : request.status === "Rejected"

                                                ? "badge bg-danger"

                                                : "badge bg-warning text-dark"
                                        }

                                    >

                                        {request.status}

                                    </span>

                                </div>

                                <hr />

                                <p>

                                    <strong>

                                        Sender Institution :

                                    </strong>

                                    {" "}

                                    {request.sender_institution_name}

                                </p>

                                <p>

                                    <strong>

                                        Receiver Institution :

                                    </strong>

                                    {" "}

                                    {request.receiver_institution_name}

                                </p>

                                <p>

                                    <strong>

                                        Project :

                                    </strong>

                                    {" "}

                                    {request.project_title}

                                </p>

                                <div className="alert alert-light border">

                                    <strong>

                                        Purpose

                                    </strong>

                                    <hr />

                                    {request.purpose}

                                </div>

                                {request.status === "Pending" ? (

                                    <div className="text-end">

                                        <button

                                            className="btn btn-success me-2"

                                            onClick={() =>
                                                updateStatus(
                                                    request.id,
                                                    "Accepted"
                                                )
                                            }

                                        >

                                            <i className="bi bi-check-circle me-2"></i>

                                            Accept

                                        </button>

                                        <button

                                            className="btn btn-danger"

                                            onClick={() =>
                                                updateStatus(
                                                    request.id,
                                                    "Rejected"
                                                )
                                            }

                                        >

                                            <i className="bi bi-x-circle me-2"></i>

                                            Reject

                                        </button>

                                    </div>

                                ) : (

                                    <div className="text-end">

                                        <button
                                            className="btn btn-secondary"
                                            disabled
                                        >

                                            Completed

                                        </button>

                                    </div>

                                )}

                            </CustomCard>

                        </div>

                    ))

                )}

            </div>

        </div>

    );

}

export default InstitutionRequests;