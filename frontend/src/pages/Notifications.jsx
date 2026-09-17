import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import "./Notifications.css";

const API_BASE_URL = "http://127.0.0.1:8000";

function Notifications() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const userId = localStorage.getItem("user_id");

  const fetchNotifications = useCallback(async () => {
    if (!userId) {
      setLoading(false);
      setNotifications([]);
      return;
    }

    try {
      setLoading(true);
      setError("");

      const response = await fetch(
        `${API_BASE_URL}/notifications/user/${userId}`
      );

      if (!response.ok) {
        const errorText = await response.text();
        console.error(
          "Notifications API error:",
          response.status,
          errorText
        );

        throw new Error(
          `Failed to fetch notifications (${response.status})`
        );
      }

      const data = await response.json();

      console.log("Notifications API response:", data);

      /*
        Some APIs return:

        [
          {...},
          {...}
        ]

        Others may return:

        {
          "notifications": [...]
        }

        This handles both.
      */
      const notificationData = Array.isArray(data)
        ? data
        : Array.isArray(data?.notifications)
        ? data.notifications
        : [];

      setNotifications(notificationData);
    } catch (err) {
      console.error("Error fetching notifications:", err);
      setError(err.message || "Unable to load notifications.");
      setNotifications([]);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
  const timer = setTimeout(() => {
    fetchNotifications();
  }, 0);

  return () => clearTimeout(timer);
}, [fetchNotifications]);
  const markAsRead = async (notificationId) => {
    if (!notificationId) {
      return;
    }

    try {
      const response = await fetch(
        `${API_BASE_URL}/notifications/${notificationId}/read`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        const errorText = await response.text();

        console.error(
          "Mark as read error:",
          response.status,
          errorText
        );

        throw new Error("Failed to mark notification as read");
      }

      // Update immediately without waiting for another GET request
      setNotifications((previousNotifications) =>
        previousNotifications.map((notification) =>
          notification.notification_id === notificationId
            ? {
                ...notification,
                is_read: 1,
              }
            : notification
        )
      );
    } catch (err) {
      console.error("Error marking notification as read:", err);
      alert("Unable to mark notification as read.");
    }
  };

  const deleteNotification = async (notificationId) => {
    if (!notificationId) {
      return;
    }

    try {
      const response = await fetch(
        `${API_BASE_URL}/notifications/${notificationId}`,
        {
          method: "DELETE",
        }
      );

      if (!response.ok) {
        const errorText = await response.text();

        console.error(
          "Delete notification error:",
          response.status,
          errorText
        );

        throw new Error("Failed to delete notification");
      }

      setNotifications((previousNotifications) =>
        previousNotifications.filter(
          (notification) =>
            notification.notification_id !== notificationId
        )
      );
    } catch (err) {
      console.error("Error deleting notification:", err);
      alert("Unable to delete notification.");
    }
  };

  const unreadCount = notifications.filter(
    (notification) =>
      notification.is_read === 0 ||
      notification.is_read === false ||
      notification.is_read === "0" ||
      notification.is_read === "false"
  ).length;

  return (
    <div className="notifications-page">
      <div className="notifications-header">
        <div>
          <h1>Notifications</h1>

          <p>
            View your latest research and collaboration updates.
          </p>

          {!loading && notifications.length > 0 && (
            <span className="notification-count">
              {unreadCount} unread notification
              {unreadCount !== 1 ? "s" : ""}
            </span>
          )}
        </div>

        <Link
          to="/dashboard"
          className="back-dashboard-btn"
        >
          Back to Dashboard
        </Link>
      </div>

      <div className="notifications-card">
        {loading ? (
          <div className="notification-message">
            <div className="loading-spinner"></div>
            <p>Loading notifications...</p>
          </div>
        ) : !userId ? (
          <div className="notification-message">
            <div className="empty-notification-icon">🔐</div>

            <h3>Login Required</h3>

            <p>
              Please log in to view your notifications.
            </p>
          </div>
        ) : error ? (
          <div className="notification-message error-message">
            <div className="empty-notification-icon">⚠️</div>

            <h3>Unable to Load Notifications</h3>

            <p>{error}</p>

            <button
              type="button"
              className="retry-btn"
              onClick={fetchNotifications}
            >
              Try Again
            </button>
          </div>
        ) : notifications.length === 0 ? (
          <div className="notification-message">
            <div className="empty-notification-icon">
              🔔
            </div>

            <h3>No Notifications</h3>

            <p>
              You don't have any notifications yet.
            </p>
          </div>
        ) : (
          <div className="notification-list">
            {notifications.map((notification) => {
              const isUnread =
                notification.is_read === 0 ||
                notification.is_read === false ||
                notification.is_read === "0" ||
                notification.is_read === "false";

              return (
                <div
                  key={notification.notification_id}
                  className={`notification-item ${
                    isUnread ? "unread" : "read"
                  }`}
                >
                  <div className="notification-icon">
                    🔔
                  </div>

                  <div className="notification-content">
                    <div className="notification-top">
                      <h3>
                        {notification.notification_type ||
                          "Notification"}
                      </h3>

                      {isUnread && (
                        <span className="unread-badge">
                          Unread
                        </span>
                      )}
                    </div>

                    <p className="notification-text">
                      {notification.message ||
                        "You have a new notification."}
                    </p>

                    {notification.created_at && (
                      <span className="notification-date">
                        {new Date(
                          notification.created_at
                        ).toLocaleString()}
                      </span>
                    )}

                    <div className="notification-actions">
                      {isUnread && (
                        <button
                          type="button"
                          onClick={() =>
                            markAsRead(
                              notification.notification_id
                            )
                          }
                          className="read-btn"
                        >
                          Mark as Read
                        </button>
                      )}

                      <button
                        type="button"
                        onClick={() =>
                          deleteNotification(
                            notification.notification_id
                          )
                        }
                        className="delete-notification-btn"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

export default Notifications;