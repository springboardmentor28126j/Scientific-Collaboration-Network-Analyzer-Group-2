import { useEffect, useState } from "react";
import api from "../services/api";
import PageHeader from "../components/PageHeader";
import CustomCard from "../components/CustomCard";

function Notifications() {

    const [notifications, setNotifications] = useState([]);

    useEffect(() => {
        loadNotifications();
    }, []);

    const loadNotifications = async () => {

        try {

            const res = await api.get("/notifications/");

            setNotifications(res.data);

        } catch (err) {

            console.log(err);

        }

    };

    return (

        <div className="container-fluid">

            <PageHeader
                title="Notifications"
                icon="bi-bell-fill"
                buttonText="Refresh"
                buttonIcon="bi-arrow-clockwise"
            />

            <div className="row">

                {notifications.map((notification) => (

                    <div
                        className="col-lg-6 mb-4"
                        key={notification.id}
                    >

                        <CustomCard>

                            <div className="d-flex justify-content-between align-items-center">

                                <h5 className="fw-bold mb-0">

                                    {notification.title}

                                </h5>

                                {

                                    notification.is_read ?

                                    <span className="badge bg-success">

                                        Read

                                    </span>

                                    :

                                    <span className="badge bg-danger">

                                        Unread

                                    </span>

                                }

                            </div>

                            <hr />

                            <p>

                                {notification.message}

                            </p>

                            <div className="d-flex justify-content-between">

                                <small className="text-muted">

                                    <i className="bi bi-person me-1"></i>

                                    Researcher #{notification.researcher_id}

                                </small>

                                <small className="text-muted">

                                    {new Date(notification.created_at).toLocaleString()}

                                </small>

                            </div>

                        </CustomCard>

                    </div>

                ))}

            </div>

        </div>

    );

}

export default Notifications;