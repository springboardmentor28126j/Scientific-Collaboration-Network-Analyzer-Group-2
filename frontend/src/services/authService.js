const API_URL = "http://localhost:8000/auth";

export const register = async(userData) => {
    const payload = {
        email: userData.email,
        password: userData.password,
        role: userData.role || "RESEARCHER"
    };

    const response = await fetch(`${API_URL}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });

    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.detail || "Registration failed");
    }
    return data;
};

export const login = async(credentials) => {
    const response = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(credentials),
    });

    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.detail || "Invalid Email or Password");
    }
    return data;
};