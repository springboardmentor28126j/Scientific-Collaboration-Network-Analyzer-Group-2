import { Link, useLocation } from "react-router-dom";
import "../styles/sidebar.css";

function Sidebar() {

    const location = useLocation();

    const menuItems = [

        { path: "/", icon: "bi-speedometer2", text: "Dashboard" },
        { path: "/researchers", icon: "bi-people", text: "Researchers" },
        { path: "/papers", icon: "bi-file-earmark-text", text: "Research Papers" },
        { path: "/institutions", icon: "bi-building", text: "Institutions" },
        { path: "/projects", icon: "bi-folder2-open", text: "Projects" },
        { path: "/collaboration-dashboard", icon: "bi-bar-chart", text: "Collaboration Dashboard" },
        { path: "/collaboration-requests", icon: "bi-person-plus", text: "Collaboration Requests" },
        { path: "/institution-requests", icon: "bi-diagram-3", text: "Institution Requests" },
        { path: "/shared-files", icon: "bi-folder", text: "Shared Files" },
        { path: "/progress-updates", icon: "bi-journal-check", text: "Progress Updates" },
        { path: "/notifications", icon: "bi-bell", text: "Notifications" },
        { path: "/timeline", icon: "bi-calendar-event", text: "Timeline" }

    ];

    return (

        <div className="sidebar">

            <div className="sidebar-title">

                <i className="bi bi-diagram-3-fill"></i>

                <span>Scientific Collaboration</span>

            </div>

            <hr />

            {menuItems.map((item) => (

                <Link

                    key={item.path}

                    to={item.path}

                    className={
                        location.pathname === item.path
                            ? "sidebar-link active"
                            : "sidebar-link"
                    }

                >

                    <i className={`bi ${item.icon}`}></i>

                    <span>{item.text}</span>

                </Link>

            ))}

        </div>

    );

}

export default Sidebar;