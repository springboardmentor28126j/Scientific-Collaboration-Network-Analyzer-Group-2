import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import CitationForm from "../../components/citations/CitationForm";

import {
  getCitation,
  updateCitation,
} from "../../services/citationService";

import {
  getPublications,
} from "../../services/publicationService";

function EditCitation() {

  const { id } = useParams();

  const navigate = useNavigate();

  const [citation, setCitation] = useState(null);

  const [publications, setPublications] = useState([]);

  const [loading, setLoading] = useState(true);

  const [saving, setSaving] = useState(false);

  const [error, setError] = useState("");

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {

    try {

      setLoading(true);

      const [citationData, publicationData] =
        await Promise.all([
          getCitation(id),
          getPublications(),
        ]);

      setCitation(citationData);

      setPublications(publicationData);

    } catch (err) {

      console.error(err);

      setError(
        "Unable to load citation details."
      );

    } finally {

      setLoading(false);

    }

  };

  const handleSubmit = async (formData) => {

    try {

      setSaving(true);

      setError("");

      await updateCitation(
        id,
        formData
      );

      alert(
        "Citation updated successfully."
      );

      navigate("/citations");

    } catch (err) {

      console.error(err);

      if (
        err.response?.data?.detail
      ) {

        if (
          Array.isArray(
            err.response.data.detail
          )
        ) {

          setError(

            err.response.data.detail
              .map(
                (item) => item.msg
              )
              .join(", ")

          );

        } else {

          setError(
            err.response.data.detail
          );

        }

      } else {

        setError(
          "Failed to update citation."
        );

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

            Edit Citation

          </h2>

          {error && (

            <div className="alert alert-danger">

              {error}

            </div>

          )}

          <CitationForm
            initialData={citation}
            publications={publications}
            onSubmit={handleSubmit}
            loading={saving}
          />

        </div>

      </div>

    </div>

  );

}

export default EditCitation;
