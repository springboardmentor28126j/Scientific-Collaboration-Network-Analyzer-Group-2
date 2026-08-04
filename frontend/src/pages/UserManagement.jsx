import { useEffect, useState } from "react";
import {
  getUsers,
  deleteUser,
} from "../services/userService";

function UserManagement() {
  const [users, setUsers] = useState([]);

  const loadUsers = async () => {
  try {
    const data = await getUsers();

    console.log("Users API Response:", data);

    setUsers(data);
  } catch (error) {
    console.error("Error fetching users:", error);
    alert("Failed to load users");
  }
};

  useEffect(() => {
    loadUsers();
  }, []);

  const handleDelete = async (id) => {
    const confirmDelete = window.confirm(
      "Are you sure you want to delete this user?"
    );

    if (!confirmDelete) return;

    try {
      await deleteUser(id);
      loadUsers();
    } catch (error) {
      console.error(error);
      alert("Failed to delete user");
    }
  };

  return (
    <div style={{ padding: "30px" }}>
      <h2>User Management</h2>

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
            <th>Email</th>
            <th>Role</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>

        <tbody>
          {users.map((user) => (
            <tr key={user.id}>
              <td>{user.email}</td>
              <td>{user.role}</td>
              <td>{user.is_active ? "Active" : "Inactive"}</td>

              <td>
                <button
                  onClick={() => handleDelete(user.id)}
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default UserManagement;