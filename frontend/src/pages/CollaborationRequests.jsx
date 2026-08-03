import { useEffect, useState } from "react";
import api from "../services/api";

function CollaborationRequests() {

    const [requests, setRequests] = useState([]);

    useEffect(() => {
        loadRequests();
    }, []);

    const loadRequests = async () => {

        try {

            const res = await api.get("/collaboration-requests/");

            setRequests(res.data);

        } catch (err) {

            console.log(err);

        }

    };

    const updateStatus = async (id, status) => {

        try {

            await api.put(`/collaboration-requests/${id}`, {
                status
            });

            loadRequests();

        } catch (err) {

            console.log(err);

        }

    };

    return (

        <div className="container-fluid">

            <div className="d-flex justify-content-between align-items-center mb-4">

                <h2 className="fw-bold">

                    <i className="bi bi-people-fill text-primary me-2"></i>

                    Collaboration Requests

                </h2>

                <button className="btn btn-primary rounded-pill">

                    <i className="bi bi-person-plus me-2"></i>

                    New Request

                </button>

            </div>

            <div className="row">

                {requests.map(request => (

                    <div
                        className="col-lg-6 mb-4"
                        key={request.id}
                    >

                        <div className="card border-0 shadow rounded-4">

                            <div className="card-body">

                                <h5>

                                    Research Collaboration

                                </h5>

                                <hr/>

                                <p>

                                    <strong>Sender :</strong>

                                    {request.sender_id}

                                </p>

                                <p>

                                    <strong>Receiver :</strong>

                                    {request.receiver_id}

                                </p>

                                <p>

                                    {request.message}

                                </p>

                                <span
                                    className={
                                        request.status==="Accepted"
                                        ? "badge bg-success"
                                        : request.status==="Rejected"
                                        ? "badge bg-danger"
                                        : "badge bg-warning text-dark"
                                    }
                                >
                                    {request.status}
                                </span>

                                <div className="mt-4">

                                    <button
                                        className="btn btn-success me-2"
                                        onClick={() =>
                                            updateStatus(
                                                request.id,
                                                "Accepted"
                                            )
                                        }
                                    >
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
                                        Reject
                                    </button>

                                </div>

                            </div>

                        </div>

                    </div>

                ))}

            </div>

        </div>

    );

}

export default CollaborationRequests;