import { Link } from "react-router-dom";
import { useState } from "react";
import "../css/researchers.css";

function Researchers() {

  const [showForm, setShowForm] = useState(false);

  const researchers = [
    {
      id: 1,
      name: "Jhansi Padala",
      institution: "SCET",
      department: "AI & ML",
      country: "India"
    },
    {
      id: 2,
      name: "Rahul Kumar",
      institution: "IIT Hyderabad",
      department: "Computer Science",
      country: "India"
    },
    {
      id: 3,
      name: "Priya Sharma",
      institution: "NIT Warangal",
      department: "Data Science",
      country: "India"
    }
  ];

  return (
    <div className="researchers-page">

      {/* Header */}
      <div className="researchers-header">

        <h1>Researchers</h1>

        <div className="header-buttons">

          <input
            type="text"
            placeholder="Search researcher..."
          />

          <button
            className="add-btn"
            onClick={() => setShowForm(true)}
          >
            + Add Researcher
          </button>

        </div>

      </div>

      {/* Add Researcher Form */}
      {showForm && (

        <div className="form-box">

          <h2>Add New Researcher</h2>

          <input
            type="text"
            placeholder="Full Name"
          />

          <input
            type="email"
            placeholder="Email Address"
          />

          <input
            type="text"
            placeholder="Institution"
          />

          <input
            type="text"
            placeholder="Department"
          />

          <input
            type="text"
            placeholder="Country"
          />

          <div className="form-buttons">

            <button className="save-btn">
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

      {/* Table */}

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

          {researchers.map((researcher) => (

            <tr key={researcher.id}>

              <td>{researcher.id}</td>

              <td>{researcher.name}</td>

              <td>{researcher.institution}</td>

              <td>{researcher.department}</td>

              <td>{researcher.country}</td>

              <td>

                <Link
                  to="/profile"
                  className="view-btn"
                >
                  View
                </Link>

              </td>

            </tr>

          ))}

        </tbody>

      </table>

    </div>
  );
}

export default Researchers;