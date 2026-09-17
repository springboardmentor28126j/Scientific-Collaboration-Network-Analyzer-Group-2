import "../css/dashboard.css";

function Dashboard() {
  return (
    <div className="dashboard-container">

      {/* Top Navbar */}
      <header className="topbar">
        <div className="logo">
          🔬 SciCollab
        </div>

        <div className="top-links">
          <a href="#">Dashboard</a>
          <a href="#">Researchers</a>
          <a href="#">Publications</a>
          <a href="#">Collaborations</a>
          <a href="#">Profile</a>
          <button className="logout-btn">Logout</button>
        </div>
      </header>

      <div className="dashboard-body">

        {/* Sidebar */}
        <aside className="sidebar">

          <h3>Menu</h3>

          <ul>
            <li>🏠 Dashboard</li>
            <li>👨‍🔬 Researchers</li>
            <li>📄 Publications</li>
            <li>🤝 Collaborations</li>
            <li>📅 Conferences</li>
            <li>📊 Analytics</li>
            <li>⚙ Settings</li>
          </ul>

        </aside>

        {/* Main Content */}
        <main className="content">

          <h1>Welcome Back 👋</h1>

          <p>
            Monitor your publications, collaborations, researchers,
            and conferences from one place.
          </p>

          {/* Statistics */}
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

          {/* Publications */}
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

          {/* Activities */}
          <div className="activity">

            <h2>Recent Activities</h2>

            <ul>
              <li>✅ New publication added</li>
              <li>🤝 Collaboration request received</li>
              <li>📅 Conference registration completed</li>
              <li>👨‍🔬 Research profile updated</li>
            </ul>

          </div>

        </main>

      </div>

    </div>
  );
}

export default Dashboard;