import { BrowserRouter, Routes, Route } from "react-router-dom";

import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Researchers from "./pages/Researchers";
import ResearcherProfile from "./pages/ResearcherProfile";
import Publications from "./pages/Publications";
import Collaborations from "./pages/Collaborations";
import Analytics from "./pages/Analytics";
import Conference from "./pages/Conferences";
import Reports from "./pages/Reports";

function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* Home */}
        <Route path="/" element={<Home />} />

        {/* Login */}
        <Route path="/login" element={<Login />} />

        {/* Register */}
        <Route path="/register" element={<Register />} />

        {/* Dashboard */}
        <Route path="/dashboard" element={<Dashboard />} />

        {/* Researchers */}
        <Route path="/researchers" element={<Researchers />} />

        {/* Researcher Profile */}
        <Route path="/profile" element={<ResearcherProfile />} />

        {/* Publications */}
        <Route path="/publications" element={<Publications />} />

        {/* Collaborations */}
        <Route path="/collaborations" element={<Collaborations />} />

        {/* Analytics */}
        <Route path="/analytics" element={<Analytics />} />

        {/* Conferences */}
        <Route path="/conferences" element={<Conference />} />

        {/* Reports */}
        <Route path="/reports" element={<Reports />} />

      </Routes>
    </BrowserRouter>
  );
}

export default App;