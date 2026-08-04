import api from "../api/api";

// Get all publications
export const getPublications = async () => {
  const response = await api.get("/publications/");
  return response.data;
};

// Get one publication
export const getPublication = async (id) => {
  const response = await api.get(`/publications/${id}`);
  return response.data;
};

// Create publication
export const createPublication = async (data) => {
  const response = await api.post("/publications/", data);
  return response.data;
};

// Update publication
export const updatePublication = async (id, data) => {
  const response = await api.put(`/publications/${id}`, data);
  return response.data;
};

// Delete publication
export const deletePublication = async (id) => {
  const response = await api.delete(`/publications/${id}`);
  return response.data;
};

// Upload PDF
export const uploadPublication = async (id, file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post(
    `/publications/${id}/upload`,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return response.data;
};

// Download PDF
export const downloadPublication = async (id) => {
  const response = await api.get(
    `/publications/${id}/download`,
    {
      responseType: "blob",
    }
  );

  return response;
};
