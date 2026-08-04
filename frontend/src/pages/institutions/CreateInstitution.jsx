import { useState } from "react";
import { useNavigate } from "react-router-dom";

import InstitutionForm from "../../components/institutions/InstitutionForm";
import { createInstitution } from "../../services/institutionService";

function CreateInstitution() {
  const navigate = useNavigate();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (formData) => {
    try {
      setLoading(true);
      setError("");

      await createInstitution(formData);

      alert("Institution created successfully.");

      navigate("/institutions");
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
        setError("Failed to create institution.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mt-4">

      <div className="row justify-content-center">

        <div className="col-lg-10">

          <h2 className="mb-4">
            Create Institution
          </h2>

          {error && (
            <div className="alert alert-danger">
              {error}
            </div>
          )}

          <InstitutionForm
            onSubmit={handleSubmit}
            loading={loading}
          />

        </div>

      </div>

    </div>
  );
}

export default CreateInstitution;
