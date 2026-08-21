import { Routes, Route, Navigate } from "react-router";
import { useAuthInit } from "@/hooks/useAuthInit";
import { useAuthStore } from "@/stores/authStore";
import { Toaster } from "@/components/ui/sonner";

// Auth Pages
import Login from "@/pages/Login";
import RegisterInstitution from "@/pages/RegisterInstitution";
import ForgotPassword from "@/pages/ForgotPassword";
import ResetPassword from "@/pages/ResetPassword";
import VerifyEmail from "@/pages/VerifyEmail";
import VerifyInvite from "@/pages/VerifyInvite";

// Dashboard
import DashboardLayout from "@/components/DashboardLayout";
import ProtectedRoute from "@/components/ProtectedRoute";
import Dashboard from "@/pages/Dashboard";
import Institutions from "@/pages/Institutions";
import Users from "@/pages/Users";
import Researcher from "@/pages/Researcher";
import Reviewer from "@/pages/Reviewer";
import ResearchHub from "@/pages/ResearchHub";
import Profile from "@/pages/Profile";
import Reports from "@/pages/Reports";
import Notifications from "@/pages/Notifications";
import GlobalResearchers from "@/pages/GlobalResearchers";
import Publications from "@/pages/Publications";
import Conferences from "@/pages/Conferences";
import Departments from "@/pages/Departments";
import Projects from "@/pages/Projects";
import Collaborations from "@/pages/Collaborations";
import Coauthors from "@/pages/Coauthors";
import Citations from "@/pages/Citations";
import NotFound from "@/pages/NotFound";

function AppRoutes() {
  useAuthInit();
  const isLoading = useAuthStore((state) => state.isLoading);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-900">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-emerald-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-slate-500">Loading ResearchMesh...</p>
        </div>
      </div>
    );
  }

  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/register-institution" element={<RegisterInstitution />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/reset-password" element={<ResetPassword />} />
      <Route path="/verify-email" element={<VerifyEmail />} />
      <Route path="/verify-invite" element={<VerifyInvite />} />

      {/* Protected Dashboard Routes */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route
          path="institutions"
          element={
            <ProtectedRoute allowedRoles={["SUPER_ADMIN"]}>
              <Institutions />
            </ProtectedRoute>
          }
        />
        <Route path="researchers" element={<ProtectedRoute allowedRoles={["SUPER_ADMIN"]}><GlobalResearchers /></ProtectedRoute>} />
        <Route
          path="users"
          element={
            <ProtectedRoute allowedRoles={["INSTITUTION_ADMIN"]}>
              <Users />
            </ProtectedRoute>
          }
        />
        <Route
          path="research"
          element={
            <ProtectedRoute allowedRoles={["RESEARCHER"]}>
              <Researcher />
            </ProtectedRoute>
          }
        />
        <Route
          path="reviews"
          element={
            <ProtectedRoute allowedRoles={["REVIEWER"]}>
              <Reviewer />
            </ProtectedRoute>
          }
        />
        <Route path="research-management" element={<ResearchHub />} />
        <Route path="publications" element={<ProtectedRoute allowedRoles={["INSTITUTION_ADMIN", "RESEARCHER"]}><Publications /></ProtectedRoute>} />
        <Route path="conferences" element={<ProtectedRoute allowedRoles={["INSTITUTION_ADMIN", "RESEARCHER", "REVIEWER"]}><Conferences /></ProtectedRoute>} />
        <Route path="departments" element={<ProtectedRoute allowedRoles={["INSTITUTION_ADMIN"]}><Departments /></ProtectedRoute>} />
        <Route path="projects" element={<ProtectedRoute allowedRoles={["INSTITUTION_ADMIN", "RESEARCHER"]}><Projects /></ProtectedRoute>} />
        <Route path="collaborations" element={<ProtectedRoute allowedRoles={["INSTITUTION_ADMIN", "RESEARCHER"]}><Collaborations /></ProtectedRoute>} />
        <Route path="coauthors" element={<ProtectedRoute allowedRoles={["INSTITUTION_ADMIN", "RESEARCHER"]}><Coauthors /></ProtectedRoute>} />
        <Route path="citations" element={<ProtectedRoute allowedRoles={["INSTITUTION_ADMIN", "RESEARCHER"]}><Citations /></ProtectedRoute>} />
        <Route path="reports" element={<Reports />} />
        <Route path="notifications" element={<Notifications />} />
        <Route path="profile" element={<Profile />} />
      </Route>

      {/* Redirect root to dashboard or login */}
      <Route
        path="/"
        element={
          useAuthStore.getState().isAuthenticated ? (
            <Navigate to="/dashboard" replace />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />

      {/* 404 */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}

export default function App() {
  return (
    <>
      <AppRoutes />
      <Toaster position="top-right" richColors />
    </>
  );
}
