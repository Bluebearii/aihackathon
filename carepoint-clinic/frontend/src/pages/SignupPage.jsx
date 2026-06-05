import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAppContext } from '../context/AppContext';

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
    const success = await signup(formData);
    if (success) {
      navigate('/dashboard');
    } else {
      setError('Error creating account. Email might already be registered.');
    }
  };

  return (
    <div className="container animate-slide-up">
      <div className="card" style={{ maxWidth: '600px', margin: '2rem auto', padding: '2rem' }}>
        <h2 style={{ textAlign: 'center', marginBottom: '1.5rem' }}>Patient Sign Up</h2>
        {error && <div style={{ color: 'var(--color-error)', marginBottom: '1rem', textAlign: 'center', background: '#f8d7da', padding: '10px', borderRadius: '5px' }}>{error}</div>}
        <form onSubmit={handleSubmit}>
          <div style={{ display: 'flex', gap: '15px' }}>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label">First Name</label>
              <input type="text" name="first_name" className="form-control" value={formData.first_name} onChange={handleChange} required />
            </div>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label">Last Name</label>
              <input type="text" name="last_name" className="form-control" value={formData.last_name} onChange={handleChange} required />
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">Email</label>
            <input type="email" name="email" className="form-control" value={formData.email} onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label className="form-label">Password</label>
            <input type="password" name="password" className="form-control" value={formData.password} onChange={handleChange} required />
          </div>
          <div style={{ display: 'flex', gap: '15px' }}>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label">Date of Birth</label>
              <input type="date" name="date_of_birth" className="form-control" value={formData.date_of_birth} onChange={handleChange} required />
            </div>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label">Phone Number</label>
              <input type="tel" name="phone" className="form-control" value={formData.phone} onChange={handleChange} required />
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">Home Address</label>
            <input type="text" name="address" className="form-control" value={formData.address} onChange={handleChange} required placeholder="123 Main St, City, State, ZIP" />
          </div>
          <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '12px', fontSize: '1.1rem', marginTop: '1rem' }}>Create Account</button>
        </form>
        <div style={{ textAlign: 'center', marginTop: '1.5rem' }}>
          Already have an account? <Link to="/login" style={{ fontWeight: 'bold' }}>Login</Link>
        </div>
      </div>
    </div>
  );
};

export default SignupPage;
