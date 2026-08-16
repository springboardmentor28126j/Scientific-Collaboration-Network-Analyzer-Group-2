import {
  Link,
  NavLink,
  useNavigate,
} from "react-router-dom";

import {
  useEffect,
  useState,
} from "react";

import {
  Bell,
  Search,
  UserCircle,
} from "lucide-react";
import { getMyResearcherProfile } from "../services/researcherService";
export default function Navbar() {
  const navigate = useNavigate();

  const isLoggedIn =
    !!localStorage.getItem("access_token") ||
    !!sessionStorage.getItem("access_token");
  // Get the currently logged-in user
  const [currentUser, setCurrentUser] = useState(() => {
    try {
      const storedUser =
        localStorage.getItem("user") ||
        sessionStorage.getItem("user");

      return storedUser ? JSON.parse(storedUser) : null;
    } catch (error) {
      console.error("Unable to read logged-in user:", error);
      return null;
    }
  });

  const [researcherProfile, setResearcherProfile] = useState(null);

  // Notification state
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");

    sessionStorage.removeItem("access_token");
    sessionStorage.removeItem("user");

    setCurrentUser(null);
    setNotifications([]);
    setUnreadCount(0);

    navigate("/login");
  };

  /*
   * Keep the user information synchronized with localStorage.
   * This is useful when the user logs in without a full page refresh.
   */
  useEffect(() => {
    const updateUser = () => {
      try {
        const storedUser =
          localStorage.getItem("user") ||
          sessionStorage.getItem("user");

        setCurrentUser(
          storedUser ? JSON.parse(storedUser) : null
        );
      } catch (error) {
        console.error(
          "Unable to read logged-in user:",
          error
        );
        setCurrentUser(null);
      }
    };

    window.addEventListener("storage", updateUser);

    return () => {
      window.removeEventListener("storage", updateUser);
    };
  }, []);


  useEffect(() => {
    const loadResearcherProfile = async () => {
      if (!isLoggedIn) {
        setResearcherProfile(null);
        return;
      }

      try {
        const profile = await getMyResearcherProfile();
        setResearcherProfile(profile);
      } catch (error) {
        console.error(
          "Unable to load researcher profile:",
          error
        );
      }
    };

    loadResearcherProfile();
  }, [isLoggedIn]);

  /*
   * Real-time notifications using WebSocket
   */
  useEffect(() => {
    if (!isLoggedIn || !currentUser?.id) {
      return;
    }

    const socket = new WebSocket(
      `ws://127.0.0.1:8000/notifications/ws?user_id=${currentUser.id}`
    );

    socket.onopen = () => {
      console.log("Notification WebSocket connected.");
    };

    socket.onmessage = (event) => {
      try {
        const notification = JSON.parse(event.data);

        setNotifications((previous) => [
          notification,
          ...previous,
        ]);

        setUnreadCount((previous) => previous + 1);
      } catch (error) {
        console.error(
          "Unable to process notification:",
          error
        );
      }
    };

    socket.onerror = (error) => {
      console.error(
        "Notification WebSocket error:",
        error
      );
    };

    socket.onclose = () => {
      console.log("Notification WebSocket disconnected.");
    };

    return () => {
      socket.close();
    };
  }, [isLoggedIn, currentUser?.id]);

  return (
    <nav
      className="navbar navbar-expand-lg navbar-dark bg-primary shadow sticky-top"
      style={{
        paddingTop: "12px",
        paddingBottom: "12px",
      }}
    >
      <div className="container-fluid px-4">

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

                {/* ================= NOTIFICATIONS ================= */}
                <li className="nav-item ms-lg-2">
                  <NavLink
                    to="/notifications"
                    className="nav-link position-relative"
                    title="Notifications"
                    style={{
                      fontSize: "22px",
                      padding: "8px 12px",
                      color: "white",
                    }}
                  >
                    <Bell size={22} />

                    {unreadCount > 0 && (
                      <span
                        className="position-absolute badge rounded-pill bg-danger"
                        style={{
                          top: "0px",
                          right: "0px",
                          fontSize: "10px",
                        }}
                      >
                        {unreadCount}
                      </span>
                    )}
                  </NavLink>
                </li>

                {/* ================= SEARCH ================= */}
                <li className="nav-item ms-lg-2">
                  <button
                    type="button"
                    onClick={() => navigate("/search")}
                    title="Search"
                    style={{
                      background: "none",
                      border: "none",
                      color: "white",
                      fontSize: "22px",
                      padding: "8px 12px",
                      cursor: "pointer",
                    }}
                  >
                    <Search size={22} />
                  </button>
                </li>

                {/* User menu */}
                <li className="nav-item dropdown ms-lg-3">
                  <a
                    className="nav-link dropdown-toggle"
                    href="#"
                    role="button"
                    data-bs-toggle="dropdown"
                    onClick={(event) =>
                      event.preventDefault()
                    }
                  >
                    <UserCircle size={22} className="me-1" />

                    <span>
                      {researcherProfile
                        ? `${researcherProfile.first_name || ""} ${researcherProfile.last_name || ""}`.trim()
                        : currentUser?.email || "User"}
                    </span>
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