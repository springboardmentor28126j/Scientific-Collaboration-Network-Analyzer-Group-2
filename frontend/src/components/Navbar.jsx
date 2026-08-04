import { Link, NavLink, useNavigate } from "react-router-dom";

export default function Navbar() {
  const navigate = useNavigate();

  const isLoggedIn = !!localStorage.getItem("access_token");

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    navigate("/login");
  };

  return (
    <nav
      className="navbar navbar-expand-lg navbar-dark bg-primary shadow sticky-top"
      style={{
        paddingTop: "12px",
        paddingBottom: "12px",
      }}
    >
      <div className="container">

        <Link
          className="navbar-brand fw-bold fs-2"
          to="/"
        >
          SCNA
        </Link>

        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbar"
        >
          <span className="navbar-toggler-icon"></span>
        </button>

        <div
          className="collapse navbar-collapse"
          id="navbar"
        >

          <ul className="navbar-nav ms-auto align-items-lg-center">

            <li className="nav-item">
              <NavLink
                className={({ isActive }) =>
                  isActive
                    ? "nav-link active fw-bold"
                    : "nav-link"
                }
                to="/"
              >
                <i className="bi bi-house-door me-1"></i>
                Home
              </NavLink>
            </li>

            {isLoggedIn && (
              <>

                <li className="nav-item">
                  <NavLink
                    className={({ isActive }) =>
                      isActive
                        ? "nav-link active fw-bold"
                        : "nav-link"
                    }
                    to="/researchers"
                  >
                    <i className="bi bi-people me-1"></i>
                    Researchers
                  </NavLink>
                </li>

                <li className="nav-item">
                  <NavLink
                    className={({ isActive }) =>
                      isActive
                        ? "nav-link active fw-bold"
                        : "nav-link"
                    }
                    to="/publications"
                  >
                    <i className="bi bi-journal-text me-1"></i>
                    Publications
                  </NavLink>
                </li>

                {/* NEW CITATIONS MENU */}

                <li className="nav-item">
                  <NavLink
                    className={({ isActive }) =>
                      isActive
                        ? "nav-link active fw-bold"
                        : "nav-link"
                    }
                    to="/citations"
                  >
                    <i className="bi bi-quote me-1"></i>
                    Citations
                  </NavLink>
                </li>

                <li className="nav-item">
                  <NavLink
                    className={({ isActive }) =>
                      isActive
                        ? "nav-link active fw-bold"
                        : "nav-link"
                    }
                    to="/institutions"
                  >
                    <i className="bi bi-bank me-1"></i>
                    Institutions
                  </NavLink>
                </li>

                <li className="nav-item">
                  <NavLink
                    className={({ isActive }) =>
                      isActive
                        ? "nav-link active fw-bold"
                        : "nav-link"
                    }
                    to="/conferences"
                  >
                    <i className="bi bi-calendar-event me-1"></i>
                    Conferences
                  </NavLink>
                </li>

                <li className="nav-item">
                  <NavLink
                    className={({ isActive }) =>
                      isActive
                        ? "nav-link active fw-bold"
                        : "nav-link"
                    }
                    to="/dashboard"
                  >
                    <i className="bi bi-speedometer2 me-1"></i>
                    Dashboard
                  </NavLink>
                </li>
                <li className="nav-item">
                  <NavLink
                    className={({ isActive }) =>
                      isActive
                        ? "nav-link active fw-bold"
                        : "nav-link"
                    }
                    to="/collaborations"
                  >
                    <i className="bi bi-people-fill me-1"></i>
                    Collaboration
                  </NavLink>
                </li>

                <li className="nav-item ms-lg-2">
                  <NavLink
                    to="/notifications"
                    className="btn btn-outline-light rounded-circle position-relative"
                  >
                    <i className="bi bi-bell"></i>

                    <span className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
                      0
                    </span>
                  </NavLink>
                </li>

                <li className="nav-item ms-lg-2">
                  <button
                    className="btn btn-outline-light rounded-circle"
                  >
                    <i className="bi bi-search"></i>
                  </button>
                </li>

                <li className="nav-item dropdown ms-lg-3">

                  <a
                    className="nav-link dropdown-toggle"
                    href="#"
                    role="button"
                    data-bs-toggle="dropdown"
                  >
                    <i className="bi bi-person-circle fs-5"></i>
                  </a>

                  <ul className="dropdown-menu dropdown-menu-end shadow">

                    <li>
                      <Link
                        className="dropdown-item"
                        to="/profile"
                      >
                        <i className="bi bi-person me-2"></i>
                        My Profile
                      </Link>
                    </li>

                    <li>
                      <Link
                        className="dropdown-item"
                        to="/settings"
                      >
                        <i className="bi bi-gear me-2"></i>
                        Settings
                      </Link>
                    </li>

                    <li>
                      <hr className="dropdown-divider" />
                    </li>

                    <li>
                      <button
                        className="dropdown-item text-danger"
                        onClick={logout}
                      >
                        <i className="bi bi-box-arrow-right me-2"></i>
                        Logout
                      </button>
                    </li>

                  </ul>

                </li>

              </>
            )}

            {!isLoggedIn && (
              <li className="nav-item ms-lg-3">

                <Link
                  className="btn btn-light"
                  to="/login"
                >
                  Login
                </Link>

              </li>
            )}

          </ul>

        </div>

      </div>
    </nav>
  );
}
