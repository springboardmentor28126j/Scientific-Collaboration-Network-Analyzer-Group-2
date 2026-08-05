// src/services/dashboardService.js

export const getDashboardData = async() => {
    try {
        const response = await fetch("http://127.0.0.1:8000/api/v1/network/stats");
        if (!response.ok) {
            throw new Error("Network response was not ok");
        }
        return await response.json();
    } catch (error) {
        console.error("Error fetching dashboard data:", error);
        return {};
    }
};