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

                            <div className="d-flex align-items-center mb-3">

                                <div
                                    className="bg-primary text-white rounded-circle d-flex justify-content-center align-items-center"
                                    style={{
                                        width: 55,
                                        height: 55,
                                        fontSize: "22px"
                                    }}
                                >

                                    <i className="bi bi-person-fill"></i>

                                </div>

                                <div className="ms-3">

                                    <h5 className="mb-0">

                                        Researcher #{update.researcher_id}

                                    </h5>

                                    <small className="text-muted">

                                        Project #{update.project_id}

                                    </small>

                                </div>

                            </div>

                            <p className="mt-3">

                                {update.comment}

                            </p>

                            <hr />

                            <small className="text-muted">

                                <i className="bi bi-clock me-2"></i>

                                {new Date(update.created_at).toLocaleString()}

                            </small>

                        </CustomCard>

                    </div>

                ))}

            </div>

        </div>

    );

}

export default ProgressUpdates;