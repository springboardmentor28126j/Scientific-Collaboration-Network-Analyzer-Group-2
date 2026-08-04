import { useState } from "react";
import { useNavigate } from "react-router-dom";

import ConferenceForm from "../../components/conferences/ConferenceForm";
import { createConference } from "../../services/conferenceService";

function CreateConference() {
  const navigate = useNavigate();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (formData) => {
    try {
      setLoading(true);
      setError("");

      await createConference(formData);

      alert("Conference created successfully.");

      navigate("/conferences");
    } catch (err) {
      console.error(err);

      if (err.response?.data?.detail) {
        if (Array.isArray(err.response.data.detail)) {
          setError(
            err.response.data.detail
              .map((item) => item.msg)
              .join(", ")
          );
        } else {
          setError(err.response.data.detail);
        }
      } else {
        setError("Failed to create conference.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mt-4">

      <div className="row justify-content-center">

        <div className="col-lg-8">

          <h2 className="mb-4">
            Create Conference
          </h2>

          {error && (
            <div className="alert alert-danger">
              {error}
            </div>
          )}

          <ConferenceForm
            onSubmit={handleSubmit}
            loading={loading}
          />

        </div>

      </div>

    </div>
  );
}

export default CreateConference;
