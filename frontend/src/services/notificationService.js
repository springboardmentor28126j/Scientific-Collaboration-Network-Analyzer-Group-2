import api from "./api";

// Get logged-in user's notifications
export const getNotifications = async () => {
  const response = await api.get("/notifications/me");
  return response.data;
};

// Mark notification as read
export const markAsRead = async (id) => {
  const response = await api.put(`/notifications/${id}/read`);
  return response.data;
};

// Delete notification
export const deleteNotification = async (id) => {
  const response = await api.delete(`/notifications/${id}`);
  return response.data;
};