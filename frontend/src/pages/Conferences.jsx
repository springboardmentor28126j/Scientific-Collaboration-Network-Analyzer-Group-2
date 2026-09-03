import { useEffect, useState } from "react";
import "../css/conferences.css";
function Conference() {
  const [conferences, setConferences] = useState([]);
  const [publications, setPublications] = useState([]);

  const [showForm, setShowForm] = useState(false);

  const [formData, setFormData] = useState({
    conference_name: "",
    location: "",
    conference_date: "",
    publication_id: ""
  });

  // Get conferences
  const fetchConferences = () => {
    fetch("http://127.0.0.1:8000/conferences/")
      .then((response) => response.json())
      .then((data) => {
        setConferences(data);
      })
      .catch((error) => {
        console.error("Error fetching conferences:", error);
      });
  };

  // Get publications
  const fetchPublications = () => {
    fetch("http://127.0.0.1:8000/publications/")
      .then((response) => response.json())
      .then((data) => {
        setPublications(data);
      })
      .catch((error) => {
        console.error("Error fetching publications:", error);
      });
  };

  useEffect(() => {
    fetchConferences();
    fetchPublications();
  }, []);

  // Handle input changes
  const handleChange = (event) => {
    setFormData({
      ...formData,
      [event.target.name]: event.target.value
    });
  };

  // Add conference
  const handleSubmit = (event) => {
    event.preventDefault();

    const dataToSend = {
      conference_name: formData.conference_name,
      location: formData.location,
      conference_date: formData.conference_date,
      publication_id: Number(formData.publication_id)
    };

    fetch("http://127.0.0.1:8000/conferences/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(dataToSend)
    })
      .then(async (response) => {
        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || "Failed to add conference");
        }

        return data;
      })
      .then(() => {
        alert("Conference added successfully!");

        setFormData({
          conference_name: "",
          location: "",
          conference_date: "",
          publication_id: ""
        });

        setShowForm(false);

        fetchConferences();
      })
      .catch((error) => {
        console.error("Error adding conference:", error);
        alert(error.message);
      });
  };

  // Delete conference
  const handleDelete = (conferenceId) => {
    if (!window.confirm("Are you sure you want to delete this conference?")) {
      return;
    }

    fetch(`http://127.0.0.1:8000/conferences/${conferenceId}`, {
      method: "DELETE"
    })
      .then(async (response) => {
        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || "Failed to delete conference");
        }

        return data;
      })
      .then(() => {
        alert("Conference deleted successfully!");
        fetchConferences();
      })
      .catch((error) => {
        console.error("Error deleting conference:", error);
        alert(error.message);
      });
  };

  return (
    <div className="conferences-page">

      <div className="conferences-header">
        <h1>Conferences</h1>

        <button
          className="add-conference-btn"
          onClick={() => setShowForm(!showForm)}
        >
          {showForm ? "Close Form" : "+ Add Conference"}
        </button>
      </div>

      {showForm && (
        <form
          className="conference-form"
          onSubmit={handleSubmit}
        >
          <h2>Add Conference</h2>

          <input
            type="text"
            name="conference_name"
            placeholder="Conference Name"
            value={formData.conference_name}
            onChange={handleChange}
            required
          />

          <input
            type="text"
            name="location"
            placeholder="Location"
            value={formData.location}
            onChange={handleChange}
            required
          />

          <input
            type="date"
            name="conference_date"
            value={formData.conference_date}
            onChange={handleChange}
            required
          />

          <select
            name="publication_id"
            value={formData.publication_id}
            onChange={handleChange}
            required
          >
            <option value="">Select Publication</option>

            {publications.map((publication) => (
              <option
                key={publication.publication_id}
                value={publication.publication_id}
              >
                {publication.title}
              </option>
            ))}
          </select>

          <div className="conference-form-buttons">
            <button
              type="submit"
              className="save-conference-btn"
            >
              Save Conference
            </button>

            <button
              type="button"
              className="cancel-conference-btn"
              onClick={() => setShowForm(false)}
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      <table className="conferences-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Conference Name</th>
            <th>Location</th>
            <th>Date</th>
            <th>Publication ID</th>
            <th>Action</th>
          </tr>
        </thead>

        <tbody>
          {conferences.length === 0 ? (
            <tr>
              <td
                colSpan="6"
                className="no-conferences"
              >
                No conferences found
              </td>
            </tr>
          ) : (
            conferences.map((conference) => (
              <tr key={conference.conference_id}>
                <td>{conference.conference_id}</td>

                <td>{conference.conference_name}</td>

                <td>{conference.location}</td>

                <td>{conference.conference_date}</td>

                <td>{conference.publication_id}</td>

                <td>
                  <button
                    className="delete-conference-btn"
                    onClick={() =>
                      handleDelete(conference.conference_id)
                    }
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>

    </div>
  );
}

export default Conference;