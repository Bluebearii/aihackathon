import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { AppProvider, useAppContext } from './context/AppContext';

// Pages Placeholder (will implement these next)
import HomePage from './pages/HomePage';
import AboutPage from './pages/AboutPage';
import ServicesPage from './pages/ServicesPage';
import BookingPage from './pages/BookingPage';
import PatientDashboard from './pages/PatientDashboard';
import RewardsPage from './pages/RewardsPage';
import AdminDashboard from './pages/AdminDashboard';
import AnalyticsDashboard from './pages/AnalyticsDashboard';

import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';

import { Activity, User, LogIn, LogOut, Settings } from 'lucide-react';

const Navbar = () => {
  const { user, logout } = useAppContext();

  return (
    <nav style={{ background: '#005f73', padding: '1rem', color: 'white', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <Activity size={28} color="#94d2bd" />
        <Link to="/" style={{ color: 'white', fontSize: '1.5rem', fontWeight: 'bold' }}>WeCarePeople</Link>
      </div>
      <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
        <Link to="/" style={{ color: 'white' }}>Home</Link>
        <Link to="/about" style={{ color: 'white' }}>About</Link>
        <Link to="/services" style={{ color: 'white' }}>Services</Link>
        <Link to="/rewards" style={{ color: 'white' }}>Rewards</Link>
        
        {user?.role === 'admin' && (
          <>
            <Link to="/admin" style={{ color: '#94d2bd', fontWeight: 'bold' }}>Admin Dashboard</Link>
            <Link to="/analytics" style={{ color: '#e9c46a', fontWeight: 'bold' }}>AI Analytics</Link>
          </>
        )}
        {user?.role === 'patient' && (
          <Link to="/dashboard" style={{ color: '#94d2bd', fontWeight: 'bold' }}>Patient Dashboard</Link>
        )}

        <div style={{ marginLeft: '20px', display: 'flex', gap: '10px', alignItems: 'center' }}>
          {!user ? (
            <>
              <Link to="/login" className="btn btn-outline" style={{ padding: '8px 16px', fontSize: '0.9rem', color: 'white', borderColor: 'white' }}>Login</Link>
              <Link to="/signup" className="btn btn-secondary" style={{ padding: '8px 16px', fontSize: '0.9rem' }}>Sign Up</Link>
            </>
          ) : (
            <>
              <span style={{ marginRight: '10px' }}>Hi, {user.first_name}</span>
              <button className="btn btn-outline" onClick={logout} style={{ padding: '8px 16px', fontSize: '0.9rem', color: '#ffb3b3', borderColor: '#ffb3b3' }}>
                <LogOut size={16} style={{ marginRight: '5px', verticalAlign: 'text-bottom' }}/> Logout
              </button>
            </>
          )}
          <Link to="/book" className="btn btn-primary" style={{ border: '1px solid #94d2bd' }}>Book Appointment</Link>
        </div>
      </div>
    </nav>
  );
};

const Footer = () => (
  <footer style={{ background: '#333', color: '#ccc', padding: '2rem', textAlign: 'center', marginTop: 'auto' }}>
    <p>&copy; 2026 WeCarePeople. All rights reserved.</p>
    <p style={{ fontSize: '0.8rem', marginTop: '10px' }}>Quality Care Made Simple.</p>
  </footer>
);

function App() {
  return (
    <AppProvider>
      <Router>
        <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
          <Navbar />
          <main style={{ flex: 1, padding: '2rem 0' }}>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/about" element={<AboutPage />} />
              <Route path="/services" element={<ServicesPage />} />
              <Route path="/book" element={<BookingPage />} />
              <Route path="/dashboard" element={<PatientDashboard />} />
              <Route path="/rewards" element={<RewardsPage />} />
              <Route path="/admin" element={<AdminDashboard />} />
              <Route path="/analytics" element={<AnalyticsDashboard />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/signup" element={<SignupPage />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </Router>
    </AppProvider>
  );
}

export default App;
