import { useNavigate } from "react-router-dom";
import "../styles/dashboardNavbar.css";

function DashboardNavbar() {

    const navigate = useNavigate();

    const user = localStorage.getItem("user");

    const logout = () => {

        localStorage.clear();

        navigate("/login");

    };

    return (

        <header className="dashboard-navbar">

            <div className="dashboard-logo">

                🔬

                <div>

                    <h2>Scientific Collaboration</h2>

                    <span>Network Analyzer</span>

                </div>

            </div>

            <div className="dashboard-right">

                <div className="online-status">

                    <span className="online-dot"></span>

                    Online

                </div>
                <button
    className="audit-nav-btn"
    onClick={() => navigate("/audit-logs")}
>
    Audit Logs
</button>

                <div className="profile-box">

                    <div className="profile-avatar">

                        {user ? user.charAt(0).toUpperCase() : "U"}

                    </div>

                    <div>

                        <small>Welcome</small>

                        <h4>{user}</h4>

                    </div>

                </div>

                <button
                    className="logout-btn-nav"
                    onClick={logout}
                >
                    Logout
                </button>

            </div>

        </header>

    );

}

export default DashboardNavbar;