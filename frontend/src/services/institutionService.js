import api from "../api/api";

// Get all institutions
export const getInstitutions = async () => {
  const res = await api.get("/institutions");
  return res.data;
};

// Get one institution
export const getInstitution = async (id) => {
  const res = await api.get(`/institutions/${id}`);
  return res.data;
};

// Create institution
export const createInstitution = async (data) => {
  const res = await api.post("/institutions", data);
  return res.data;
};

// Update institution
export const updateInstitution = async (id, data) => {
  const res = await api.put(`/institutions/${id}`, data);
  return res.data;
};

// Delete institution
export const deleteInstitution = async (id) => {
  const res = await api.delete(`/institutions/${id}`);
  return res.data;
};
