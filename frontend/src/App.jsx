import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Navbar from './components/Navbar';

// Core Pages
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import ForgotPassword from './pages/ForgotPassword';
import Dashboard from './pages/Dashboard';
import Reports from './pages/Reports';

// Conferences Pages
import Conferences from './pages/conferences/Conferences';
import ConferenceDetails from './pages/conferences/ConferenceDetails';
import CreateConference from './pages/conferences/CreateConference';
import EditConference from './pages/conferences/EditConference';

// Institutions Pages
import Institutions from './pages/institutions/Institutions';
import InstitutionDetails from './pages/institutions/InstitutionDetails';
import CreateInstitution from './pages/institutions/CreateInstitution';
import EditInstitution from './pages/institutions/EditInstitution';

// Researchers Pages
import Researchers from './pages/researchers/Researchers';
import ResearcherDetails from './pages/researchers/ResearcherDetails';
import CreateResearcher from './pages/researchers/CreateResearcher';
import EditResearcher from './pages/researchers/EditResearcher';

// Publications Pages
import Publications from './pages/publications/Publications';
import PublicationDetails from './pages/publications/PublicationDetails';
import CreatePublication from './pages/publications/CreatePublication';
import EditPublication from './pages/publications/EditPublication';

// Helper component to conditionally show Navbar
function Layout({ children }) {
  const location = useLocation();
  const hideNavbarOn = ['/login', '/register', '/forgot-password', '/'];
  const shouldShowNavbar = !hideNavbarOn.includes(location.pathname);

  return (
    <>
      {shouldShowNavbar && <Navbar />}
      <div>{children}</div>
    </>
  );
}

export default function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          {/* Public Auth Routes */}
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />

          {/* Dashboard & Reports */}
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/reports" element={<Reports />} />

          {/* Conferences */}
          <Route path="/conferences" element={<Conferences />} />
          <Route path="/conferences/create" element={<CreateConference />} />
          <Route path="/conferences/:id" element={<ConferenceDetails />} />
          <Route path="/conferences/:id/edit" element={<EditConference />} />

          {/* Institutions */}
          <Route path="/institutions" element={<Institutions />} />
          <Route path="/institutions/create" element={<CreateInstitution />} />
          <Route path="/institutions/:id" element={<InstitutionDetails />} />
          <Route path="/institutions/:id/edit" element={<EditInstitution />} />

          {/* Researchers */}
          <Route path="/researchers" element={<Researchers />} />
          <Route path="/researchers/create" element={<CreateResearcher />} />
          <Route path="/researchers/:id" element={<ResearcherDetails />} />
          <Route path="/researchers/:id/edit" element={<EditResearcher />} />

          {/* Publications */}
          <Route path="/publications" element={<Publications />} />
          <Route path="/publications/create" element={<CreatePublication />} />
          <Route path="/publications/:id" element={<PublicationDetails />} />
          <Route path="/publications/:id/edit" element={<EditPublication />} />
          <Route path="/publications/edit/:id" element={<EditPublication />} />
        </Routes>
      </Layout>
    </Router>
  );
}