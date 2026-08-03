import { useEffect, useState } from "react";
import api from "../services/api";
import PageHeader from "../components/PageHeader";
import CustomCard from "../components/CustomCard";

function Projects() {

    const [projects, setProjects] = useState([]);

    useEffect(() => {
        loadProjects();
    }, []);

    const loadProjects = async () => {

        try {

            const res = await api.get("/projects");

            setProjects(res.data);

        } catch (err) {

            console.log(err);

        }

    };

    return (

        <div className="container-fluid">

            <PageHeader
                title="Projects"
                icon="bi-folder2-open"
                buttonText="Create Project"
                buttonIcon="bi-plus-circle"
            />

            <div className="row">

                {projects.map((project) => (

                    <div
                        className="col-lg-4 col-md-6 mb-4"
                        key={project.id}
                    >

                        <CustomCard>

                            <h4 className="fw-bold">

                                {project.title}

                            </h4>

                            <p className="text-muted">

                                {project.description}

                            </p>

                            <hr />

                            <p>

                                <strong>Status :</strong>

                                <span className="badge bg-success ms-2">

                                    {project.status}

                                </span>

                            </p>

                            <p>

                                <strong>Lead :</strong>

                                {" "}

                                {project.project_lead_id}

                            </p>

                            <p>

                                <strong>Institution :</strong>

                                {" "}

                                {project.institution_id}

                            </p>

                            <p>

                                <strong>Duration</strong>

                                <br />

                                {project.start_date}

                                <br />

                                <strong>to</strong>

                                <br />

                                {project.end_date}

                            </p>

                        </CustomCard>

                    </div>

                ))}

            </div>

        </div>

    );

}

export default Projects;