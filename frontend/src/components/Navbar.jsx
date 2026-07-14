import { Link, useNavigate } from "react-router-dom";
import "../styles/navbar.css";

function Navbar() {

    const navigate = useNavigate();

    const user = localStorage.getItem("user");
    const role = localStorage.getItem("role");

    const logout = () => {
        localStorage.clear();
        navigate("/login");
    };

    return (

        <header className="navbar">

            <div className="navbar-left">

                <div className="logo">
                    🔬
                </div>

                <div>

                    <h2>
                        Scientific Collaboration
                    </h2>

                    <span>
                        Network Analyzer
                    </span>

                </div>

            </div>

            <div className="navbar-right">

                <div className="status">

                    <span className="dot"></span>

                    System Online

                </div>

                {user && (

                    <div className="user-box">

                        <div className="avatar">
                            {user.charAt(0).toUpperCase()}
                        </div>

                        <div>

                            <p>
                                Welcome
                            </p>

                            <h4>
                                {user}
                            </h4>

                        </div>

                    </div>

                )}

                {user && (

                    <button
                        className="logout"
                        onClick={logout}
                    >
                        Logout
                    </button>

                )}

                {!user && (

                    <>
                       <div className="auth-buttons">

    <Link
        to="/login"
        className="login-btn"
    >
        Login
    </Link>

    <Link
        to="/register"
        className="register-btn"
    >
        Register
    </Link>

</div>
                    </>

                )}

            </div>

        </header>

    );

}

export default Navbar;