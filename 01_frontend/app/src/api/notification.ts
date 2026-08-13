import { API_BASE_URL, getHeaders, handleResponse } from "./core";

export type NotificationType = 
  | "COAUTHOR_ADDED" 
  | "PUBLICATION_PUBLISHED" 
  | "REVIEW_ASSIGNED" 
  | "CONFERENCE_CREATED";

export interface NotificationRead {
  id: string;
  notification_type: NotificationType;
  title: string;
  message: string;
  publication_id: string;
  is_read: boolean;
  created_at: string;
}

export async function getNotifications(): Promise<NotificationRead[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/notifications`, {
    headers: getHeaders(),
  });
  return handleResponse<NotificationRead[]>(response);
}

export async function getUnreadNotificationCount(): Promise<number> {
  const response = await fetch(`${API_BASE_URL}/api/v1/notifications/unread-count`, {
    headers: getHeaders(),
  });
  return handleResponse<number>(response);
}

export async function markNotificationRead(notificationId: string): Promise<NotificationRead> {
  const response = await fetch(`${API_BASE_URL}/api/v1/notifications/${notificationId}/read`, {
    method: "PATCH",
    headers: getHeaders(),
  });
  return handleResponse<NotificationRead>(response);
}
