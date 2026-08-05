import { useEffect, useState } from "react";
import api from "../services/api";
import PageHeader from "../components/PageHeader";
import CustomCard from "../components/CustomCard";

function InstitutionRequests() {

    const [requests, setRequests] = useState([]);

    useEffect(() => {
        loadRequests();
    }, []);

    const loadRequests = async () => {
        try {

            const res = await api.get("/institution-collaboration-requests/");
            setRequests(res.data);

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

            loadRequests();

        } catch (err) {

            console.log(err);

        }

    };

    return (

        <div className="container-fluid">

            <PageHeader
                title="Institution Collaboration Requests"
                icon="bi-building"
                buttonText="New Request"
                buttonIcon="bi-building-add"
            />

            <div className="row">

                {requests.map((request) => (

                    <div
                        className="col-lg-6 mb-4"
                        key={request.id}
                    >

                        <CustomCard>

                            <div className="d-flex justify-content-between align-items-center">

                                <div className="d-flex align-items-center">

                                    <div
                                        className="bg-primary text-white rounded-circle d-flex justify-content-center align-items-center"
                                        style={{
                                            width: 60,
                                            height: 60,
                                            fontSize: "24px"
                                        }}
                                    >

                                        <i className="bi bi-building"></i>

                                    </div>

                                    <div className="ms-3">

                                        <h5 className="fw-bold mb-1">

                                            {request.project_title}

                                        </h5>

                                        <small className="text-muted">

                                            Request #{request.id}

                                        </small>

                                    </div>

                                </div>

                                <span
                                    className={
                                        request.status === "Accepted"
                                            ? "badge bg-success px-3 py-2"
                                            : request.status === "Rejected"
                                            ? "badge bg-danger px-3 py-2"
                                            : "badge bg-warning text-dark px-3 py-2"
                                    }
                                >
                                    {request.status}
                                </span>

                            </div>

                            <hr />

                            <p>

                                <strong>
                                    <i className="bi bi-send me-2"></i>

                                    Sender Institution :
                                </strong>

                                {" "}#{request.sender_institution_id}

                            </p>

                            <p>

                                <strong>
                                    <i className="bi bi-reception-4 me-2"></i>

                                    Receiver Institution :
                                </strong>

                                {" "}#{request.receiver_institution_id}

                            </p>

                            <div className="alert alert-light border">

                                <strong>Purpose</strong>

                                <br />

                                {request.purpose}

                            </div>

                            <div className="d-flex justify-content-end mt-3">

                                {

                                    request.status === "Pending" ? (

                                        <>

                                            <button
                                                className="btn btn-success rounded-pill me-2"
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
                                                className="btn btn-danger rounded-pill"
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

                                        </>

                                    ) : (

                                        <button
                                            className="btn btn-secondary rounded-pill"
                                            disabled
                                        >

                                            Completed

                                        </button>

                                    )

                                }

                            </div>

                        </CustomCard>

                    </div>

                ))}

            </div>

        </div>

    );

}

export default InstitutionRequests;