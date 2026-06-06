import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useAppContext } from '../context/AppContext';

const BookingPage = () => {
  const { bookAppointment } = useAppContext();
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const prefillDate = queryParams.get('date') || '';
  const prefillTime = queryParams.get('time') || '';

  const [submitted, setSubmitted] = useState(false);
  const [formData, setFormData] = useState({
    appointment_type: 'Annual Checkup',
    appointment_date: prefillDate,
    appointment_time: prefillTime,
    reason_for_visit: '',
    insurance_provider: ''
  });

  const handleChange = (e) => {
    setFormData({...formData, [e.target.name]: e.target.value});
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const success = await bookAppointment(formData);
    if (success) {
      setSubmitted(true);
    } else {
      alert("There was an error booking your appointment. Please make sure you are logged in as a patient.");
    }
  };

  if (submitted) {
    return (
      <div className="container animate-pop">
        <div className="card" style={{ textAlign: 'center', padding: '4rem 2rem', maxWidth: '600px', margin: '0 auto' }}>
          <div style={{ background: '#d4edda', width: '80px', height: '80px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1.5rem auto' }}>
            <span style={{ fontSize: '2rem' }}>✓</span>
          </div>
          <h2>Request Submitted!</h2>
          <p style={{ fontSize: '1.2rem', color: 'var(--color-primary)' }}>Your appointment request has been submitted. Our office will confirm your appointment soon.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container animate-slide-up">
      <div className="card" style={{ maxWidth: '600px', margin: '0 auto' }}>
        <h2 style={{ textAlign: 'center', marginBottom: '2rem' }}>Book an Appointment</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Appointment Type</label>
            <select name="appointment_type" className="form-control" value={formData.appointment_type} onChange={handleChange} required>
              <option value="Annual Checkup">Annual Checkup</option>
              <option value="Eye Exam">Eye Exam or General Health Exam</option>
              <option value="Follow-up Appointment">Follow-up Appointment</option>
              <option value="Lab Result Discussion">Lab Result Discussion</option>
              <option value="Preventive Care Visit">Preventive Care Visit</option>
              <option value="Insurance Verification">Insurance Verification</option>
            </select>
          </div>
          <div style={{ display: 'flex', gap: '15px' }}>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label">Preferred Date</label>
              <input type="date" name="appointment_date" className="form-control" value={formData.appointment_date} onChange={handleChange} required />
            </div>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label">Preferred Time</label>
              <input type="time" name="appointment_time" className="form-control" value={formData.appointment_time} onChange={handleChange} required />
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">Reason for Visit</label>
            <textarea name="reason_for_visit" className="form-control" rows="3" value={formData.reason_for_visit} onChange={handleChange} required></textarea>
          </div>
          <div className="form-group">
            <label className="form-label">Insurance Provider</label>
            <input type="text" name="insurance_provider" className="form-control" placeholder="e.g. Medicare, BlueCross" value={formData.insurance_provider} onChange={handleChange} required />
          </div>
          <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '15px', fontSize: '1.1rem', marginTop: '1rem' }}>Submit Request</button>
        </form>
      </div>
    </div>
  );
};

export default BookingPage;
