import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import ConferenceForm from "../../components/conferences/ConferenceForm";
import {
  getConference,
  updateConference,
} from "../../services/conferenceService";

function EditConference() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [conference, setConference] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchConference();
  }, []);

  const fetchConference = async () => {
    try {
      setLoading(true);

      const data = await getConference(id);

      setConference(data);
    } catch (err) {
      console.error(err);
      setError("Unable to load conference.");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (formData) => {
    try {
      setSaving(true);
      setError("");

      await updateConference(id, formData);

      alert("Conference updated successfully.");

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
        setError("Failed to update conference.");
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

        <div className="col-lg-8">

          <h2 className="mb-4">
            Edit Conference
          </h2>

          {error && (
            <div className="alert alert-danger">
              {error}
            </div>
          )}

          <ConferenceForm
            initialData={conference}
            onSubmit={handleSubmit}
            loading={saving}
          />

        </div>

      </div>

    </div>
  );
}

export default EditConference;
