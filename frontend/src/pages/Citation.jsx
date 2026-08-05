import { useEffect, useState } from "react";
import api from "../services/api";
import PageHeader from "../components/PageHeader";
import CustomCard from "../components/CustomCard";

function Citation() {

    const [citations, setCitations] = useState([]);
    const [papers, setPapers] = useState([]);

    const [paperId, setPaperId] = useState("");
    const [citedPaperId, setCitedPaperId] = useState("");
    const [citationYear, setCitationYear] = useState(new Date().getFullYear());

    useEffect(() => {

        loadCitations();
        loadPapers();

    }, []);

    const loadCitations = async () => {

        try {

            const res = await api.get("/citations/");
            setCitations(res.data);

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

    const createCitation = async () => {

        if (!paperId || !citedPaperId) {

            alert("Select both papers");
            return;

        }

        try {

            await api.post("/citations/", {

                paper_id: Number(paperId),
                cited_paper_id: Number(citedPaperId),
                citation_year: Number(citationYear),
                citation_count: 1

            });

            alert("✅ Citation Added Successfully");

            setPaperId("");
            setCitedPaperId("");

            loadCitations();

        } catch (err) {

            console.log(err);

            alert("Unable to create citation");

        }

    };

    const deleteCitation = async (id) => {

        if (!window.confirm("Delete Citation?"))
            return;

        try {

            await api.delete(`/citations/${id}`);

            loadCitations();

        } catch (err) {

            console.log(err);

        }

    };

    return (

        <div className="container-fluid">

            <PageHeader
                title="Citation Management"
                icon="bi-journal-bookmark-fill"
            />

            <CustomCard>

                <h5 className="mb-3">
                    Add Citation
                </h5>

                <div className="row">

                    <div className="col-md-5">

                        <label className="fw-bold">
                            Paper
                        </label>

                        <select
                            className="form-select"
                            value={paperId}
                            onChange={(e) =>
                                setPaperId(e.target.value)
                            }
                        >

                            <option value="">
                                Select Paper
                            </option>

                            {

                                papers.map((paper) => (

                                    <option
                                        key={paper.id}
                                        value={paper.id}
                                    >
                                        {paper.title}
                                    </option>

                                ))

                            }

                        </select>

                    </div>

                    <div className="col-md-5">

                        <label className="fw-bold">
                            Cited Paper
                        </label>

                        <select
                            className="form-select"
                            value={citedPaperId}
                            onChange={(e) =>
                                setCitedPaperId(e.target.value)
                            }
                        >

                            <option value="">
                                Select Cited Paper
                            </option>

                            {

                                papers.map((paper) => (

                                    <option
                                        key={paper.id}
                                        value={paper.id}
                                    >
                                        {paper.title}
                                    </option>

                                ))

                            }

                        </select>

                    </div>

                    <div className="col-md-2">

                        <label className="fw-bold">
                            Year
                        </label>

                        <input
                            type="number"
                            className="form-control"
                            value={citationYear}
                            onChange={(e) =>
                                setCitationYear(e.target.value)
                            }
                        />

                    </div>

                </div>

                <button
                    className="btn btn-primary mt-3"
                    onClick={createCitation}
                >
                    Add Citation
                </button>

            </CustomCard>

            <div className="row mt-4">

                {

                    citations.map((citation) => (

                        <div
                            className="col-lg-6 mb-3"
                            key={citation.id}
                        >

                            <CustomCard>

                                <h5>

                                    Citation #{citation.id}

                                </h5>

                                <hr />
<p>

    <strong>

        <i className="bi bi-file-earmark-text me-2"></i>

        Paper

    </strong>

    <br />

    {citation.paper_title}

</p>

<p>

    <strong>

        <i className="bi bi-journal-text me-2"></i>

        Cited Paper

    </strong>

    <br />

    {citation.cited_paper_title}

</p>

                                <p>

    <strong>

        <i className="bi bi-calendar-event me-2"></i>

        Citation Year

    </strong>

    <br />

    {citation.citation_year}

</p>

                                <p>

    <strong>

        <i className="bi bi-graph-up-arrow me-2"></i>

        Citation Count

    </strong>

    <br />

    {citation.citation_count}

</p>

                                <button
                                    className="btn btn-danger"
                                    onClick={() =>
                                        deleteCitation(
                                            citation.id
                                        )
                                    }
                                >

                                    Delete

                                </button>

                            </CustomCard>

                        </div>

                    ))

                }

            </div>

        </div>

    );

}

export default Citation;