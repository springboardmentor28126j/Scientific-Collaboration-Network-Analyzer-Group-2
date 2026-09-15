import { useEffect, useState } from "react";
import axios from "axios";
import "../css/Publications.css";

function Publications() {
  const [publications, setPublications] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(() => Boolean(localStorage.getItem("access_token")));

  const token = localStorage.getItem("access_token");
  const role = localStorage.getItem("role");

  const [formData, setFormData] = useState({
    title: "",
    publication_type: "Journal Paper",
    abstract: "",
    keywords: "",
    author: "",
    journal: "",
    year: "",
    status: "Draft",
    pdf_file: "",
    researcher_id: "",
  });

  // =====================================================
  // LOAD PUBLICATIONS
  // =====================================================

  useEffect(() => {
    let cancelled = false;

    const fetchPublications = async () => {
      try {
        setLoading(true);

        const response = await axios.get(
          "http://127.0.0.1:8000/publications/",
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (!cancelled) {
          setPublications(response.data);
        }
      } catch (error) {
        console.log("Error loading publications:", error);

        if (!cancelled) {
          if (error.response?.status === 401) {
            alert("Please login again.");
          } else if (error.response?.status === 403) {
            alert(
              "You are not authorized to view publications."
            );
          }

          setPublications([]);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    if (token) {
      fetchPublications();
    }

    return () => {
      cancelled = true;
    };
  }, [token]);

  // =====================================================
  // HANDLE FORM CHANGE
  // =====================================================

  const handleChange = (event) => {
    setFormData({
      ...formData,
      [event.target.name]: event.target.value,
    });
  };

  // =====================================================
  // HANDLE PDF UPLOAD
  // =====================================================

  const handlePdfUpload = async (event) => {
    const file = event.target.files[0];

    if (!file) {
      return;
    }

    // Allow PDF files only
    if (file.type !== "application/pdf") {
      alert("Please select a PDF file only.");
      event.target.value = "";
      return;
    }

    if (!token) {
      alert("Please login first.");
      event.target.value = "";
      return;
    }

    try {
      const uploadData = new FormData();

      uploadData.append("file", file);

      const response = await axios.post(
        "http://127.0.0.1:8000/files/upload",
        uploadData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "multipart/form-data",
          },
        }
      );

      // Store the path returned by FastAPI
      setFormData((previous) => ({
        ...previous,
        pdf_file: response.data.file_path,
      }));

      alert("PDF uploaded successfully.");
    } catch (error) {
      console.log("PDF upload error:", error);

      alert(
        error.response?.data?.detail ||
          "Unable to upload PDF."
      );

      event.target.value = "";
    }
  };

  // =====================================================
  // RESET FORM
  // =====================================================

  const resetForm = () => {
    setFormData({
      title: "",
      publication_type: "Journal Paper",
      abstract: "",
      keywords: "",
      author: "",
      journal: "",
      year: "",
      status: "Draft",
      pdf_file: "",
      researcher_id: "",
    });

    setEditingId(null);
    setShowForm(false);
  };

  // =====================================================
  // RELOAD PUBLICATIONS
  // =====================================================

  const reloadPublications = async () => {
    try {
      const response = await axios.get(
        "http://127.0.0.1:8000/publications/",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setPublications(response.data);
    } catch (error) {
      console.log(
        "Error reloading publications:",
        error
      );
    }
  };

  // =====================================================
  // ADD / UPDATE PUBLICATION
  // =====================================================

  const savePublication = async (event) => {
    event.preventDefault();

    if (!token) {
      alert("Please login first.");
      return;
    }

    // PDF required for new publication
    if (!editingId && !formData.pdf_file) {
      alert("Please upload a PDF file.");
      return;
    }

    try {
      const data = {
        title: formData.title,
        publication_type: formData.publication_type,
        abstract: formData.abstract || null,
        keywords: formData.keywords || null,
        author: formData.author,
        journal: formData.journal,
        year: Number(formData.year),
        status: formData.status,
        pdf_file: formData.pdf_file || null,
        researcher_id: Number(formData.researcher_id),
      };

      // =================================================
      // UPDATE PUBLICATION
      // =================================================

      if (editingId) {
        await axios.put(
          `http://127.0.0.1:8000/publications/${editingId}`,
          data,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        alert(
          "Publication updated successfully."
        );
      }

      // =================================================
      // CREATE PUBLICATION
      // =================================================

      else {
        await axios.post(
          "http://127.0.0.1:8000/publications/",
          data,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        alert(
          "Publication added successfully."
        );
      }

      resetForm();

      await reloadPublications();
    } catch (error) {
      console.log(
        "Publication error:",
        error
      );

      alert(
        error.response?.data?.detail ||
          "Unable to save publication."
      );
    }
  };

  // =====================================================
  // EDIT PUBLICATION
  // =====================================================

  const editPublication = (pub) => {
    setEditingId(pub.publication_id);

    setFormData({
      title: pub.title || "",
      publication_type:
        pub.publication_type ||
        "Journal Paper",
      abstract: pub.abstract || "",
      keywords: pub.keywords || "",
      author: pub.author || "",
      journal: pub.journal || "",
      year: pub.year || "",
      status: pub.status || "Draft",
      pdf_file: pub.pdf_file || "",
      researcher_id:
        pub.researcher_id || "",
    });

    setShowForm(true);

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  // =====================================================
  // DELETE PUBLICATION
  // =====================================================

  const deletePublication = async (id) => {
    if (
      !window.confirm(
        "Are you sure you want to delete this publication?"
      )
    ) {
      return;
    }

    try {
      await axios.delete(
        `http://127.0.0.1:8000/publications/${id}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      alert(
        "Publication deleted successfully."
      );

      await reloadPublications();
    } catch (error) {
      console.log(
        "Delete error:",
        error
      );

      alert(
        error.response?.data?.detail ||
          "Unable to delete publication."
      );
    }
  };

  // =====================================================
  // CHANGE WORKFLOW STATUS
  // =====================================================

  const changeStatus = async (
    pub,
    newStatus
  ) => {
    if (newStatus === pub.status) {
      return;
    }

    try {
      await axios.put(
        `http://127.0.0.1:8000/publications/${pub.publication_id}`,
        {
          status: newStatus,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      alert(
        `Publication status changed to "${newStatus}".`
      );

      await reloadPublications();
    } catch (error) {
      console.log(
        "Status update error:",
        error
      );

      alert(
        error.response?.data?.detail ||
          "Status change is not allowed."
      );

      await reloadPublications();
    }
  };

  // =====================================================
  // UI
  // =====================================================

  return (
    <div className="container">

      <h2>Publications</h2>

      {/* =================================================
          ADD PUBLICATION BUTTON
          ================================================= */}

      {role !== "Reviewer" && (
        <button
          type="button"
          onClick={() => {
            if (showForm) {
              resetForm();
            } else {
              setEditingId(null);

              setFormData({
                title: "",
                publication_type:
                  "Journal Paper",
                abstract: "",
                keywords: "",
                author: "",
                journal: "",
                year: "",
                status: "Draft",
                pdf_file: "",
                researcher_id: "",
              });

              setShowForm(true);
            }
          }}
        >
          {showForm
            ? "Close Form"
            : "Add Publication"}
        </button>
      )}

      {/* =================================================
          PUBLICATION FORM
          ================================================= */}

      {showForm &&
        role !== "Reviewer" && (
          <form onSubmit={savePublication}>

            <h3>
              {editingId
                ? "Edit Publication"
                : "Add Publication"}
            </h3>

            {/* TITLE */}

            <input
              type="text"
              name="title"
              placeholder="Title"
              value={formData.title}
              onChange={handleChange}
              required
            />

            {/* PUBLICATION TYPE */}

            <select
              name="publication_type"
              value={
                formData.publication_type
              }
              onChange={handleChange}
              required
            >
              <option value="Journal Paper">
                Journal Paper
              </option>

              <option value="Conference Paper">
                Conference Paper
              </option>

              <option value="Book">
                Book
              </option>

              <option value="Patent">
                Patent
              </option>

              <option value="Technical Report">
                Technical Report
              </option>
            </select>

            {/* ABSTRACT */}

            <textarea
              name="abstract"
              placeholder="Abstract"
              value={formData.abstract}
              onChange={handleChange}
              rows="4"
            />

            {/* KEYWORDS */}

            <input
              type="text"
              name="keywords"
              placeholder="Keywords"
              value={formData.keywords}
              onChange={handleChange}
            />

            {/* AUTHOR */}

            <input
              type="text"
              name="author"
              placeholder="Author"
              value={formData.author}
              onChange={handleChange}
              required
            />

            {/* JOURNAL */}

            <input
              type="text"
              name="journal"
              placeholder="Journal"
              value={formData.journal}
              onChange={handleChange}
              required
            />

            {/* YEAR */}

            <input
              type="number"
              name="year"
              placeholder="Year"
              value={formData.year}
              onChange={handleChange}
              required
            />

            {/* STATUS */}

            <select
              name="status"
              value={formData.status}
              onChange={handleChange}
            >
              <option value="Draft">
                Draft
              </option>

              <option value="Submitted">
                Submitted
              </option>

              <option value="Reviewer Assigned">
                Reviewer Assigned
              </option>

              <option value="Review Submitted">
                Review Submitted
              </option>

              <option value="Editorial Decision">
                Editorial Decision
              </option>

              <option value="Published">
                Published
              </option>

              <option value="Rejected">
                Rejected
              </option>

              <option value="Archived">
                Archived
              </option>
            </select>

            {/* =================================================
                PDF UPLOAD
                ================================================= */}

            <label>
              Upload Publication PDF
            </label>

            <input
              type="file"
              accept=".pdf,application/pdf"
              onChange={handlePdfUpload}
            />

            {/* SHOW UPLOADED PDF */}

            {formData.pdf_file && (
              <p>
                PDF uploaded:{" "}
                {formData.pdf_file}
              </p>
            )}

            {/* RESEARCHER ID */}

            <input
              type="number"
              name="researcher_id"
              placeholder="Researcher ID"
              value={
                formData.researcher_id
              }
              onChange={handleChange}
              required
            />

            {/* SAVE BUTTON */}

            <button type="submit">
              {editingId
                ? "Update Publication"
                : "Save Publication"}
            </button>

            {/* CANCEL BUTTON */}

            {editingId && (
              <button
                type="button"
                onClick={resetForm}
              >
                Cancel
              </button>
            )}

          </form>
        )}

      {/* =================================================
          LOADING
          ================================================= */}

      {loading ? (
        <p>
          Loading publications...
        </p>
      ) : publications.length === 0 ? (
        <p>
          No publications found.
        </p>
      ) : (

        /* =================================================
           PUBLICATIONS TABLE
           ================================================= */

        <div className="table-wrapper">

          <table>

            <thead>

              <tr>
                <th>ID</th>
                <th>Title</th>
                <th>Type</th>
                <th>Abstract</th>
                <th>Keywords</th>
                <th>Author</th>
                <th>Journal</th>
                <th>Year</th>
                <th>Status</th>
                <th>PDF File</th>
                <th>Researcher ID</th>
                <th>Action</th>
              </tr>

            </thead>

            <tbody>

              {publications.map(
                (pub) => (

                  <tr
                    key={
                      pub.publication_id
                    }
                  >

                    <td>
                      {
                        pub.publication_id
                      }
                    </td>

                    <td>
                      {pub.title}
                    </td>

                    <td>
                      {
                        pub.publication_type ||
                        "-"
                      }
                    </td>

                    <td>
                      {
                        pub.abstract ||
                        "-"
                      }
                    </td>

                    <td>
                      {
                        pub.keywords ||
                        "-"
                      }
                    </td>

                    <td>
                      {pub.author}
                    </td>

                    <td>
                      {pub.journal}
                    </td>

                    <td>
                      {pub.year}
                    </td>

                    {/* STATUS */}

                    <td>

                      <select
                        value={
                          pub.status
                        }
                        onChange={(
                          event
                        ) =>
                          changeStatus(
                            pub,
                            event.target
                              .value
                          )
                        }
                        disabled={
                          role ===
                          "Reviewer"
                        }
                      >

                        <option value="Draft">
                          Draft
                        </option>

                        <option value="Submitted">
                          Submitted
                        </option>

                        <option value="Reviewer Assigned">
                          Reviewer Assigned
                        </option>

                        <option value="Review Submitted">
                          Review Submitted
                        </option>

                        <option value="Editorial Decision">
                          Editorial Decision
                        </option>

                        <option value="Published">
                          Published
                        </option>

                        <option value="Rejected">
                          Rejected
                        </option>

                        <option value="Archived">
                          Archived
                        </option>

                      </select>

                    </td>

                    {/* PDF */}

                    <td>

                      {pub.pdf_file ? (
                        <span>
                          {
                            pub.pdf_file
                          }
                        </span>
                      ) : (
                        "-"
                      )}

                    </td>

                    {/* RESEARCHER ID */}

                    <td>
                      {
                        pub.researcher_id ||
                        "-"
                      }
                    </td>

                    {/* ACTION */}

                    <td>

                      {role !==
                        "Reviewer" && (
                        <>
                          <button
                            type="button"
                            onClick={() =>
                              editPublication(
                                pub
                              )
                            }
                          >
                            Edit
                          </button>

                          <button
                            type="button"
                            onClick={() =>
                              deletePublication(
                                pub.publication_id
                              )
                            }
                          >
                            Delete
                          </button>
                        </>
                      )}

                      {role ===
                        "Reviewer" && (
                        <span>
                          View Only
                        </span>
                      )}

                    </td>

                  </tr>

                )
              )}

            </tbody>

          </table>

        </div>
      )}

    </div>
  );
}

export default Publications;