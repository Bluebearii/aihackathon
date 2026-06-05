import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import { AppProvider, useAppContext } from './context/AppContext';
import axios from 'axios';

// Pages
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

import { Activity, User, LogIn, LogOut, Search, Loader2, Menu } from 'lucide-react';
import ChatbotWidget from './components/ChatbotWidget';

const Navbar = () => {
  const { user, logout, API_URL } = useAppContext();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    
    setIsSearching(true);
    try {
      const res = await axios.post(`${API_URL}/api/ai/search`, { query: searchQuery });
      if (res.data.route) {
        navigate(res.data.route);
        setSearchQuery('');
      }
    } catch (err) {
      console.error("Search failed", err);
    }
    setIsSearching(false);
  };

  return (
    <nav style={{ 
      background: 'rgba(255, 255, 255, 0.95)', 
      backdropFilter: 'blur(10px)',
      padding: '12px 40px', 
      display: 'flex', 
      justifyContent: 'space-between', 
      alignItems: 'center',
      boxShadow: '0 4px 20px rgba(0, 0, 0, 0.05)',
      position: 'sticky',
      top: 0,
      zIndex: 100,
      borderBottom: '1px solid rgba(0,0,0,0.05)'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{ background: 'linear-gradient(135deg, #0f766e 0%, #0d9488 100%)', padding: '8px', borderRadius: '12px' }}>
          <Activity size={24} color="white" />
        </div>
        <Link to="/" style={{ color: '#0f172a', fontSize: '1.5rem', fontWeight: '800', textDecoration: 'none', letterSpacing: '-0.5px' }}>
          WeCarePeople
        </Link>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '30px' }}>
        {/* Navigation Links */}
        <div style={{ display: 'flex', gap: '24px', alignItems: 'center' }}>
          <Link to="/" className="nav-link">Home</Link>
          <Link to="/about" className="nav-link">About</Link>
          <Link to="/services" className="nav-link">Services</Link>
          <Link to="/rewards" className="nav-link">Rewards</Link>
          
          {user?.role === 'admin' && (
            <>
              <Link to="/admin" className="nav-link admin-link">Admin</Link>
              <Link to="/analytics" className="nav-link analytics-link">Analytics</Link>
            </>
          )}
          {user?.role === 'patient' && (
            <Link to="/dashboard" className="nav-link patient-link">Dashboard</Link>
          )}
        </div>

        {/* AI Search Bar */}
        <form onSubmit={handleSearch} style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
          <Search size={16} color="#94a3b8" style={{ position: 'absolute', left: '12px' }} />
          <input 
            type="text" 
            placeholder="AI Search..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            disabled={isSearching}
            style={{
              padding: '10px 16px 10px 36px',
              borderRadius: '20px',
              border: '1px solid #cbd5e1',
              outline: 'none',
              background: '#f8fafc',
              fontSize: '0.9rem',
              width: '200px',
              transition: 'all 0.2s ease',
              boxShadow: 'inset 0 1px 2px rgba(0,0,0,0.02)'
            }}
            onFocus={(e) => e.target.style.width = '260px'}
            onBlur={(e) => e.target.style.width = '200px'}
          />
          {isSearching && <Loader2 size={16} className="spin-animation" style={{ position: 'absolute', right: '12px', color: '#0f766e' }}/>}
        </form>

        {/* Auth Buttons */}
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center', borderLeft: '1px solid #e2e8f0', paddingLeft: '30px' }}>
          {!user ? (
            <>
              <Link to="/login" style={{ color: '#475569', fontWeight: '600', textDecoration: 'none', padding: '8px 12px' }}>Log In</Link>
              <Link to="/signup" style={{ 
                background: '#0f172a', color: 'white', fontWeight: '600', textDecoration: 'none', 
                padding: '10px 20px', borderRadius: '24px', transition: 'background 0.2s ease' 
              }}>Sign Up</Link>
            </>
          ) : (
            <>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#334155', fontWeight: '500' }}>
                <div style={{ background: '#e2e8f0', borderRadius: '50%', padding: '6px' }}><User size={16} /></div>
                <span>{user.first_name}</span>
              </div>
              <button onClick={logout} style={{ 
                background: 'transparent', border: '1px solid #ef4444', color: '#ef4444', fontWeight: '600', 
                padding: '8px 16px', borderRadius: '24px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px'
              }}>
                <LogOut size={16}/> Logout
              </button>
            </>
          )}
          <Link to="/book" style={{ 
            background: 'linear-gradient(135deg, #0f766e 0%, #0d9488 100%)', color: 'white', fontWeight: '600', textDecoration: 'none', 
            padding: '10px 20px', borderRadius: '24px', boxShadow: '0 4px 10px rgba(15, 118, 110, 0.2)'
          }}>Book Now</Link>
        </div>
      </div>
    </nav>
  );
};

const Footer = () => (
  <footer style={{ background: '#0f172a', color: '#94a3b8', padding: '3rem 40px', marginTop: 'auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      <Activity size={20} color="#0d9488" />
      <span style={{ color: 'white', fontWeight: 'bold', fontSize: '1.2rem' }}>WeCarePeople</span>
    </div>
    <div style={{ fontSize: '0.9rem' }}>&copy; 2026 WeCarePeople Clinic. Quality Care Made Simple.</div>
  </footer>
);

function App() {
  return (
    <AppProvider>
      <Router>
        <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', background: '#f1f5f9' }}>
          <Navbar />
          <main style={{ flex: 1, padding: '0 40px' }}>
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
          <ChatbotWidget />
        </div>
      </Router>
      
      <style>{`
        .nav-link {
          color: #475569;
          text-decoration: none;
          font-weight: 600;
          font-size: 0.95rem;
          transition: color 0.2s ease;
        }
        .nav-link:hover {
          color: #0f766e;
        }
        .admin-link { color: #8b5cf6; }
        .admin-link:hover { color: #7c3aed; }
        .analytics-link { color: #f59e0b; }
        .analytics-link:hover { color: #d97706; }
        .patient-link { color: #0ea5e9; }
        .patient-link:hover { color: #0284c7; }
        .spin-animation {
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </AppProvider>
  );
}

export default App;
