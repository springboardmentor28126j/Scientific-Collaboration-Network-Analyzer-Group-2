import { useEffect, useState } from "react";
import api from "../services/api";

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
                    status: status
                }
            );

            loadRequests();

        } catch (err) {
            console.log(err);
        }
    };

    return (

        <div className="container mt-4">

            <h2>Institution Collaboration Requests</h2>

            <table className="table table-bordered mt-3">

                <thead>

                    <tr>

                        <th>ID</th>
                        <th>Sender Institution</th>
                        <th>Receiver Institution</th>
                        <th>Project</th>
                        <th>Purpose</th>
                        <th>Status</th>
                        <th>Actions</th>

                    </tr>

                </thead>

                <tbody>

                    {requests.map((request) => (

                        <tr key={request.id}>

                            <td>{request.id}</td>

                            <td>{request.sender_institution_id}</td>

                            <td>{request.receiver_institution_id}</td>

                            <td>{request.project_title}</td>

                            <td>{request.purpose}</td>

                            <td>

                                {request.status === "Pending" && (
                                    <span className="badge bg-warning text-dark">
                                        Pending
                                    </span>
                                )}

                                {request.status === "Accepted" && (
                                    <span className="badge bg-success">
                                        Accepted
                                    </span>
                                )}

                                {request.status === "Rejected" && (
                                    <span className="badge bg-danger">
                                        Rejected
                                    </span>
                                )}

                            </td>

                            <td>

                                {request.status === "Pending" ? (

                                    <>

                                        <button
                                            className="btn btn-success btn-sm me-2"
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
                                            className="btn btn-danger btn-sm"
                                            onClick={() =>
                                                updateStatus(
                                                    request.id,
                                                    "Rejected"
                                                )
                                            }
                                        >
                                            Reject
                                        </button>

                                    </>

                                ) : (

                                    <span>-</span>

                                )}

                            </td>

                        </tr>

                    ))}

                </tbody>

            </table>

        </div>

    );

}

export default InstitutionRequests;