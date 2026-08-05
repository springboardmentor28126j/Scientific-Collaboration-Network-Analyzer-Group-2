import { Link } from "react-router-dom";

function InstitutionSidebar() {

    return (

        <div
            style={{
                width: "250px",
                minHeight: "100vh",
                background: "#0f766e",
                color: "white",
                padding: "20px"
            }}
        >

            <h2 style={{ marginBottom: "30px" }}>
                🏛 Institution
            </h2>

            <ul
                style={{
                    listStyle: "none",
                    padding: 0
                }}
            >

                <li style={{ marginBottom: "18px" }}>
                    <Link
                        to="/institution-dashboard"
                        style={{
                            color: "white",
                            textDecoration: "none"
                        }}
                    >
                        🏠 Dashboard
                    </Link>
                </li>

                <li style={{ marginBottom: "18px" }}>
                    <Link
                        to="/institution-profile"
                        style={{
                            color: "white",
                            textDecoration: "none"
                        }}
                    >
                        🏛 Institution Profile
                    </Link>
                </li>

                <li style={{ marginBottom: "18px" }}>
                    <Link
                        to="/institution-researchers"
                        style={{
                            color: "white",
                            textDecoration: "none"
                        }}
                    >
                        👨‍🔬 Researchers
                    </Link>
                </li>

                <li style={{ marginBottom: "18px" }}>
                    <Link
                        to="/institution-papers"
                        style={{
                            color: "white",
                            textDecoration: "none"
                        }}
                    >
                        📄 Research Papers
                    </Link>
                </li>

                <li style={{ marginBottom: "18px" }}>
                    <Link
                        to="/institution-collaboration"
                        style={{
                            color: "white",
                            textDecoration: "none"
                        }}
                    >
                        🤝 Institution Collaboration
                    </Link>
                </li>

                <li style={{ marginBottom: "18px" }}>
                    <Link
                        to="/institution-requests"
                        style={{
                            color: "white",
                            textDecoration: "none"
                        }}
                    >
                        📥 Collaboration Requests
                    </Link>
                </li>

                <li style={{ marginBottom: "18px" }}>
                    <Link
                        to="/citations"
                        style={{
                            color: "white",
                            textDecoration: "none"
                        }}
                    >
                        📚 Citation Management
                    </Link>
                </li>

                <li style={{ marginBottom: "18px" }}>
                    <Link
                        to="/institution-analytics"
                        style={{
                            color: "white",
                            textDecoration: "none"
                        }}
                    >
                        📊 Analytics
                    </Link>
                </li>

                <li style={{ marginBottom: "18px" }}>
                    <Link
                        to="/institution-settings"
                        style={{
                            color: "white",
                            textDecoration: "none"
                        }}
                    >
                        ⚙ Settings
                    </Link>
                </li>

                <li style={{ marginTop: "40px" }}>
                    <Link
                        to="/login"
                        style={{
                            color: "#ffb4b4",
                            textDecoration: "none"
                        }}
                        onClick={() => {

                            localStorage.clear();

                        }}
                    >
                        🚪 Logout
                    </Link>
                </li>

            </ul>

        </div>

    );

}

export default InstitutionSidebar;