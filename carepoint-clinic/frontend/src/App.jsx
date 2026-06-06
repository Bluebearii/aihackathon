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
import CalendarPage from './pages/CalendarPage';
import PatientDatabase from './pages/PatientDatabase';
import AdminBooking from './pages/AdminBooking';
import MedicalHistoryPage from './pages/MedicalHistoryPage';

import { Activity, User, LogIn, LogOut, Search, Loader2, Menu } from 'lucide-react';
import ChatbotWidget from './components/ChatbotWidget';

const SEARCHABLE_PAGES = [
  { name: 'Home', route: '/' },
  { name: 'About', route: '/about' },
  { name: 'Services', route: '/services' },
  { name: 'Rewards', route: '/rewards' },
  { name: 'Book Appointment', route: '/book' },
  { name: 'Medical History', route: '/medical-history' },
  { name: 'Admin Dashboard', route: '/admin', requiresAuth: 'admin' },
  { name: 'Admin Calendar', route: '/admin/calendar', requiresAuth: 'admin' },
  { name: 'Patient Database', route: '/admin/patients', requiresAuth: 'admin' },
  { name: 'Admin Booking', route: '/admin/book', requiresAuth: 'admin' },
  { name: 'Analytics', route: '/analytics', requiresAuth: 'admin' },
  { name: 'Patient Dashboard', route: '/dashboard', requiresAuth: 'patient' },
  { name: 'Patient Calendar', route: '/calendar', requiresAuth: 'patient' },
  { name: 'Login', route: '/login' },
  { name: 'Sign Up', route: '/signup' }
];

const Navbar = () => {
  const { user, logout, API_URL } = useAppContext();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [isFocused, setIsFocused] = useState(false);

  const handleSearchInput = (e) => {
    const val = e.target.value;
    setSearchQuery(val);
    if (!val.trim()) {
      setSuggestions([]);
      return;
    }
    const lowerVal = val.toLowerCase();
    
    const accessiblePages = SEARCHABLE_PAGES.filter(page => {
      if (page.requiresAuth) return user && user.role === page.requiresAuth;
      return true;
    });

    const matched = accessiblePages.filter(page => page.name.toLowerCase().includes(lowerVal));
    
    matched.sort((a, b) => {
      const aStarts = a.name.toLowerCase().startsWith(lowerVal);
      const bStarts = b.name.toLowerCase().startsWith(lowerVal);
      if (aStarts && !bStarts) return -1;
      if (!aStarts && bStarts) return 1;
      return 0;
    });

    setSuggestions(matched);
  };

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
        <img src="/logo.png" alt="Care Flow AI Logo" style={{ width: '40px', height: '40px', borderRadius: '8px' }} />
        <Link to="/" style={{ color: '#0f172a', fontSize: '1.5rem', fontWeight: '800', textDecoration: 'none', letterSpacing: '-0.5px', whiteSpace: 'nowrap' }}>
          Care Flow AI
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
              <Link to="/admin/calendar" className="nav-link admin-link">Calendar</Link>
              <Link to="/admin/patients" className="nav-link admin-link">Patients</Link>
              <Link to="/analytics" className="nav-link analytics-link">Analytics</Link>
            </>
          )}
          {user?.role === 'patient' && (
            <>
              <Link to="/dashboard" className="nav-link patient-link">Dashboard</Link>
              <Link to="/calendar" className="nav-link patient-link">Calendar</Link>
            </>
          )}
        </div>

        {/* AI Search Bar */}
        <div style={{ position: 'relative' }}>
          <form onSubmit={handleSearch} style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
            <Search size={16} color="#94a3b8" style={{ position: 'absolute', left: '12px' }} />
            <input 
              type="text" 
              placeholder="AI Search..." 
              value={searchQuery}
              onChange={handleSearchInput}
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
              onFocus={(e) => { e.target.style.width = '260px'; setIsFocused(true); }}
              onBlur={(e) => { e.target.style.width = '200px'; setIsFocused(false); }}
            />
            {isSearching && <Loader2 size={16} className="spin-animation" style={{ position: 'absolute', right: '12px', color: '#0f766e' }}/>}
          </form>
          {/* Autocomplete Dropdown */}
          {isFocused && suggestions.length > 0 && (
            <div style={{
              position: 'absolute',
              top: '100%',
              left: 0,
              right: 0,
              background: 'white',
              marginTop: '8px',
              borderRadius: '12px',
              boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)',
              border: '1px solid #e2e8f0',
              overflow: 'hidden',
              zIndex: 50
            }}>
              {suggestions.map((s, i) => (
                <div 
                  key={i} 
                  onMouseDown={() => {
                    navigate(s.route);
                    setSearchQuery('');
                    setSuggestions([]);
                  }}
                  style={{
                    padding: '12px 16px',
                    cursor: 'pointer',
                    fontSize: '0.9rem',
                    color: '#334155',
                    borderBottom: i === suggestions.length - 1 ? 'none' : '1px solid #f1f5f9',
                    background: 'white',
                    transition: 'background 0.2s',
                    whiteSpace: 'nowrap',
                    textOverflow: 'ellipsis',
                    overflow: 'hidden'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = '#f8fafc'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'white'}
                >
                  <Search size={14} color="#94a3b8" style={{ marginRight: '10px', verticalAlign: 'middle' }} />
                  {s.name}
                </div>
              ))}
            </div>
          )}
        </div>

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
      <img src="/logo.png" alt="Care Flow AI Logo" style={{ width: '24px', height: '24px', borderRadius: '4px' }} />
      <span style={{ color: 'white', fontWeight: 'bold', fontSize: '1.2rem' }}>Care Flow AI</span>
    </div>
    <div style={{ fontSize: '0.9rem' }}>&copy; 2026 Care Flow AI Clinic. Quality Care Made Simple.</div>
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
              <Route path="/admin/calendar" element={<CalendarPage />} />
              <Route path="/calendar" element={<CalendarPage />} />
              <Route path="/admin/patients" element={<PatientDatabase />} />
              <Route path="/admin/book" element={<AdminBooking />} />
              <Route path="/medical-history" element={<MedicalHistoryPage />} />
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
