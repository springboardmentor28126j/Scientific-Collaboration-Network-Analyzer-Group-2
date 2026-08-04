import { Navigate } from "react-router-dom";
import { isAdmin } from "../utils/auth";

export default function AdminRoute({ children }) {
  return isAdmin()
    ? children
    : <Navigate to="/conferences" replace />;
}