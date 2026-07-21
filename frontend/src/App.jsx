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


      </Routes>

    </BrowserRouter>
  );
}

export default App;