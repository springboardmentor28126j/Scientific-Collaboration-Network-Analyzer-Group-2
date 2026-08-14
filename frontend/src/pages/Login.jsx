import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import api from "../services/api";

import "../styles/login.css";

function Login() {
  const navigate = useNavigate();

  // ==============================
  // LOGIN STATE
  // ==============================

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  // ==============================
  // CAPTCHA STATE
  // ==============================

  const [captchaId, setCaptchaId] = useState("");
  const [captchaImage, setCaptchaImage] = useState("");
  const [captchaInput, setCaptchaInput] = useState("");

  // ==============================
  // UI STATE
  // ==============================

  const [message, setMessage] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  // ==============================
  // LOAD CAPTCHA FROM BACKEND
  // ==============================

  const loadCaptcha = async () => {
    try {
      setMessage("");

      const response = await api.get("/auth/captcha");

      console.log("CAPTCHA RESPONSE:", response.data);

      setCaptchaId(response.data.captcha_id);
      setCaptchaImage(response.data.captcha_image);
      setCaptchaInput("");

    } catch (error) {
      console.error(
        "CAPTCHA LOAD ERROR:",
        error.response?.data || error
      );

      setMessage(
        "Unable to load CAPTCHA. Please refresh the page."
      );
    }
  };

  // ==============================
  // LOAD CAPTCHA WHEN PAGE OPENS
  // ==============================

  useEffect(() => {
    loadCaptcha();
  }, []);

  // ==============================
  // LOGIN
  // ==============================

  const handleLogin = async (e) => {
    e.preventDefault();

    setMessage("");

    // Prevent multiple requests
    if (loading) {
      return;
    }

    // ==============================
    // BASIC VALIDATION
    // ==============================

    if (!email.trim()) {
      setMessage("Please enter your email.");
      return;
    }

    if (!password) {
      setMessage("Please enter your password.");
      return;
    }

    if (!captchaInput.trim()) {
      setMessage("Please enter the CAPTCHA.");
      return;
    }

    if (!captchaId) {
      setMessage(
        "CAPTCHA is not available. Please refresh the CAPTCHA."
      );
      return;
    }

    try {
      setLoading(true);

      // ==============================
      // SEND LOGIN REQUEST
      // ==============================

      const loginData = {
        email: email.trim(),
        password: password,
        captcha_id: captchaId,
        captcha_answer: captchaInput
          .trim()
          .toUpperCase(),
      };

      console.log("LOGIN REQUEST:", {
        email: loginData.email,
        captcha_id: loginData.captcha_id,
        captcha_answer: loginData.captcha_answer,
      });

      const response = await api.post(
        "/auth/login",
        loginData
      );

      console.log(
        "LOGIN RESPONSE:",
        response.data
      );

      // ==============================
      // SAVE LOGIN INFORMATION
      // ==============================

      localStorage.setItem(
        "token",
        response.data.access_token
      );

      localStorage.setItem(
        "user",
        response.data.full_name
      );

      localStorage.setItem(
        "role",
        response.data.role
      );

      localStorage.setItem(
        "username",
        response.data.username
      );

      // ==============================
      // SUCCESS MESSAGE
      // ==============================

      setMessage("Login Successful");

      // ==============================
      // NAVIGATION
      // ==============================

      setTimeout(() => {
        if (response.data.role === "Researcher") {
          navigate("/researcher-dashboard");
        } else {
          navigate("/institution-dashboard");
        }
      }, 800);

    } catch (error) {
      console.error(
        "LOGIN ERROR:",
        error.response?.data || error
      );

      // ==============================
      // SHOW BACKEND ERROR
      // ==============================

      const errorMessage =
        error.response?.data?.detail ||
        "Invalid email or password.";

      setMessage(errorMessage);

      // ==============================
      // CAPTCHA IS ONE-TIME USE
      // ==============================

      await loadCaptcha();

    } finally {
      setLoading(false);
    }
  };

  // ==============================
  // JSX
  // ==============================

  return (
    <>
      <Navbar />

      <main className="login-page">

        <div className="login-card">

          {/* ==========================
              HEADER
          ========================== */}

          <div className="login-heading">

            <h1>
              Login
            </h1>

            <p>
              Sign in to your research collaboration
              <br />
              account.
            </p>

          </div>


          {/* ==========================
              LOGIN FORM
          ========================== */}

          <form onSubmit={handleLogin}>

            {/* ========================
                EMAIL
            ======================== */}

            <div className="form-group">

              <label htmlFor="email">
                Email
              </label>

              <div className="input-wrapper">

                <span className="input-icon">
                  ✉
                </span>

                <input
                  id="email"
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) =>
                    setEmail(e.target.value)
                  }
                  autoComplete="email"
                  required
                />

              </div>

            </div>


            {/* ========================
                PASSWORD
            ======================== */}

            <div className="form-group">

              <label htmlFor="password">
                Password
              </label>

              <div className="input-wrapper">

                <span className="input-icon">
                  🔒
                </span>

                <input
                  id="password"
                  type={
                    showPassword
                      ? "text"
                      : "password"
                  }
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) =>
                    setPassword(e.target.value)
                  }
                  autoComplete="current-password"
                  required
                />

                <button
                  type="button"
                  className="password-toggle"
                  onClick={() =>
                    setShowPassword(
                      !showPassword
                    )
                  }
                  aria-label={
                    showPassword
                      ? "Hide password"
                      : "Show password"
                  }
                >
                  {showPassword ? "◉" : "◌"}
                </button>

              </div>

            </div>


            {/* ========================
                CAPTCHA
            ======================== */}

            <div className="form-group captcha-section">

              <label>
                Human Verification
              </label>


              {/* CAPTCHA IMAGE + REFRESH */}

              <div className="captcha-row">

                {/* Backend CAPTCHA */}

                <div className="captcha-box">

                  {captchaImage ? (
                    <div
                      dangerouslySetInnerHTML={{
                        __html: captchaImage,
                      }}
                    />
                  ) : (
                    <span>
                      Loading CAPTCHA...
                    </span>
                  )}

                </div>


                {/* REFRESH BUTTON */}

                <button
                  type="button"
                  className="captcha-refresh"
                  onClick={loadCaptcha}
                  title="Generate new CAPTCHA"
                  disabled={loading}
                >

                  <span className="refresh-icon">
                    ↻
                  </span>

                  <span>
                    Refresh
                  </span>

                </button>

              </div>


              {/* ======================
                  CAPTCHA INPUT
              ====================== */}

              <div className="captcha-input-row">

                <div className="input-wrapper captcha-input-wrapper">

                  <span className="input-icon">
                    ✓
                  </span>

                  <input
                    type="text"
                    placeholder="Enter CAPTCHA"
                    value={captchaInput}
                    onChange={(e) =>
                      setCaptchaInput(
                        e.target.value.toUpperCase()
                      )
                    }
                    maxLength={5}
                    autoComplete="off"
                    required
                  />

                </div>

                <span className="captcha-help">
                  Enter the 5 characters above
                </span>

              </div>

            </div>


            {/* ========================
                MESSAGE
            ======================== */}

            {message && (

              <div
                className={
                  message === "Login Successful"
                    ? "login-message success"
                    : "login-message error"
                }
              >
                {message}
              </div>

            )}


            {/* ========================
                LOGIN BUTTON
            ======================== */}

            <button
              type="submit"
              className="login-submit"
              disabled={loading}
            >

              {loading
                ? "Logging in..."
                : "Login"}

            </button>

          </form>


          {/* ==========================
              REGISTER SECTION
          ========================== */}

          <div className="register-section">

            <span>
              Don't have an account?
            </span>

            <button
              type="button"
              onClick={() =>
                navigate("/register")
              }
            >
              Register here
            </button>

          </div>

        </div>

      </main>

      <Footer />
    </>
  );
}

export default Login;