import { Link, useNavigate } from "react-router-dom";
import "../css/dashboard.css";

function Dashboard() {
  const navigate = useNavigate();

  // Get logged-in user details
  const username = localStorage.getItem("username");
  const role = localStorage.getItem("role");

  // Logout
  const handleLogout = () => {
    localStorage.removeItem("username");
    localStorage.removeItem("email");
    localStorage.removeItem("role");

    navigate("/");
  };

  return (
    <div className="dashboard-container">

      {/* ================= TOP NAVBAR ================= */}

      <header className="topbar">

        <div className="logo">
          <span className="logo-icon">🔬</span>
          <span className="logo-text">SciCollab</span>
        </div>

        <div className="top-links">

          <Link to="/dashboard">
            Dashboard
          </Link>

          {/* Researchers */}
          {(role === "Researcher" ||
            role === "Institution Admin" ||
            role === "System Admin") && (
            <Link to="/researchers">
              Researchers
            </Link>
          )}

          {/* Publications */}
          {(role === "Researcher" ||
            role === "Institution Admin" ||
            role === "Reviewer" ||
            role === "System Admin") && (
            <Link to="/publications">
              Publications
            </Link>
          )}

          {/* Collaborations */}
          {(role === "Researcher" ||
            role === "Institution Admin" ||
            role === "System Admin") && (
            <Link to="/collaborations">
              Collaborations
            </Link>
          )}

          {/* Profile */}
          <Link to="/profile">
            Profile
          </Link>

          {/* Logout */}
          <button
            className="logout-btn"
            onClick={handleLogout}
          >
            Logout
          </button>

        </div>

      </header>


      {/* ================= DASHBOARD BODY ================= */}

      <div className="dashboard-body">


        {/* ================= SIDEBAR ================= */}

        <aside className="sidebar">

          <h3>Menu</h3>

          <ul>

            {/* Dashboard */}
            <li>
              <Link to="/dashboard">
                🏠 Dashboard
              </Link>
            </li>


            {/* Researchers */}

            {(role === "Researcher" ||
              role === "Institution Admin" ||
              role === "System Admin") && (
              <li>
                <Link to="/researchers">
                  👨‍🔬 Researchers
                </Link>
              </li>
            )}


            {/* Publications */}

            {(role === "Researcher" ||
              role === "Institution Admin" ||
              role === "Reviewer" ||
              role === "System Admin") && (
              <li>
                <Link to="/publications">
                  📄 Publications
                </Link>
              </li>
            )}


            {/* Collaborations */}

            {(role === "Researcher" ||
              role === "Institution Admin" ||
              role === "System Admin") && (
              <li>
                <Link to="/collaborations">
                  🤝 Collaborations
                </Link>
              </li>
            )}


            {/* Conferences */}

            {(role === "Researcher" ||
              role === "Institution Admin" ||
              role === "Reviewer" ||
              role === "System Admin") && (
              <li>
                <Link to="/conferences">
                  📅 Conferences
                </Link>
              </li>
            )}


            {/* Analytics */}

            {(role === "Institution Admin" ||
              role === "System Admin") && (
              <li>
                <Link to="/analytics">
                  📊 Analytics
                </Link>
              </li>
            )}


            {/* Reports */}

            {(role === "Institution Admin" ||
              role === "Reviewer" ||
              role === "System Admin") && (
              <li>
                <Link to="/reports">
                  📋 Reports
                </Link>
              </li>
            )}
            {/* Reviews */}

            {(role === "Institution Admin" ||
  role === "Reviewer" ||
            role === "System Admin") && (
            <li>
            <Link to="/reviews">
            📝 Reviews
             </Link>
              </li>
            )}

            {/* Profile */}

            <li>
              <Link to="/profile">
                👤 Profile
              </Link>
            </li>

          </ul>

        </aside>


        {/* ================= MAIN CONTENT ================= */}

        <main className="content">


          {/* Welcome */}

          <h1>
            Welcome Back {username ? username : ""} 👋
          </h1>

          <p>
            Monitor your publications, collaborations,
            researchers, and conferences from one place.
          </p>


          {/* ================= ROLE ================= */}

          <div
            style={{
              marginBottom: "25px",
              padding: "12px 20px",
              backgroundColor: "#e8f2ff",
              borderRadius: "8px",
              fontWeight: "bold",
              fontSize: "18px",
              textAlign: "center"
            }}
          >
            Logged in as: {role || "User"}
          </div>


          {/* ================= SYSTEM ADMIN ================= */}

          {role === "System Admin" && (
            <div
              style={{
                marginBottom: "25px",
                padding: "20px",
                backgroundColor: "#f1f7ff",
                border: "1px solid #c8ddf5",
                borderRadius: "10px",
                textAlign: "center"
              }}
            >

              <h2>
                ⚙️ System Admin Dashboard
              </h2>

              <p>
                You have full access to the Scientific
                Collaboration Network Analyzer system.
              </p>

            </div>
          )}


          {/* ================= INSTITUTION ADMIN ================= */}

          {role === "Institution Admin" && (
            <div
              style={{
                marginBottom: "25px",
                padding: "20px",
                backgroundColor: "#f1f7ff",
                border: "1px solid #c8ddf5",
                borderRadius: "10px",
                textAlign: "center"
              }}
            >

              <h2>
                🏛️ Institution Admin Dashboard
              </h2>

              <p>
                You can manage institution-related research,
                publications, collaborations, conferences,
                and analytics.
              </p>

            </div>
          )}


          {/* ================= RESEARCHER ================= */}

          {role === "Researcher" && (
            <div
              style={{
                marginBottom: "25px",
                padding: "20px",
                backgroundColor: "#f1f7ff",
                border: "1px solid #c8ddf5",
                borderRadius: "10px",
                textAlign: "center"
              }}
            >

              <h2>
                👨‍🔬 Researcher Dashboard
              </h2>

              <p>
                Manage your researcher profile,
                publications, collaborations, and conferences.
              </p>

            </div>
          )}


          {/* ================= REVIEWER ================= */}

          {role === "Reviewer" && (
            <div
              style={{
                marginBottom: "25px",
                padding: "20px",
                backgroundColor: "#f1f7ff",
                border: "1px solid #c8ddf5",
                borderRadius: "10px",
                textAlign: "center"
              }}
            >

              <h2>
                📝 Reviewer Dashboard
              </h2>

              <p>
                Access publications, conferences,
                and review-related reports.
              </p>

            </div>
          )}


          {/* ================= DASHBOARD CARDS ================= */}

          <div className="cards">

            <div className="card">
              <h2>150</h2>
              <p>Researchers</p>
            </div>

            <div className="card">
              <h2>540</h2>
              <p>Publications</p>
            </div>

            <div className="card">
              <h2>95</h2>
              <p>Collaborations</p>
            </div>

            <div className="card">
              <h2>28</h2>
              <p>Conferences</p>
            </div>

          </div>


          {/* ================= RECENT PUBLICATIONS ================= */}

          <div className="table-box">

            <h2>Recent Publications</h2>

            <table>

              <thead>

                <tr>
                  <th>Title</th>
                  <th>Author</th>
                  <th>Year</th>
                  <th>Status</th>
                </tr>

              </thead>

              <tbody>

                <tr>
                  <td>AI in Healthcare</td>
                  <td>Jhansi Padala</td>
                  <td>2026</td>
                  <td>Published</td>
                </tr>

                <tr>
                  <td>Machine Learning</td>
                  <td>Rahul Kumar</td>
                  <td>2025</td>
                  <td>Under Review</td>
                </tr>

                <tr>
                  <td>Natural Language Processing</td>
                  <td>Priya Sharma</td>
                  <td>2026</td>
                  <td>Published</td>
                </tr>

              </tbody>

            </table>

          </div>


          {/* ================= RECENT ACTIVITIES ================= */}

          <div className="activity">

            <h2>Recent Activities</h2>

            <ul>

              <li>
                ✅ New publication added
              </li>

              <li>
                🤝 Collaboration request received
              </li>

              <li>
                📅 Conference registration completed
              </li>

              <li>
                👨‍🔬 Research profile updated
              </li>

            </ul>

          </div>


        </main>

      </div>

    </div>
  );
}

export default Dashboard;