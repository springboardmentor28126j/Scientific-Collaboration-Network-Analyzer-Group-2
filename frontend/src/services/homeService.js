import api from "../api/api";

export const getHomeData = async () => {
  const response = await api.get("/home");
  return response.data;
};
