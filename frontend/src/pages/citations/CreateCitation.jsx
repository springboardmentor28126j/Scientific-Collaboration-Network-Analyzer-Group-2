import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import CitationForm from "../../components/citations/CitationForm";
import { createCitation } from "../../services/citationService";
import { getPublications } from "../../services/publicationService";

function CreateCitation() {
  const navigate = useNavigate();

  const [publications, setPublications] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pageLoading, setPageLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchPublications();
  }, []);

  const fetchPublications = async () => {
    try {
      const data = await getPublications();
      setPublications(data);
    } catch (err) {
      console.error(err);
      setError("Unable to load publications.");
    } finally {
      setPageLoading(false);
    }
  };

  const handleSubmit = async (formData) => {
    try {
      setLoading(true);
      setError("");

      await createCitation(formData);

      alert("Citation created successfully.");

      navigate("/citations");
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
        setError("Failed to create citation.");
      }
    } finally {
      setLoading(false);
    }
  };

  if (pageLoading) {
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
            Create Citation
          </h2>

          {error && (
            <div className="alert alert-danger">
              {error}
            </div>
          )}

          <CitationForm
            publications={publications}
            onSubmit={handleSubmit}
            loading={loading}
          />

        </div>

      </div>

    </div>
  );
}

export default CreateCitation;
