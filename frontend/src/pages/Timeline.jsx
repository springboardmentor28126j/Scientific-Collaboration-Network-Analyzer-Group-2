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
                                    className="bg-primary rounded-circle"
                                    style={{
                                        width:18,
                                        height:18,
                                        marginTop:8,
                                        marginRight:20
                                    }}
                                ></div>

                                <div className="w-100">

                                    <div className="d-flex justify-content-between">

                                        <h4 className="fw-bold">

                                            {event.event_title}

                                        </h4>

                                        <span className="badge bg-success">

                                            {event.event_type}

                                        </span>

                                    </div>

                                    <p className="mt-3 text-muted">

                                        {event.description}

                                    </p>

                                    <hr />

                                    <div className="d-flex justify-content-between">

                                        <small>

                                            <i className="bi bi-folder2-open me-2"></i>

                                            Project #{event.project_id}

                                        </small>

                                        <small>

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