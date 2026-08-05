import { useEffect, useState } from "react";
import axios from "axios";

import Layout from "../components/Layout";
import CollaborationStats from "../components/CollaborationStats";
import CollaborationTable from "../components/CollaborationTable";

function Collaborations() {

    const [collaborations, setCollaborations] = useState([]);
    const [researchers, setResearchers] = useState([]);
    const [papers, setPapers] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {

        try {

            const [
                collaborationsRes,
                researchersRes,
                papersRes
            ] = await Promise.all([

                axios.get("http://127.0.0.1:8000/collaborations/"),

                axios.get("http://127.0.0.1:8000/researchers/"),

                axios.get("http://127.0.0.1:8000/research-papers/")

            ]);

            setCollaborations(collaborationsRes.data);
            setResearchers(researchersRes.data);
            setPapers(papersRes.data);

        } catch (err) {

            console.error(err);

        } finally {

            setLoading(false);

        }

    };

    return (

        <Layout>

            <h2
                style={{
                    marginBottom: "25px",
                    fontWeight: "bold"
                }}
            >
                Collaboration Dashboard
            </h2>

            <CollaborationStats
                collaborations={collaborations}
            />

            <CollaborationTable
                collaborations={collaborations}
                researchers={researchers}
                papers={papers}
                loading={loading}
            />

        </Layout>

    );

}

export default Collaborations;
const fetchCollaborations = async () => {
    try {
        console.log("Fetching collaborations...");

        const res = await axios.get(
            "http://127.0.0.1:8000/collaborations/"
        );

        console.log("Response:", res.data);

        setCollaborations(res.data);

    } catch (err) {
        console.error("Error:", err);
    } finally {
        setLoading(false);
    }
};