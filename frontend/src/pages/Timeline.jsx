import { useEffect, useState } from "react";
import api from "../services/api";
import PageHeader from "../components/PageHeader";
import CustomCard from "../components/CustomCard";

function Timeline() {

    const [events, setEvents] = useState([]);

    useEffect(() => {
        loadTimeline();
    }, []);

    const loadTimeline = async () => {

        try {

            const res = await api.get("/project-timelines/");
            setEvents(res.data);

        } catch (err) {

            console.log(err);

        }

    };

    return (

        <div className="container-fluid">

            <PageHeader
                title="Project Timeline"
                icon="bi-calendar-event"
                buttonText="Add Event"
                buttonIcon="bi-plus-circle"
            />

            <div className="row">

                {events.map((event) => (

                    <div
                        className="col-lg-6 mb-4"
                        key={event.id}
                    >

                        <CustomCard>

                            <div className="d-flex">

                                <div
                                    className="bg-primary rounded-circle d-flex justify-content-center align-items-center"
                                    style={{
                                        width: 55,
                                        height: 55,
                                        minWidth: 55,
                                        marginRight: 20
                                    }}
                                >

                                    <i
                                        className="bi bi-calendar-event text-white"
                                        style={{ fontSize: "22px" }}
                                    ></i>

                                </div>

                                <div className="w-100">

                                    <div className="d-flex justify-content-between align-items-center">

                                        <h5 className="fw-bold mb-0">

                                            {event.event_title}

                                        </h5>

                                        <span className="badge bg-success px-3 py-2">

                                            {event.event_type}

                                        </span>

                                    </div>

                                    <hr />

                                    <p
                                        className="text-muted"
                                        style={{
                                            lineHeight: "28px",
                                            fontSize: "16px"
                                        }}
                                    >

                                        {event.description}

                                    </p>

                                    <hr />

                                    <div className="d-flex justify-content-between">

                                        <small className="text-secondary">

                                            <i className="bi bi-folder2-open me-2"></i>

                                            Project #{event.project_id}

                                        </small>

                                        <small className="text-secondary">

                                            <i className="bi bi-calendar3 me-2"></i>

                                            {event.event_date}

                                        </small>

                                    </div>

                                </div>

                            </div>

                        </CustomCard>

                    </div>

                ))}

            </div>

        </div>

    );

}

export default Timeline;