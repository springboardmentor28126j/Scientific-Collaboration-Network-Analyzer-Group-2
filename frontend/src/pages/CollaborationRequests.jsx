import { useEffect, useState } from "react";
import api from "../services/api";
import PageHeader from "../components/PageHeader";
import CustomCard from "../components/CustomCard";
import Pagination from "../components/Pagination";

function CollaborationRequests() {

    const [requests, setRequests] = useState([]);

    const [currentPage, setCurrentPage] = useState(1);

    const requestsPerPage = 4;

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

    const indexOfLast =
        currentPage * requestsPerPage;

    const indexOfFirst =
        indexOfLast - requestsPerPage;

    const currentRequests =
        requests.slice(indexOfFirst, indexOfLast);

    const totalPages =
        Math.ceil(requests.length / requestsPerPage);

    return (

        <div className="container-fluid">

            <PageHeader
                title="Collaboration Requests"
                icon="bi-people-fill"
                buttonText="New Request"
                buttonIcon="bi-person-plus"
            />

            <div className="row">

                {currentRequests.map((request) => (

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
                                        <i className="bi bi-people-fill"></i>
                                    </div>

                                    <div className="ms-3">

                                        <h5 className="fw-bold mb-1">
                                            Research Collaboration
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
                                    <i className="bi bi-person-fill me-2"></i>
                                    Sender :
                                </strong>{" "}
                                {request.sender_name}
                            </p>

                            <p>
                                <strong>
                                    <i className="bi bi-person-check-fill me-2"></i>
                                    Receiver :
                                </strong>{" "}
                                {request.receiver_name}
                            </p>

                            <p>
                                <strong>
                                    <i className="bi bi-file-earmark-text me-2"></i>
                                    Paper :
                                </strong>{" "}
                                {request.paper_title}
                            </p>

                            <div className="alert alert-light border">
                                {request.message}
                            </div>

                            {request.status === "Pending" && (

                                <div className="d-flex justify-content-end mt-3">

                                    <button
                                        className="btn btn-success rounded-pill me-2"
                                        onClick={() =>
                                            updateStatus(request.id, "Accepted")
                                        }
                                    >
                                        <i className="bi bi-check-circle me-2"></i>
                                        Accept
                                    </button>

                                    <button
                                        className="btn btn-danger rounded-pill"
                                        onClick={() =>
                                            updateStatus(request.id, "Rejected")
                                        }
                                    >
                                        <i className="bi bi-x-circle me-2"></i>
                                        Reject
                                    </button>

                                </div>

                            )}

                        </CustomCard>

                    </div>

                ))}

            </div>

            <Pagination
                currentPage={currentPage}
                totalPages={totalPages}
                onPageChange={setCurrentPage}
            />

        </div>

    );

}

export default CollaborationRequests;