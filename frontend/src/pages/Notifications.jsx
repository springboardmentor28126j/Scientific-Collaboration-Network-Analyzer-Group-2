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

                                <div className="d-flex align-items-center">

                                    <div
                                        className="bg-warning rounded-circle d-flex justify-content-center align-items-center"
                                        style={{
                                            width: 60,
                                            height: 60,
                                            fontSize: "25px",
                                            color: "white"
                                        }}
                                    >

                                        <i className="bi bi-bell-fill"></i>

                                    </div>

                                    <div className="ms-3">

                                        <h5 className="fw-bold mb-1">

                                            {notification.title}

                                        </h5>

                                        <small className="text-muted">

                                            Researcher #{notification.researcher_id}

                                        </small>

                                    </div>

                                </div>

                                {

                                    notification.is_read ?

                                        <span className="badge bg-success px-3 py-2">

                                            <i className="bi bi-check-circle me-1"></i>

                                            Read

                                        </span>

                                        :

                                        <span className="badge bg-danger px-3 py-2">

                                            <i className="bi bi-exclamation-circle me-1"></i>

                                            Unread

                                        </span>

                                }

                            </div>

                            <hr />

                            <p
                                style={{
                                    fontSize: "16px",
                                    lineHeight: "28px"
                                }}
                            >

                                {notification.message}

                            </p>

                            <hr />

                            <div className="d-flex justify-content-between">

                                <small className="text-muted">

                                    <i className="bi bi-calendar-event me-2"></i>

                                    {new Date(notification.created_at).toLocaleDateString()}

                                </small>

                                <small className="text-muted">

                                    <i className="bi bi-clock me-2"></i>

                                    {new Date(notification.created_at).toLocaleTimeString()}

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