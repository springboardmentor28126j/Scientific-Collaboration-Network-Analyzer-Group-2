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
        <Route path="/collaborations" element={<Collaborations />} />

        <Route path="/analytics" element={<Analytics />} />

      </Routes>
    </BrowserRouter>
  );
}

export default App;