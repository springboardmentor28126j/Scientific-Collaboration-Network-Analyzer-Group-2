import { useEffect, useState } from "react";
import axios from "axios";

import Layout from "../components/Layout";
import CollaborationStats from "../components/CollaborationStats";
import CollaborationTable from "../components/CollaborationTable";

function Collaborations() {

    const [collaborations, setCollaborations] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchCollaborations();
    }, []);

    const fetchCollaborations = async () => {

        try {

            const res = await axios.get(
                "http://127.0.0.1:8000/collaborations/"
            );

            setCollaborations(res.data);

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
                loading={loading}
            />

        </Layout>

    );

}

export default Collaborations;