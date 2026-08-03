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
                                    style={{ fontSize: "60px" }}
                                ></i>

                            </div>

                            <h5 className="text-center mt-3">

                                {file.file_name}

                            </h5>

                            <div className="text-center">

                                <span className="badge bg-primary">

                                    {file.file_type}

                                </span>

                            </div>

                            <hr />

                            <p>

                                <strong>Description</strong>

                                <br />

                                {file.description}

                            </p>

                            <p>

                                <strong>Project :</strong>

                                {" "}

                                {file.project_id}

                            </p>

                            <p>

                                <strong>Uploaded By :</strong>

                                {" "}

                                {file.uploaded_by}

                            </p>

                            <a
                                href={file.file_url}
                                target="_blank"
                                rel="noreferrer"
                                className="btn btn-success rounded-pill w-100"
                            >

                                <i className="bi bi-download me-2"></i>

                                Download

                            </a>

                        </CustomCard>

                    </div>

                ))}

            </div>

        </div>

    );

}

export default SharedFiles;