import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  getPublication,
  updatePublication,
  uploadPublication,
} from "../services/publicationService";

function EditPublication() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [pdf, setPdf] = useState(null);

  const [loading, setLoading] = useState(true);

  const [form, setForm] = useState({
    title: "",
    abstract: "",
    doi: "",
    journal: "",
    conference: "",
    publication_year: "",
    publication_type: "",
    status: "",
    url: "",
    citation_count: 0,
  });

  useEffect(() => {
    loadPublication();
  }, []);

  const loadPublication = async () => {
    try {
      const publication = await getPublication(id);

      setForm({
        title: publication.title || "",
        abstract: publication.abstract || "",
        doi: publication.doi || "",
        journal: publication.journal || "",
        conference: publication.conference || "",
        publication_year: publication.publication_year || "",
        publication_type: publication.publication_type || "",
        status: publication.status || "",
        url: publication.url || "",
        citation_count: publication.citation_count || 0,
      });
    } catch (err) {
      console.error(err);
      alert("Unable to load publication.");
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]:
        e.target.name === "publication_year" ||
        e.target.name === "citation_count"
          ? Number(e.target.value)
          : e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      await updatePublication(id, form);

      if (pdf) {
        await uploadPublication(id, pdf);
      }

      alert("Publication updated successfully.");

      navigate("/publications");
    } catch (err) {
      console.error(err);
      alert("Failed to update publication.");
    }
  };

  if (loading) {
    return (
      <div className="container mt-5">
        <h3>Loading...</h3>
      </div>
    );
  }

  return (
    <div className="container mt-5">

      <h2 className="text-primary mb-4">
        Edit Publication
      </h2>

      <form onSubmit={handleSubmit}>

        <div className="mb-3">
          <label>Title</label>

          <input
            className="form-control"
            name="title"
            value={form.title}
            onChange={handleChange}
            required
          />
        </div>

        <div className="mb-3">
          <label>Abstract</label>

          <textarea
            rows="5"
            className="form-control"
            name="abstract"
            value={form.abstract}
            onChange={handleChange}
            required
          />
        </div>

        <div className="mb-3">
          <label>DOI</label>

          <input
            className="form-control"
            name="doi"
            value={form.doi}
            onChange={handleChange}
          />
        </div>

        <div className="mb-3">
          <label>Journal</label>

          <input
            className="form-control"
            name="journal"
            value={form.journal}
            onChange={handleChange}
          />
        </div>

        <div className="mb-3">
          <label>Conference</label>

          <input
            className="form-control"
            name="conference"
            value={form.conference}
            onChange={handleChange}
          />
        </div>

        <div className="mb-3">
          <label>Publication Year</label>

          <input
            type="number"
            className="form-control"
            name="publication_year"
            value={form.publication_year}
            onChange={handleChange}
          />
        </div>

        <div className="mb-3">
          <label>Publication Type</label>

          <input
            className="form-control"
            name="publication_type"
            value={form.publication_type}
            onChange={handleChange}
          />
        </div>

        <div className="mb-3">
          <label>Status</label>

          <input
            className="form-control"
            name="status"
            value={form.status}
            onChange={handleChange}
          />
        </div>

        <div className="mb-3">
          <label>URL</label>

          <input
            className="form-control"
            name="url"
            value={form.url}
            onChange={handleChange}
          />
        </div>

        <div className="mb-3">
          <label>Citation Count</label>

          <input
            type="number"
            className="form-control"
            name="citation_count"
            value={form.citation_count}
            onChange={handleChange}
          />
        </div>

        <div className="mb-4">
          <label>Replace PDF (Optional)</label>

          <input
            type="file"
            accept=".pdf"
            className="form-control"
            onChange={(e) => setPdf(e.target.files[0])}
          />
        </div>

        <button
          className="btn btn-warning me-2"
          type="submit"
        >
          Update Publication
        </button>

        <button
          type="button"
          className="btn btn-secondary"
          onClick={() => navigate("/publications")}
        >
          Cancel
        </button>

      </form>

    </div>
  );
}

export default EditPublication;
