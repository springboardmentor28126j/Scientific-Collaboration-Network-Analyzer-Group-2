// ======================================
// Authentication
// Scientific Collaboration Network Analyzer
// ======================================

// ------------------------------
// Login
// ------------------------------

const loginForm = document.getElementById("loginForm");

if (loginForm) {

    loginForm.addEventListener("submit", loginUser);

}

async function loginUser(event) {

    event.preventDefault();

    const email = document.getElementById("email").value.trim();

    const password = document.getElementById("password").value.trim();

    const messageBox = document.getElementById("messageBox");

    const loginBtn = document.getElementById("loginBtn");

    loginBtn.disabled = true;

    loginBtn.innerHTML = "Logging in...";

    try {

        const response = await fetch(LOGIN_API, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                email: email,

                password: password

            })

        });

        const data = await response.json();

        if (response.ok) {

            localStorage.setItem("token", data.access_token || data.token);

            localStorage.setItem("username", data.name || email);

            localStorage.setItem("role", data.role || "");

            messageBox.className = "alert alert-success";

            messageBox.classList.remove("d-none");

            messageBox.innerHTML = "Login Successful.";

            setTimeout(() => {

                window.location.href = "dashboard.html";

            }, 1000);

        }

        else {

            messageBox.className = "alert alert-danger";

            messageBox.classList.remove("d-none");

            messageBox.innerHTML = data.detail || "Invalid Email or Password.";

        }

    }

    catch (error) {

        console.log(error);

        messageBox.className = "alert alert-danger";

        messageBox.classList.remove("d-none");

        messageBox.innerHTML = "Unable to connect to server.";

    }

    loginBtn.disabled = false;

    loginBtn.innerHTML = '<i class="bi bi-box-arrow-in-right"></i> Login';

}

// ------------------------------
// Register
// ------------------------------

const registerForm = document.getElementById("registerForm");

if (registerForm) {

    registerForm.addEventListener("submit", registerUser);

}

async function registerUser(event) {

    event.preventDefault();

    const name = document.getElementById("name").value.trim();

    const email = document.getElementById("registerEmail").value.trim();

    const password = document.getElementById("registerPassword").value.trim();

    const role = document.getElementById("role").value;

    const messageBox = document.getElementById("registerMessage");

    try {

        const response = await fetch(REGISTER_API, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                name: name,

                email: email,

                password: password,

                role: role

            })

        });

        const data = await response.json();

        if (response.ok) {

            messageBox.className = "alert alert-success";

            messageBox.classList.remove("d-none");

            messageBox.innerHTML = "Registration Successful. Redirecting to Login...";

            registerForm.reset();

            setTimeout(() => {

                window.location.href = "index.html";

            }, 1500);

        }

        else {

            messageBox.className = "alert alert-danger";

            messageBox.classList.remove("d-none");

            messageBox.innerHTML = data.detail || "Registration Failed.";

        }

    }

    catch (error) {

        console.log(error);

        messageBox.className = "alert alert-danger";

        messageBox.classList.remove("d-none");

        messageBox.innerHTML = "Unable to connect to server.";

    }

}

// ------------------------------
// Authentication Check
// ------------------------------

function checkLogin() {

    const token = localStorage.getItem("token");

    if (!token) {

        window.location.href = "index.html";

    }

}

// ------------------------------
// Logout
// ------------------------------

function logout() {

    localStorage.clear();

    window.location.href = "index.html";

}