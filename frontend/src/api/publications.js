import axiosClient from "./axiosClient";

export const getPublications = () => axiosClient.get("/publications/");
export const createPublication = (data) => axiosClient.post("/publications/", data);
export const updatePublication = (id, data) => axiosClient.put(`/publications/${id}`, data);
export const deletePublication = (id) => axiosClient.delete(`/publications/${id}`);
