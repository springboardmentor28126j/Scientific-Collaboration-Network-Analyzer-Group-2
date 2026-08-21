import { useEffect, useState, useCallback } from "react";
import axios from "axios";
import "../css/collaborations.css";

function Collaborations() {
  const [collaborations, setCollaborations] = useState([]);
  const [researchers, setResearchers] = useState([]);
  const [showForm, setShowForm] = useState(false);

  const [formData, setFormData] = useState({
    researcher1_id: "",
    researcher2_id: "",
    project: "",
    institution: "",
    collaboration_type: "",
    start_date: "",
    status: "Active"
  });

  // Load collaborations
  const fetchCollaborations = useCallback(async () => {
    try {
      const response = await axios.get(
        "http://127.0.0.1:8001/collaborations/"
      );

      setCollaborations(response.data);
    } catch (error) {
      console.log("Error loading collaborations:", error);
    }
  }, []);

  // Load researchers
  const fetchResearchers = useCallback(async () => {
    try {
      const response = await axios.get(
        "http://127.0.0.1:8001/researchers/"
      );

      setResearchers(response.data);
    } catch (error) {
      console.log("Error loading researchers:", error);
    }
  }, []);

  // Load data when page opens
 // Load data when page opens
/* eslint-disable react-hooks/set-state-in-effect */
useEffect(() => {
  fetchCollaborations();
  fetchResearchers();
}, [fetchCollaborations, fetchResearchers]);
/* eslint-enable react-hooks/set-state-in-effect */

  // Handle form changes
  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  // Add collaboration
  const addCollaboration = async (e) => {
    e.preventDefault();

    if (
      !formData.researcher1_id ||
      !formData.researcher2_id ||
      !formData.project
    ) {
      alert("Please fill all required fields");
      return;
    }

    if (
      formData.researcher1_id === formData.researcher2_id
    ) {
      alert("Researcher 1 and Researcher 2 cannot be the same");
      return;
    }

    try {
      await axios.post(
        "http://127.0.0.1:8001/collaborations/",
        {
          researcher1_id: Number(formData.researcher1_id),
          researcher2_id: Number(formData.researcher2_id),
          project: formData.project,
          institution: formData.institution || null,
          collaboration_type:
            formData.collaboration_type || null,
          start_date: formData.start_date || null,
          status: formData.status
        }
      );

      alert("Collaboration added successfully!");

      setFormData({
        researcher1_id: "",
        researcher2_id: "",
        project: "",
        institution: "",
        collaboration_type: "",
        start_date: "",
        status: "Active"
      });

      setShowForm(false);

      fetchCollaborations();

    } catch (error) {
      console.log("Error adding collaboration:", error);

      if (error.response) {
        console.log("Backend error:", error.response.data);
      }

      alert("Unable to add collaboration");
    }
  };

  // Delete collaboration
  const deleteCollaboration = async (id) => {
    const confirmDelete = window.confirm(
      "Are you sure you want to delete this collaboration?"
    );

    if (!confirmDelete) {
      return;
    }

    try {
      await axios.delete(
        `http://127.0.0.1:8001/collaborations/${id}`
      );

      alert("Collaboration deleted successfully!");

      fetchCollaborations();

    } catch (error) {
      console.log("Error deleting collaboration:", error);
      alert("Unable to delete collaboration");
    }
  };

  // Get researcher name using researcher ID
  const getResearcherName = (id) => {
    const researcher = researchers.find(
      (r) => Number(r.researcher_id) === Number(id)
    );

    return researcher
      ? researcher.full_name
      : `Researcher ${id}`;
  };

  return (
    <div className="collaborations-page">

      {/* Header */}
      <div className="collaborations-header">

        <h1>Collaborations</h1>

        <button
          className="add-collaboration-btn"
          onClick={() => setShowForm(!showForm)}
        >
          {showForm
            ? "Close Form"
            : "+ Add Collaboration"}
        </button>

      </div>

      {/* Add Collaboration Form */}
      {showForm && (
        <form
          className="collaboration-form"
          onSubmit={addCollaboration}
        >

          <h2>Add New Collaboration</h2>

          {/* Researcher 1 */}
          <select
            name="researcher1_id"
            value={formData.researcher1_id}
            onChange={handleChange}
            required
          >
            <option value="">
              Select Researcher 1
            </option>

            {researchers.map((researcher) => (
              <option
                key={researcher.researcher_id}
                value={researcher.researcher_id}
              >
                {researcher.full_name}
              </option>
            ))}
          </select>

          {/* Researcher 2 */}
          <select
            name="researcher2_id"
            value={formData.researcher2_id}
            onChange={handleChange}
            required
          >
            <option value="">
              Select Researcher 2
            </option>

            {researchers.map((researcher) => (
              <option
                key={researcher.researcher_id}
                value={researcher.researcher_id}
              >
                {researcher.full_name}
              </option>
            ))}
          </select>

          {/* Project */}
          <input
            type="text"
            name="project"
            placeholder="Project Name"
            value={formData.project}
            onChange={handleChange}
            required
          />

          {/* Institution */}
          <input
            type="text"
            name="institution"
            placeholder="Institution"
            value={formData.institution}
            onChange={handleChange}
          />

          {/* Collaboration Type */}
          <input
            type="text"
            name="collaboration_type"
            placeholder="Collaboration Type"
            value={formData.collaboration_type}
            onChange={handleChange}
          />

          {/* Start Date */}
          <input
            type="date"
            name="start_date"
            value={formData.start_date}
            onChange={handleChange}
          />

          {/* Status */}
          <select
            name="status"
            value={formData.status}
            onChange={handleChange}
          >
            <option value="Active">
              Active
            </option>

            <option value="Completed">
              Completed
            </option>

            <option value="Pending">
              Pending
            </option>
          </select>

          {/* Buttons */}
          <div className="form-buttons">

            <button
              type="submit"
              className="save-collaboration-btn"
            >
              Save
            </button>

            <button
              type="button"
              className="cancel-collaboration-btn"
              onClick={() => setShowForm(false)}
            >
              Cancel
            </button>

          </div>

        </form>
      )}

      {/* Collaborations Table */}
      <table className="collaborations-table">

        <thead>
          <tr>
            <th>ID</th>
            <th>Researcher 1</th>
            <th>Researcher 2</th>
            <th>Project</th>
            <th>Institution</th>
            <th>Type</th>
            <th>Start Date</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>

        <tbody>

          {collaborations.length > 0 ? (

            collaborations.map((collaboration) => (

              <tr
                key={collaboration.collaboration_id}
              >

                <td>
                  {collaboration.collaboration_id}
                </td>

                <td>
                  {getResearcherName(
                    collaboration.researcher1_id
                  )}
                </td>

                <td>
                  {getResearcherName(
                    collaboration.researcher2_id
                  )}
                </td>

                <td>
                  {collaboration.project}
                </td>

                <td>
                  {collaboration.institution || "-"}
                </td>

                <td>
                  {collaboration.collaboration_type || "-"}
                </td>

                <td>
                  {collaboration.start_date || "-"}
                </td>

                <td>
                  {collaboration.status}
                </td>

                <td>

                  <button
                    className="delete-collaboration-btn"
                    onClick={() =>
                      deleteCollaboration(
                        collaboration.collaboration_id
                      )
                    }
                  >
                    Delete
                  </button>

                </td>

              </tr>

            ))

          ) : (

            <tr>
              <td
                colSpan="9"
                className="no-collaborations"
              >
                No collaborations found
              </td>
            </tr>

          )}

        </tbody>

      </table>

    </div>
  );
}

export default Collaborations;