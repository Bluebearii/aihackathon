import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAppContext } from '../context/AppContext';
import axios from 'axios';

const LoginPage = () => {
  const { login, API_URL } = useAppContext();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({...formData, [e.target.name]: e.target.value});
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    const userResult = await login(formData.email, formData.password);
    if (userResult) {
      if (userResult.role === 'admin') {
        navigate('/admin');
      } else {
        try {
          const res = await axios.get(`${API_URL}/medical-history/${userResult.id}`);
          if (res.data && res.data.completed_at) {
            const completedAt = new Date(res.data.completed_at);
            const sixMonthsAgo = new Date();
            sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6);
            
            if (completedAt < sixMonthsAgo) {
              navigate('/medical-history');
            } else {
              navigate('/dashboard');
            }
          } else {
            navigate('/medical-history');
          }
        } catch (err) {
          // 404 or other error means no medical history found
          navigate('/medical-history');
        }
      }
    } else {
      setError('Invalid email or password.');
    }
  };

  return (
    <div className="container animate-slide-up">
      <div className="card" style={{ maxWidth: '400px', margin: '4rem auto', padding: '2rem' }}>
        <h2 style={{ textAlign: 'center', marginBottom: '1.5rem' }}>Login to Care Flow AI</h2>
        {error && <div style={{ color: 'var(--color-error)', marginBottom: '1rem', textAlign: 'center', background: '#f8d7da', padding: '10px', borderRadius: '5px' }}>{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Email</label>
            <input type="email" name="email" className="form-control" value={formData.email} onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label className="form-label">Password</label>
            <input type="password" name="password" className="form-control" value={formData.password} onChange={handleChange} required />
          </div>
          <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '12px', fontSize: '1.1rem', marginTop: '1rem' }}>Login</button>
        </form>
        <div style={{ textAlign: 'center', marginTop: '1.5rem' }}>
          Don't have an account? <Link to="/signup" style={{ fontWeight: 'bold' }}>Sign Up</Link>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
