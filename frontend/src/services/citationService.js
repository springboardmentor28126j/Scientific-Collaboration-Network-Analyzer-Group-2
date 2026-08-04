import api from "./api";

export const getCitations = async () => {
  const response = await api.get("/citations");
  return response.data;
};

export const getCitation = async (id) => {
  const response = await api.get(`/citations/${id}`);
  return response.data;
};

export const getPublicationCitations = async (publicationId) => {
  const response = await api.get(
    `/citations/publication/${publicationId}`
  );
  return response.data;
};

export const createCitation = async (data) => {
  const response = await api.post(
    "/citations",
    data
  );
  return response.data;
};

export const updateCitation = async (
  id,
  data
) => {
  const response = await api.put(
    `/citations/${id}`,
    data
  );
  return response.data;
};

export const deleteCitation = async (
  id
) => {
  const response = await api.delete(
    `/citations/${id}`
  );
  return response.data;
};

export const exportBibtex = async (
  id
) => {
  const response = await api.get(
    `/citations/${id}/bibtex`,
    {
      responseType: "text",
    }
  );

  return response.data;
};
