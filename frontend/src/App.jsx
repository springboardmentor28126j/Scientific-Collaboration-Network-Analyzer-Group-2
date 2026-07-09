import { BrowserRouter, Routes, Route } from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import Researchers from "./pages/Researchers";
import ResearchPapers from "./pages/ResearchPapers";
import Institutions from "./pages/Institutions";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ProtectedRoute from "./components/ProtectedRoute";

function App() {
  return (
    <BrowserRouter>
      <Routes>
       <Route
  path="/"
  element={
    <ProtectedRoute>
      <Dashboard />
    </ProtectedRoute>
  }
/>

<Route
  path="/researchers"
  element={
    <ProtectedRoute>
      <Researchers />
    </ProtectedRoute>
  }
/>

<Route
  path="/papers"
  element={
    <ProtectedRoute>
      <ResearchPapers />
    </ProtectedRoute>
  }
/>

<Route
  path="/institutions"
  element={
    <ProtectedRoute>
      <Institutions />
    </ProtectedRoute>
  }
/>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;