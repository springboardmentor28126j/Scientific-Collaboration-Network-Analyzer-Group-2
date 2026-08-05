import { useEffect, useState } from "react";
import api from "../services/api";
import PageHeader from "../components/PageHeader";
import CustomCard from "../components/CustomCard";

function SharedFiles() {

    const [files, setFiles] = useState([]);

    useEffect(() => {
        loadFiles();
    }, []);

    const loadFiles = async () => {

        try {

            const res = await api.get("/project-documents/");
            setFiles(res.data);

        } catch (err) {

            console.log(err);

        }

    };

    return (

        <div className="container-fluid">

            <PageHeader
                title="Shared Files"
                icon="bi-folder2-open"
                buttonText="Upload File"
                buttonIcon="bi-upload"
            />

            <div className="row">

                {files.map((file) => (

                    <div
                        className="col-lg-4 col-md-6 mb-4"
                        key={file.id}
                    >

                        <CustomCard>

                            <div className="text-center">

                                <i
                                    className="bi bi-file-earmark-pdf-fill text-danger"
                                    style={{ fontSize: "70px" }}
                                ></i>

                                <h5 className="mt-3 fw-bold">

                                    {file.file_name}

                                </h5>

                                <span className="badge bg-primary rounded-pill px-3 py-2">

                                    {file.file_type}

                                </span>

                            </div>

                            <hr />

                            <div className="mb-2">

                                <small className="text-muted">
                                    Description
                                </small>

                                <p className="mb-2">
                                    {file.description}
                                </p>

                            </div>

                            <div className="d-flex justify-content-between">

                                <span className="text-secondary">

                                    <i className="bi bi-folder me-1"></i>

                                    Project #{file.project_id}

                                </span>

                            </div>

                            <div className="mt-2 mb-3">

                                <span className="text-secondary">

                                    <i className="bi bi-person-circle me-1"></i>

                                    Researcher #{file.uploaded_by}

                                </span>

                            </div>

                            <a
                                href={file.file_url}
                                target="_blank"
                                rel="noreferrer"
                                className="btn btn-success rounded-pill w-100"
                            >

                                <i className="bi bi-download me-2"></i>

                                Download File

                            </a>

                        </CustomCard>

                    </div>

                ))}

            </div>

        </div>

    );

}

export default SharedFiles;