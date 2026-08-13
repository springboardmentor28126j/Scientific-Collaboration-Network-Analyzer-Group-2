import { useState } from "react";
import { useNavigate } from "react-router";
import { Bell, Loader2 } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  useNotifications, 
  useUnreadNotificationCount, 
  useMarkNotificationRead 
} from "@/hooks/useNotificationQuery";
import type { NotificationRead } from "@/api/notification";
import { cn } from "@/lib/utils";

export function NotificationBell() {
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  
  const { data: notifications, isLoading } = useNotifications();
  const { data: unreadCount = 0 } = useUnreadNotificationCount();
  const markAsRead = useMarkNotificationRead();

  const handleNotificationClick = (notification: NotificationRead) => {
    // Optimistically mark as read if it isn't already
    if (!notification.is_read) {
      markAsRead.mutate(notification.id);
    }
    
    // Close the popover
    setOpen(false);

    // Route based on type
    switch (notification.notification_type) {
      case "PUBLICATION_PUBLISHED":
        navigate(`/dashboard/catalog/${notification.publication_id}`);
        break;
      case "REVIEW_ASSIGNED":
        navigate(`/dashboard/reviews`);
        break;
      case "COAUTHOR_ADDED":
      case "CONFERENCE_CREATED":
      default:
        navigate(`/dashboard/publications/${notification.publication_id}`);
        break;
    }
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="icon" className="relative text-slate-600 hover:bg-slate-100 hover:text-slate-900 rounded-full">
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <span className="absolute top-0 right-0 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white ring-2 ring-white">
              {unreadCount > 99 ? "99+" : unreadCount}
            </span>
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80 p-0 mr-4 mt-2" align="end">
        <div className="flex items-center justify-between px-4 py-3 border-b">
          <h4 className="font-semibold text-slate-900">Notifications</h4>
          {unreadCount > 0 && (
            <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full">
              {unreadCount} unread
            </span>
          )}
        </div>
        
        <ScrollArea className="h-80">
          {isLoading ? (
            <div className="flex justify-center items-center h-32 text-slate-400">
              <Loader2 className="h-5 w-5 animate-spin" />
            </div>
          ) : !notifications || notifications.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-32 text-slate-500">
              <Bell className="h-8 w-8 text-slate-200 mb-2" />
              <p className="text-sm">No notifications yet.</p>
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {notifications.map((notification) => (
                <button
                  key={notification.id}
                  onClick={() => handleNotificationClick(notification)}
                  className={cn(
                    "w-full text-left p-4 hover:bg-slate-50 transition-colors flex items-start gap-3",
                    !notification.is_read ? "bg-blue-50/50" : ""
                  )}
                >
                  <div className="flex-1 space-y-1">
                    <p className={cn(
                      "text-sm font-medium leading-snug",
                      !notification.is_read ? "text-slate-900" : "text-slate-700"
                    )}>
                      {notification.title}
                    </p>
                    <p className="text-xs text-slate-600 line-clamp-2">
                      {notification.message}
                    </p>
                    <p className="text-[10px] font-medium text-slate-400 uppercase tracking-wider pt-1">
                      {formatDistanceToNow(new Date(notification.created_at), { addSuffix: true })}
                    </p>
                  </div>
                  {!notification.is_read && (
                    <div className="w-2 h-2 rounded-full bg-blue-500 mt-1.5 shrink-0" />
                  )}
                </button>
              ))}
            </div>
          )}
        </ScrollArea>
      </PopoverContent>
    </Popover>
  );
}
