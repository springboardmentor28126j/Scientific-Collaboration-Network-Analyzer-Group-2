import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Researchers from "./pages/Researchers";
import Publications from "./pages/Publications";
import Collaborations from "./pages/Collaborations";
import Conferences from "./pages/Conferences";
import Reports from "./pages/Reports";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/researchers" element={<Researchers />} />
        <Route path="/publications" element={<Publications />} />
        <Route path="/collaborations" element={<Collaborations />} />
        <Route path="/conferences" element={<Conferences />} />
        <Route path="/reports" element={<Reports />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
