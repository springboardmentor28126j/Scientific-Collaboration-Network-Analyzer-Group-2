// ==========================================
// API CONFIGURATION
// Scientific Collaboration Network Analyzer
// ==========================================

// Local FastAPI Server
const API_URL = "http://127.0.0.1:8000";

// ===============================
// Authentication Endpoints
// ===============================

const LOGIN_API = API_URL + "/users/login";
const REGISTER_API = API_URL + "/users/register";

// ===============================
// Researchers
// ===============================

const RESEARCHERS_API = API_URL + "/researchers";

// ===============================
// Institutions
// ===============================

const INSTITUTIONS_API = API_URL + "/institutions";

// ===============================
// Publications
// ===============================

const PUBLICATIONS_API = API_URL + "/publications";

// ===============================
// Conferences
// ===============================

const CONFERENCES_API = API_URL + "/conferences";

const COLLABORATIONS_API = API_URL + "/collaborations";
const DASHBOARD_API = API_URL + "/dashboard/";
const CITATIONS_API = API_URL + "/citations/";
const PROJECTS_API = API_URL + "/projects/";

// ===============================
// File Upload
// ===============================

const FILE_UPLOAD_API = API_URL + "/upload";

// ===================================
// Authorization Header
// ===================================

function getAuthHeaders() {

    const token = localStorage.getItem("token");

    return {

        "Content-Type": "application/json",

        "Authorization": "Bearer " + token

    };

}

// ===================================
// GET Request
// ===================================

async function apiGet(url) {

    const response = await fetch(url, {

        method: "GET",

        headers: getAuthHeaders()

    });

    return response;

}

// ===================================
// POST Request
// ===================================

async function apiPost(url, data) {

    const response = await fetch(url, {

        method: "POST",

        headers: getAuthHeaders(),

        body: JSON.stringify(data)

    });

    return response;

}

// ===================================
// PUT Request
// ===================================

async function apiPut(url, data) {

    const response = await fetch(url, {

        method: "PUT",

        headers: getAuthHeaders(),

        body: JSON.stringify(data)

    });

    return response;

}

// ===================================
// DELETE Request
// ===================================

async function apiDelete(url) {

    const response = await fetch(url, {

        method: "DELETE",

        headers: getAuthHeaders()

    });

    return response;

}

// ===================================
// Logout
// ===================================

function logout() {

    localStorage.removeItem("token");

    localStorage.removeItem("username");

    localStorage.removeItem("role");

    window.location.href = "../index.html";

}
