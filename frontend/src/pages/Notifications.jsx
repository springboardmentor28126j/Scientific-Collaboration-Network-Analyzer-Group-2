import { useEffect, useState } from "react";
import {
  getNotifications,
  markAsRead,
  deleteNotification,
} from "../services/notificationService";

function Notifications() {
  const [notifications, setNotifications] = useState([]);

  const loadNotifications = async () => {
    try {
      const data = await getNotifications();

      console.log("Notifications:", data);

      setNotifications(data);
    } catch (error) {
      console.error(error);
      alert("Failed to load notifications");
    }
  };

  useEffect(() => {
    loadNotifications();
  }, []);

  const handleRead = async (id) => {
    try {
      await markAsRead(id);
      loadNotifications();
    } catch (error) {
      console.error(error);
      alert("Failed to mark notification as read");
    }
  };

  const handleDelete = async (id) => {
    const confirmDelete = window.confirm(
      "Delete this notification?"
    );

    if (!confirmDelete) return;

    try {
      await deleteNotification(id);
      loadNotifications();
    } catch (error) {
      console.error(error);
      alert("Failed to delete notification");
    }
  };

  return (
    <div style={{ padding: "30px" }}>
      <h2>Notifications</h2>

      {notifications.length === 0 ? (
        <p>No notifications available.</p>
      ) : (
        <table
          border="1"
          cellPadding="10"
          style={{
            width: "100%",
            borderCollapse: "collapse",
            marginTop: "20px",
          }}
        >
          <thead>
            <tr>
              <th>Title</th>
              <th>Message</th>
              <th>Type</th>
              <th>Status</th>
              <th>Created At</th>
              <th>Actions</th>
            </tr>
          </thead>

          <tbody>
            {notifications.map((notification) => (
              <tr key={notification.id}>
                <td>{notification.title}</td>

                <td>{notification.message}</td>

                <td>{notification.notification_type}</td>

                <td>
                  {notification.is_read ? "Read" : "Unread"}
                </td>

                <td>
                  {new Date(
                    notification.created_at
                  ).toLocaleString()}
                </td>

                <td>
                  {!notification.is_read && (
                    <button
                      onClick={() =>
                        handleRead(notification.id)
                      }
                    >
                      Mark as Read
                    </button>
                  )}

                  {" "}

                  <button
                    onClick={() =>
                      handleDelete(notification.id)
                    }
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default Notifications;