import { useEffect, useState } from "react";
import api from "../services/api";
import PageHeader from "../components/PageHeader";
import CustomCard from "../components/CustomCard";

function ProgressUpdates() {

    const [updates, setUpdates] = useState([]);

    useEffect(() => {
        loadUpdates();
    }, []);

    const loadUpdates = async () => {

        try {

            const res = await api.get("/project-comments/");
            setUpdates(res.data);

        } catch (err) {

            console.log(err);

        }

    };

    return (

        <div className="container-fluid">

            <PageHeader
                title="Progress Updates"
                icon="bi-journal-check"
                buttonText="Add Update"
                buttonIcon="bi-plus-circle"
            />

            <div className="row">

                {updates.map((update) => (

                    <div
                        className="col-lg-6 mb-4"
                        key={update.id}
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

                                        <i className="bi bi-person-fill"></i>

                                    </div>

                                    <div className="ms-3">

                                        <h5 className="fw-bold mb-1">

                                            Researcher #{update.researcher_id}

                                        </h5>

                                        <span className="badge bg-info">

                                            Project #{update.project_id}

                                        </span>

                                    </div>

                                </div>

                                <span className="badge bg-success">

                                    Updated

                                </span>

                            </div>

                            <hr />

                            <p
                                style={{
                                    lineHeight: "28px",
                                    fontSize: "16px"
                                }}
                            >

                                {update.comment}

                            </p>

                            <hr />

                            <div className="d-flex justify-content-between">

                                <small className="text-muted">

                                    <i className="bi bi-calendar-event me-2"></i>

                                    {new Date(update.created_at).toLocaleDateString()}

                                </small>

                                <small className="text-muted">

                                    <i className="bi bi-clock me-2"></i>

                                    {new Date(update.created_at).toLocaleTimeString()}

                                </small>

                            </div>

                        </CustomCard>

                    </div>

                ))}

            </div>

        </div>

    );

}

export default ProgressUpdates;