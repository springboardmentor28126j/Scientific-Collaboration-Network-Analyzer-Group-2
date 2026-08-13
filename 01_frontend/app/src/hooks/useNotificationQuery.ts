import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { 
  getNotifications, 
  getUnreadNotificationCount, 
  markNotificationRead 
} from "@/api/notification";
import { toast } from "sonner";

export function useNotifications() {
  return useQuery({
    queryKey: ["notifications"],
    queryFn: getNotifications,
    refetchInterval: 30000, // Refetch every 30 seconds to simulate real-time updates
  });
}

export function useUnreadNotificationCount() {
  return useQuery({
    queryKey: ["notifications-unread-count"],
    queryFn: getUnreadNotificationCount,
    refetchInterval: 30000,
  });
}

export function useMarkNotificationRead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (notificationId: string) => markNotificationRead(notificationId),
    onSuccess: () => {
      // Refresh both the notification list and the unread count
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      queryClient.invalidateQueries({ queryKey: ["notifications-unread-count"] });
    },
    onError: (error: Error) => {
      console.error("Failed to mark notification as read:", error);
      toast.error("Could not mark notification as read");
    },
  });
}
