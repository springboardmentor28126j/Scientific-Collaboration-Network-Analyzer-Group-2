import { BrowserRouter, Routes, Route } from "react-router-dom";

// Public Pages
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import VerifyEmail from "./pages/VerifyEmail";
import ResendVerification from "./pages/ResendVerification";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import Notifications from "./pages/Notifications";
// Dashboard
import Dashboard from "./pages/Dashboard";
import Reports from "./pages/Reports";

// Navbar & Protection
import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/ProtectedRoute";
import AdminRoute from "./components/AdminRoute";

// Researchers
import Researchers from "./pages/researchers/Researchers";
import CreateResearcher from "./pages/researchers/CreateResearcher";
import ResearcherDetails from "./pages/researchers/ResearcherDetails";
import EditResearcher from "./pages/researchers/EditResearcher";

// Publications
import Publications from "./pages/Publications";
import CreatePublication from "./pages/CreatePublication";
import EditPublication from "./pages/EditPublication";
import PublicationDetails from "./pages/PublicationDetails";

// Conferences
import Conferences from "./pages/conferences/Conferences";
import CreateConference from "./pages/conferences/CreateConference";
import EditConference from "./pages/conferences/EditConference";
import ConferenceDetails from "./pages/conferences/ConferenceDetails";

// Institutions
import Institutions from "./pages/institutions/Institutions";
import CreateInstitution from "./pages/institutions/CreateInstitution";
import EditInstitution from "./pages/institutions/EditInstitution";
import InstitutionDetails from "./pages/institutions/InstitutionDetails";

// Search
import Search from "./pages/Search";
import UserManagement from "./pages/UserManagement";


// Citations
import Citations from "./pages/citations/Citations";
import CreateCitation from "./pages/citations/CreateCitation";
import EditCitation from "./pages/citations/EditCitation";
import CitationDetails from "./pages/citations/CitationDetails";

import Collaboration from "./pages/Collaboration";


function App() {
  return (
    <BrowserRouter>
      <Navbar />

      <Routes>

        {/* ================= Public Routes ================= */}

        <Route path="/" element={<Home />} />

        <Route path="/login" element={<Login />} />

        <Route path="/register" element={<Register />} />

        <Route
          path="/verify-email"
          element={<VerifyEmail />}
        />

        <Route
          path="/resend-verification"
          element={<ResendVerification />}
        />


        <Route
          path="/forgot-password"
          element={<ForgotPassword />}
        />

        <Route
          path="/reset-password"
          element={<ResetPassword />}
        />

        {/* ================= Dashboard ================= */}

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        {/* ================= Researchers ================= */}

        <Route
          path="/researchers"
          element={
            <ProtectedRoute>
              <Researchers />
            </ProtectedRoute>
          }
        />
        

        <Route
          path="/researchers/create"
          element={
            <ProtectedRoute>
              <CreateResearcher />
            </ProtectedRoute>
          }
        />
        <Route
          path="/researchers/:id"
          element={
            <ProtectedRoute>
              <ResearcherDetails />
            </ProtectedRoute>
          }
        />
        <Route
          path="/researchers/edit/:id"
          element={
            <ProtectedRoute>
              <EditResearcher />
            </ProtectedRoute>
          }
        />

        {/* ================= Publications ================= */}

        <Route
          path="/publications"
          element={
            <ProtectedRoute>
              <Publications />
            </ProtectedRoute>
          }
        />

        <Route
          path="/publications/create"
          element={
            <ProtectedRoute>
              <CreatePublication />
            </ProtectedRoute>
          }
        />

        <Route
          path="/publications/:id"
          element={
            <ProtectedRoute>
              <PublicationDetails />
            </ProtectedRoute>
          }
        />

        <Route
          path="/publications/edit/:id"
          element={
            <ProtectedRoute>
              <EditPublication />
            </ProtectedRoute>
          }
        />

        {/* =================Citations ================ */}
        <Route
          path="/citations"
          element={
            <ProtectedRoute>
              <Citations />
            </ProtectedRoute>
          }
        />

        <Route
          path="/citations/create"
          element={
            <ProtectedRoute>
              <CreateCitation />
            </ProtectedRoute>
          }
        />

        <Route
          path="/citations/edit/:id"
          element={
            <ProtectedRoute>
              <EditCitation />
            </ProtectedRoute>
          }
        />

        <Route
          path="/citations/:id"
          element={
            <ProtectedRoute>
              <CitationDetails />
            </ProtectedRoute>
          }
        />



        {/* ================= Conferences ================= */}

        <Route
          path="/conferences"
          element={
            <ProtectedRoute>
              <Conferences />
            </ProtectedRoute>
          }
        />

        {/* Only System Admin and Institution Admin can create conferences */}

        <Route
          path="/conferences/create"
          element={
            <ProtectedRoute>
              <AdminRoute>
                <CreateConference />
              </AdminRoute>
            </ProtectedRoute>
          }
        />

        <Route
          path="/conferences/:id"
          element={
            <ProtectedRoute>
              <ConferenceDetails />
            </ProtectedRoute>
          }
        />

        {/* Only System Admin can edit conferences */}

        <Route
          path="/conferences/edit/:id"
          element={
            <ProtectedRoute>
              <AdminRoute>
                <EditConference />
              </AdminRoute>
            </ProtectedRoute>
          }
        />

        {/* ================= Institutions ================= */}

        <Route
          path="/institutions"
          element={
            <ProtectedRoute>
              <Institutions />
            </ProtectedRoute>
          }
        />

        <Route
          path="/institutions/create"
          element={
            <ProtectedRoute>
              <CreateInstitution />
            </ProtectedRoute>
          }
        />

        <Route
          path="/institutions/:id"
          element={
            <ProtectedRoute>
              <InstitutionDetails />
            </ProtectedRoute>
          }
        />

        <Route
          path="/institutions/edit/:id"
          element={
            <ProtectedRoute>
              <EditInstitution />
            </ProtectedRoute>
          }
        />

        {/* ================= Collaboration ================= */}

        <Route
          path="/collaborations"
          element={
            <ProtectedRoute>
              <Collaboration />
            </ProtectedRoute>
          }
        />
        {/* ================= Search ================= */}

        <Route
          path="/search"
          element={
            <ProtectedRoute>
              <Search />
            </ProtectedRoute>
          }
        />

        {/* ================= User Management ================= */}

        <Route
          path="/users"
          element={
            <ProtectedRoute>
              <AdminRoute>
                <UserManagement />
              </AdminRoute>
            </ProtectedRoute>
          }
        />

        <Route
          path="/notifications"
          element={
            <ProtectedRoute>
              <Notifications />
            </ProtectedRoute>
          }
        />

        <Route
          path="/reports"
          element={
            <ProtectedRoute>
              <Reports />
            </ProtectedRoute>
          }
        />

      </Routes>
    </BrowserRouter>
  );
}

export default App;
