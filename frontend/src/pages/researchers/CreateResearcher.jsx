import { useState } from "react";
import { useNavigate } from "react-router-dom";

import ResearcherForm from "../../components/researchers/ResearcherForm";

import { createResearcher } from "../../services/researcherService";
import { getCurrentUser } from "../../services/authService";

export default function CreateResearcher() {

    const navigate = useNavigate();

    const [loading, setLoading] = useState(false);

    const submit = async (form) => {

        try {

            setLoading(true);

            const user = await getCurrentUser();

            await createResearcher({
                user_id: user.id,
                ...form,
            });

            navigate("/researchers");

        } catch (error) {

            console.error(error);

            alert("Unable to create researcher.");

        } finally {

            setLoading(false);

        }

    };

    return (
        <div className="container py-5">

            <h2>Create Researcher</h2>

            <ResearcherForm
                loading={loading}
                onSubmit={submit}
            />

        </div>
    );
}
