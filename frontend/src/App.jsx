import { BrowserRouter, Routes, Route } from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import Researchers from "./pages/Researchers";
import ResearchPapers from "./pages/ResearchPapers";
import Institutions from "./pages/Institutions";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ResearcherDashboard from "./pages/ResearcherDashboard";
import InstitutionDashboard from "./pages/InstitutionDashboard";
import ResearcherProfile from "./pages/ResearcherProfile";
import MyPapers from "./pages/MyPapers";
import UploadPaper from "./pages/UploadPaper";
import Collaborations from "./pages/Collaborations";
import Analytics from "./pages/Analytics";
import Settings from "./pages/Settings";
import AddConference from "./pages/AddConference";
import MyConferences from "./pages/MyConferences";
import EditConference from "./pages/EditConference";
import ConferenceDetails from "./pages/ConferenceDetails";
import InstitutionManagement from "./pages/InstitutionManagement";
import Projects from "./pages/Projects";
import CollaborationDashboard from "./pages/CollaborationDashboard";
import CollaborationRequests from "./pages/CollaborationRequests";
import InstitutionRequests from "./pages/InstitutionRequests";
import SharedFiles from "./pages/SharedFiles";
import ProgressUpdates from "./pages/ProgressUpdates";
import Notifications from "./pages/Notifications";
import Timeline from "./pages/Timeline";
import Citation from "./pages/Citation";
import InstitutionCollaboration from "./pages/InstitutionCollaboration";
import PublicationReport from "./pages/PublicationReport";
import AuditLogs from "./pages/AuditLogs";
import Reports from "./pages/Reports";
import ResearchReport from "./pages/ResearchReport";
import InstitutionReport from "./pages/InstitutionReport";
import CollaborationReport from "./pages/CollaborationReport";
import AIRecommendations from "./pages/AIRecommendations";
function App() {
  return (
    <BrowserRouter>

      <Routes>

        <Route path="/" element={<Dashboard />} />

        <Route path="/researchers" element={<Researchers />} />

        <Route path="/papers" element={<ResearchPapers />} />

        <Route path="/institutions" element={<Institutions />} />

        <Route path="/login" element={<Login />} />

        <Route path="/register" element={<Register />} />

        <Route
  path="/researcher-dashboard"
  element={<ResearcherDashboard />}
/>

<Route
  path="/institution-dashboard"
  element={<InstitutionDashboard />}
/>
<Route
  path="/researcher-profile"
  element={<ResearcherProfile />}
/>

<Route
  path="/my-papers"
  element={<MyPapers />}
/>

<Route
  path="/upload-paper"
  element={<UploadPaper />}
/>

<Route
  path="/collaborations"
  element={<Collaborations />}
/>

<Route
  path="/analytics"
  element={<Analytics />}
/>

<Route
  path="/settings"
  element={<Settings />}
/>
<Route
    path="/add-conference"
    element={<AddConference />}
/>

<Route
    path="/my-conferences"
    element={<MyConferences />}
/>

<Route
    path="/edit-conference/:id"
    element={<EditConference />}
/>

<Route
    path="/conference/:id"
    element={<ConferenceDetails />}
/>
<Route
    path="/institution-management"
    element={<InstitutionManagement />}
/>
<Route path="/projects" element={<Projects />} />
<Route
    path="/collaboration-dashboard"
    element={<CollaborationDashboard />}
/>
<Route
    path="/collaboration-requests"
    element={<CollaborationRequests />}
/>
<Route
    path="/institution-requests"
    element={<InstitutionRequests />}
/>
<Route
    path="/shared-files"
    element={<SharedFiles />}
/>
<Route
    path="/progress-updates"
    element={<ProgressUpdates />}
/>
<Route
    path="/notifications"
    element={<Notifications />}
/>
<Route
    path="/timeline"
    element={<Timeline />}
/>
<Route
    path="/citations"
    element={<Citation />}
/>
<Route
    path="/institution-collaboration"
    element={<InstitutionCollaboration />}
/>
<Route
    path="/publication-report"
    element={<PublicationReport />}
/>
<Route
    path="/reports"
    element={<Reports />}
/>
<Route path="/audit-logs" element={<AuditLogs />} />
<Route
    path="/ai-recommendations"
    element={<AIRecommendations />}
/>
<Route
    path="/reports/research"
    element={<ResearchReport />}
/>
<Route
    path="/reports/institution"
    element={<InstitutionReport />}
/>
<Route
    path="/reports/collaboration"
    element={<CollaborationReport />}
/>

      </Routes>

    </BrowserRouter>
  );
}

export default App;