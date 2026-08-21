import { Link } from "react-router-dom";
import { useState, useEffect } from "react";
import axios from "axios";
import "../css/researchers.css";

function Researchers() {
  const [showForm, setShowForm] = useState(false);
  const [researchers, setResearchers] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");

  const [formData, setFormData] = useState({
    full_name: "",
    email: "",
    institution: "",
    department: "",
    country: ""
  });

  useEffect(() => {
    const getResearchers = async () => {
      try {
        const response = await axios.get(
          "http://127.0.0.1:8001/researchers/"
        );

        setResearchers(response.data);
      } catch (error) {
        console.log(error);
      }
    };

    getResearchers();
  }, []);

  const fetchResearchers = async () => {
    try {
      const response = await axios.get(
        "http://127.0.0.1:8001/researchers/"
      );

      setResearchers(response.data);
    } catch (error) {
      console.log(error);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const saveResearcher = async () => {
    try {
      await axios.post(
        "http://127.0.0.1:8001/researchers/",
        formData
      );

      alert("Researcher added successfully!");

      setFormData({
        full_name: "",
        email: "",
        institution: "",
        department: "",
        country: ""
      });

      setShowForm(false);

      fetchResearchers();
    } catch (error) {
      console.log(error);
      alert("Unable to save researcher");
    }
  };

  const deleteResearcher = async (id) => {
    const confirmDelete = window.confirm(
      "Are you sure you want to delete this researcher?"
    );

    if (!confirmDelete) {
      return;
    }

    try {
      await axios.delete(
        `http://127.0.0.1:8001/researchers/${id}`
      );

      alert("Researcher deleted successfully!");

      fetchResearchers();
    } catch (error) {
      console.log(error);
      alert("Unable to delete researcher");
    }
  };

  const filteredResearchers = researchers.filter((researcher) => {
    const search = searchTerm.toLowerCase();

    return (
      String(researcher.researcher_id || "")
        .toLowerCase()
        .includes(search) ||
      String(researcher.full_name || "")
        .toLowerCase()
        .includes(search) ||
      String(researcher.institution || "")
        .toLowerCase()
        .includes(search) ||
      String(researcher.department || "")
        .toLowerCase()
        .includes(search) ||
      String(researcher.country || "")
        .toLowerCase()
        .includes(search)
    );
  });

  return (
    <div className="researchers-page">

      <div className="researchers-header">

        <h1>Researchers</h1>

        <div className="header-buttons">

          <input
            type="text"
            placeholder="Search researcher..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />

          <button
            className="add-btn"
            onClick={() => setShowForm(true)}
          >
            + Add Researcher
          </button>

        </div>

      </div>

      {showForm && (
        <div className="form-box">

          <h2>Add New Researcher</h2>

          <input
            type="text"
            name="full_name"
            placeholder="Full Name"
            value={formData.full_name}
            onChange={handleChange}
          />

          <input
            type="email"
            name="email"
            placeholder="Email Address"
            value={formData.email}
            onChange={handleChange}
          />

          <input
            type="text"
            name="institution"
            placeholder="Institution"
            value={formData.institution}
            onChange={handleChange}
          />

          <input
            type="text"
            name="department"
            placeholder="Department"
            value={formData.department}
            onChange={handleChange}
          />

          <input
            type="text"
            name="country"
            placeholder="Country"
            value={formData.country}
            onChange={handleChange}
          />

          <div className="form-buttons">

            <button
              className="save-btn"
              onClick={saveResearcher}
            >
              Save
            </button>

            <button
              className="cancel-btn"
              onClick={() => setShowForm(false)}
            >
              Cancel
            </button>

          </div>

        </div>
      )}

      <table className="researchers-table">

        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Institution</th>
            <th>Department</th>
            <th>Country</th>
            <th>Action</th>
          </tr>
        </thead>

        <tbody>

          {filteredResearchers.length > 0 ? (

            filteredResearchers.map((researcher) => (

              <tr key={researcher.researcher_id}>

                <td>
                  {researcher.researcher_id}
                </td>

                <td>
                  {researcher.full_name}
                </td>

                <td>
                  {researcher.institution}
                </td>

                <td>
                  {researcher.department}
                </td>

                <td>
                  {researcher.country}
                </td>

                <td className="action-buttons">

                  <Link
                    to="/profile"
                    className="view-btn"
                  >
                    View
                  </Link>

                  <button
                    className="delete-btn"
                    onClick={() =>
                      deleteResearcher(
                        researcher.researcher_id
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
              <td colSpan="6">
                No researchers found
              </td>
            </tr>

          )}

        </tbody>

      </table>

    </div>
  );
}

export default Researchers;