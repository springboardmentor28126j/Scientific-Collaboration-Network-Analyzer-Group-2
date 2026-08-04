import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import InstitutionForm from "../../components/institutions/InstitutionForm";
import {
  getInstitution,
  updateInstitution,
} from "../../services/institutionService";

function EditInstitution() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [institution, setInstitution] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchInstitution();
  }, []);

  const fetchInstitution = async () => {
    try {
      setLoading(true);

      const data = await getInstitution(id);

      setInstitution(data);
    } catch (err) {
      console.error(err);
      setError("Unable to load institution details.");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (formData) => {
    try {
      setSaving(true);
      setError("");

      await updateInstitution(id, formData);

      alert("Institution updated successfully.");

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
        setError("Failed to update institution.");
      }
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="container mt-5 text-center">
        <div
          className="spinner-border text-primary"
          role="status"
        ></div>
      </div>
    );
  }

  return (
    <div className="container mt-4">

      <div className="row justify-content-center">

        <div className="col-lg-10">

          <h2 className="mb-4">
            Edit Institution
          </h2>

          {error && (
            <div className="alert alert-danger">
              {error}
            </div>
          )}

          <InstitutionForm
            initialData={institution}
            onSubmit={handleSubmit}
            loading={saving}
          />

        </div>

      </div>

    </div>
  );
}

export default EditInstitution;
