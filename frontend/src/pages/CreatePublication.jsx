import { useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  createPublication,
  uploadPublication,
} from "../services/publicationService";

function CreatePublication() {
  const navigate = useNavigate();

  const [pdf, setPdf] = useState(null);

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

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]:
        e.target.name === "citation_count" ||
        e.target.name === "publication_year"
          ? Number(e.target.value)
          : e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      // Create publication
      const publication = await createPublication(form);

      // Upload PDF if selected
      if (pdf) {
        await uploadPublication(publication.id, pdf);
      }

      alert("Publication created successfully.");

      navigate("/publications");
    } catch (err) {
      console.error(err);
      alert("Failed to create publication.");
    }
  };

  return (
    <div className="container mt-5">

      <h2 className="mb-4 text-primary">
        Create Publication
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
            className="form-control"
            rows="4"
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
          <label>Upload PDF</label>

          <input
            type="file"
            accept=".pdf"
            className="form-control"
            onChange={(e) => setPdf(e.target.files[0])}
          />
        </div>

        <button
          className="btn btn-success"
          type="submit"
        >
          Create Publication
        </button>

      </form>
    </div>
  );
}

export default CreatePublication;
