import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAppContext } from '../context/AppContext';

const COMMON_CONDITIONS = [
  "Acquired Respiratory Distress Syndrome", "Angina", "Anxiety or Panic Disorders",
  "Arthritis (RA, OA)", "Asthma", "Chronic Obstructive Pulmonary Disease (COPD)",
  "Congestive Heart Failure (CHF)", "Degenerative Disc Disease", "Depression",
  "Diabetes", "Emphysema", "Hearing Impairment", "Heart Attack",
  "Multiple Sclerosis", "Osteoporosis", "Parkinson's Disease", "Stroke or TIA",
  "Allergies", "Headaches", "Back Injury", "Bleeding Disorders", "Cancer",
  "Epilepsy or Seizure Disorder", "Hepatitis A, B, C", "High Blood Pressure"
];

const SignupPage = () => {
  const { signup } = useAppContext();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    address: '',
    date_of_birth: '',
    password: ''
  });
  
  const [medicalConditions, setMedicalConditions] = useState([]);
  const [error, setError] = useState('');

  // Listen for Chatbot filling out the form automatically
  useEffect(() => {
    const handleStorageChange = () => {
      const pending = localStorage.getItem('pending_medical_conditions');
      if (pending) {
        try {
          const aiConditions = JSON.parse(pending);
          // Only add conditions that exist in our common list (basic fuzzy match)
          const matchedConditions = [];
          aiConditions.forEach(aiCond => {
            const match = COMMON_CONDITIONS.find(c => c.toLowerCase().includes(aiCond.toLowerCase()));
            if (match && !medicalConditions.includes(match)) {
              matchedConditions.push(match);
            } else if (!match) {
               // If AI mentions something not in the list, just add it as a custom string
               matchedConditions.push(aiCond);
            }
          });
          
          if (matchedConditions.length > 0) {
            setMedicalConditions(prev => [...new Set([...prev, ...matchedConditions])]);
          }
          localStorage.removeItem('pending_medical_conditions');
        } catch (e) {}
      }
    };

    // Initial check
    handleStorageChange();
    
    // Listen for cross-tab or same-window storage updates from the bot
    window.addEventListener('storage', handleStorageChange);
    // Custom event just in case it's in the same window and storage event doesn't fire
    window.addEventListener('bot_medical_update', handleStorageChange);
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('bot_medical_update', handleStorageChange);
    };
  }, []);

  const handleChange = (e) => {
    setFormData({...formData, [e.target.name]: e.target.value});
  };

  const handleConditionToggle = (cond) => {
    if (medicalConditions.includes(cond)) {
      setMedicalConditions(medicalConditions.filter(c => c !== cond));
    } else {
      setMedicalConditions([...medicalConditions, cond]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    // In a real app, we would also submit medicalConditions to the backend here.
    // For this hackathon, we'll append it to the user object or just let the signup proceed.
    
    const success = await signup(formData);
    if (success) {
      navigate('/dashboard');
    } else {
      setError('Error creating account. Email might already be registered.');
    }
  };

  return (
    <div className="container animate-slide-up" style={{ maxWidth: '900px' }}>
      <div className="card" style={{ margin: '2rem auto', padding: '3rem', borderRadius: '12px', boxShadow: '0 10px 25px rgba(0,0,0,0.05)' }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <h2 style={{ fontSize: '2rem', color: '#0f172a', marginBottom: '0.5rem' }}>Patient Registration & Medical History</h2>
          <p style={{ color: '#64748b' }}>Please provide your details and medical history. You can also ask CareBot to assist you!</p>
        </div>
        
        {error && <div style={{ color: '#ef4444', marginBottom: '1.5rem', textAlign: 'center', background: '#fef2f2', padding: '12px', borderRadius: '8px', border: '1px solid #fca5a5' }}>{error}</div>}
        
        <form onSubmit={handleSubmit}>
          
          <h3 style={{ borderBottom: '2px solid #f1f5f9', paddingBottom: '10px', marginBottom: '20px', color: '#334155' }}>1. Personal Information</h3>
          <div style={{ display: 'flex', gap: '20px' }}>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label" style={{ fontWeight: '600' }}>First Name</label>
              <input type="text" name="first_name" className="form-control" value={formData.first_name} onChange={handleChange} required style={{ background: '#f8fafc' }}/>
            </div>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label" style={{ fontWeight: '600' }}>Last Name</label>
              <input type="text" name="last_name" className="form-control" value={formData.last_name} onChange={handleChange} required style={{ background: '#f8fafc' }}/>
            </div>
          </div>
          <div className="form-group">
            <label className="form-label" style={{ fontWeight: '600' }}>Email Address</label>
            <input type="email" name="email" className="form-control" value={formData.email} onChange={handleChange} required style={{ background: '#f8fafc' }}/>
          </div>
          <div className="form-group">
            <label className="form-label" style={{ fontWeight: '600' }}>Password</label>
            <input type="password" name="password" className="form-control" value={formData.password} onChange={handleChange} required style={{ background: '#f8fafc' }}/>
          </div>
          <div style={{ display: 'flex', gap: '20px' }}>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label" style={{ fontWeight: '600' }}>Date of Birth</label>
              <input type="date" name="date_of_birth" className="form-control" value={formData.date_of_birth} onChange={handleChange} required style={{ background: '#f8fafc' }}/>
            </div>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label" style={{ fontWeight: '600' }}>Phone Number</label>
              <input type="tel" name="phone" className="form-control" value={formData.phone} onChange={handleChange} required style={{ background: '#f8fafc' }}/>
            </div>
          </div>
          <div className="form-group">
            <label className="form-label" style={{ fontWeight: '600' }}>Home Address</label>
            <input type="text" name="address" className="form-control" value={formData.address} onChange={handleChange} required placeholder="123 Main St, City, State, ZIP" style={{ background: '#f8fafc' }}/>
          </div>

          <h3 style={{ borderBottom: '2px solid #f1f5f9', paddingBottom: '10px', marginBottom: '20px', marginTop: '30px', color: '#334155' }}>2. Medical History</h3>
          <p style={{ fontSize: '0.9rem', color: '#64748b', marginBottom: '15px' }}>
            Check any conditions you currently have or have been treated for in the past. 
            <strong style={{ color: '#0f766e', marginLeft: '5px' }}>Try telling CareBot "I have Asthma and Diabetes" to watch this auto-fill!</strong>
          </p>
          
          {/* Grid of Checkboxes */}
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', 
            gap: '12px',
            background: '#f8fafc',
            padding: '20px',
            borderRadius: '8px',
            border: '1px solid #e2e8f0'
          }}>
            {COMMON_CONDITIONS.map((cond, idx) => (
              <label key={idx} style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '0.95rem', color: '#334155' }}>
                <input 
                  type="checkbox" 
                  checked={medicalConditions.includes(cond)}
                  onChange={() => handleConditionToggle(cond)}
                  style={{ width: '18px', height: '18px', accentColor: '#0f766e', cursor: 'pointer' }}
                />
                {cond}
              </label>
            ))}
            {/* Render any custom conditions added by AI */}
            {medicalConditions.filter(c => !COMMON_CONDITIONS.includes(c)).map((customCond, idx) => (
              <label key={`custom-${idx}`} style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '0.95rem', color: '#0f766e', fontWeight: 'bold' }}>
                <input 
                  type="checkbox" 
                  checked={true}
                  onChange={() => handleConditionToggle(customCond)}
                  style={{ width: '18px', height: '18px', accentColor: '#0f766e', cursor: 'pointer' }}
                />
                {customCond} (Added by AI)
              </label>
            ))}
          </div>

          <button type="submit" style={{ 
            width: '100%', padding: '16px', fontSize: '1.1rem', marginTop: '30px', 
            background: 'linear-gradient(135deg, #0f766e 0%, #0d9488 100%)', 
            color: 'white', border: 'none', borderRadius: '8px', fontWeight: 'bold', cursor: 'pointer',
            boxShadow: '0 4px 10px rgba(15, 118, 110, 0.2)'
          }}>
            Complete Registration
          </button>
        </form>
        
        <div style={{ textAlign: 'center', marginTop: '2rem', color: '#64748b' }}>
          Already have an account? <Link to="/login" style={{ fontWeight: 'bold', color: '#0f766e', textDecoration: 'none' }}>Log in here</Link>
        </div>
      </div>
    </div>
  );
};

export default SignupPage;
