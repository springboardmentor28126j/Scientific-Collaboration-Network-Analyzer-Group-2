import { useEffect, useState } from "react";
import api from "../services/api";

function CollaborationRequestModal({ onClose }) {

    const [researchers, setResearchers] = useState([]);
    const [papers, setPapers] = useState([]);

    const [receiver, setReceiver] = useState("");
    const [paper, setPaper] = useState("");
    const [message, setMessage] = useState("");

    useEffect(() => {

        loadResearchers();
        loadPapers();

    }, []);

    const loadResearchers = async () => {

        try {

            const res = await api.get("/researchers/");
            setResearchers(res.data);

        } catch (err) {

            console.log(err);

        }

    };

    const loadPapers = async () => {

        try {

            const res = await api.get("/papers/");
            setPapers(res.data);

        } catch (err) {

            console.log(err);

        }

    };

    const sendRequest = async () => {

        if (!receiver) {

            alert("Please select a researcher");
            return;

        }

        if (!paper) {

            alert("Please select a paper");
            return;

        }

        try {

            await api.post("/collaboration-requests/", {

                sender_id: 2,
                receiver_id: Number(receiver),
                paper_id: Number(paper),
                message: message

            });

            alert("Collaboration Request Sent Successfully!");

            onClose();

        } catch (err) {

            console.log(err);

            alert("Unable to send request");

        }

    };

    return (

        <div className="modal d-block">

            <div className="modal-dialog modal-lg">

                <div className="modal-content">

                    <div className="modal-header">

                        <h5 className="fw-bold">

                            Send Collaboration Request

                        </h5>

                        <button
                            className="btn-close"
                            onClick={onClose}
                        ></button>

                    </div>

                    <div className="modal-body">

                        <label className="fw-bold">

                            Select Researcher

                        </label>

                        <select
                            className="form-select mb-3"
                            value={receiver}
                            onChange={(e) => setReceiver(e.target.value)}
                        >

                            <option value="">

                                Choose Researcher

                            </option>

                            {

                                researchers.map((r) => (

                                    <option
                                        key={r.id}
                                        value={r.id}
                                    >

                                        {r.full_name}

                                    </option>

                                ))

                            }

                        </select>

                        <label className="fw-bold">

                            Select Paper

                        </label>

                        <select
                            className="form-select mb-3"
                            value={paper}
                            onChange={(e) => setPaper(e.target.value)}
                        >

                            <option value="">

                                Choose Paper

                            </option>

                            {

                                papers.map((p) => (

                                    <option
                                        key={p.id}
                                        value={p.id}
                                    >

                                        {p.title}

                                    </option>

                                ))

                            }

                        </select>

                        <label className="fw-bold">

                            Message

                        </label>

                        <textarea
                            className="form-control"
                            rows="4"
                            value={message}
                            onChange={(e) => setMessage(e.target.value)}
                            placeholder="Type your collaboration request..."
                        />

                    </div>

                    <div className="modal-footer">

                        <button
                            className="btn btn-secondary"
                            onClick={onClose}
                        >

                            Cancel

                        </button>

                        <button
                            className="btn btn-primary"
                            onClick={sendRequest}
                        >

                            Send Request

                        </button>

                    </div>

                </div>

            </div>

        </div>

    );

}

export default CollaborationRequestModal;