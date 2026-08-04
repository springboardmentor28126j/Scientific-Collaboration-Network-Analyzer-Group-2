import api from "../api/api";

export const getResearchers = async () => {
    const response = await api.get("/researchers/");
    return response.data;
};

export const getResearcher = async (id) => {
    const response = await api.get(`/researchers/${id}`);
    return response.data;
};

export const createResearcher = async (data) => {
    const response = await api.post("/researchers/", data);
    return response.data;
};

export const updateResearcher = async (id, data) => {
    const response = await api.put(`/researchers/${id}`, data);
    return response.data;
};

export const deleteResearcher = async (id) => {
    const response = await api.delete(`/researchers/${id}`);
    return response.data;
};
