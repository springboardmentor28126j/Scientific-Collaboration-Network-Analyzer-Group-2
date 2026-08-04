import api from "../api/api";

export const getDashboardStats = async () => {
  const response = await api.get("/dashboard/stats");
  return response.data;
};

export const getPublicationsPerYear = async () => {
  const response = await api.get("/dashboard/publications-per-year");
  return response.data;
};

export const getPublicationTypes = async () => {
  const response = await api.get("/dashboard/publication-types");
  return response.data;
};
