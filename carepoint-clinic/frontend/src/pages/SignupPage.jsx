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
  
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({...formData, [e.target.name]: e.target.value});
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    const userResult = await signup(formData);
    if (userResult) {
      navigate('/medical-history'); // Redirect new users to complete their medical history
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
