import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAppContext } from '../context/AppContext';
import { useNavigate, useLocation } from 'react-router-dom';

const APPOINTMENT_TYPES = [
  'Annual Eye Exam', 'Contact Lens Exam', 'Follow-up Visit',
  'Medical Office Visit', 'New Patient Visit', 'Emergency Visit', 'Consultation'
];
const PROVIDERS = ['Dr. Smith', 'Dr. Patel', 'Dr. Lee'];

const AdminBooking = () => {
  const { user, API_URL } = useAppContext();
  const navigate = useNavigate();
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const prefillDate = queryParams.get('date') || '';

  const [patients, setPatients] = useState([]);
  const [submitted, setSubmitted] = useState(false);
  const [formData, setFormData] = useState({
    patient_id: '',
    appointment_type: 'Annual Eye Exam',
    appointment_date: prefillDate,
    appointment_time: '',
    reason_for_visit: '',
    provider: 'Dr. Smith',
    notes: '',
    insurance_provider: '',
    status: 'Confirmed'
  });

  useEffect(() => {
    let intervalId;
    if (user?.role === 'admin') {
      const fetchPatients = () => {
        axios.get(`${API_URL}/patients/`)
          .then(res => setPatients(res.data))
          .catch(console.error);
      };
      
      fetchPatients(); // initial fetch
      intervalId = setInterval(fetchPatients, 5000); // Poll every 5s
    }
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [user]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Auto-fill insurance when patient is selected
    if (name === 'patient_id') {
      const selected = patients.find(p => p.id === parseInt(value));
      if (selected) {
        setFormData(prev => ({ ...prev, [name]: value, insurance_provider: selected.insurance_provider || '' }));
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/appointments/`, {
        patient_id: parseInt(formData.patient_id),
        appointment_type: formData.appointment_type,
        appointment_date: formData.appointment_date,
        appointment_time: formData.appointment_time,
        reason_for_visit: formData.reason_for_visit,
        insurance_provider: formData.insurance_provider,
        status: formData.status,
        provider: formData.provider,
        notes: formData.notes || null
      });
      setSubmitted(true);
    } catch (err) {
      alert(err.response?.data?.detail || 'Error booking appointment.');
    }
  };

  if (!user || user.role !== 'admin') {
    return (
      <div className="container">
        <div className="card" style={{ textAlign: 'center' }}>
          <h2>Access Denied</h2>
          <p>Admin access required.</p>
        </div>
      </div>
    );
  }

  if (submitted) {
    return (
      <div className="container animate-pop">
        <div className="card" style={{ textAlign: 'center', padding: '4rem 2rem', maxWidth: '600px', margin: '0 auto' }}>
          <div style={{ background: '#d4edda', width: '80px', height: '80px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1.5rem auto', fontSize: '2rem' }}>
            &#10003;
          </div>
          <h2>Appointment Booked!</h2>
          <p style={{ fontSize: '1.1rem', color: '#005f73' }}>The appointment has been scheduled successfully.</p>
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', marginTop: '1.5rem' }}>
            <button className="btn btn-primary" onClick={() => { setSubmitted(false); setFormData({ patient_id: '', appointment_type: 'Annual Eye Exam', appointment_date: '', appointment_time: '', reason_for_visit: '', provider: 'Dr. Smith', notes: '', insurance_provider: '', status: 'Confirmed' }); }}>
              Book Another
            </button>
            <button className="btn btn-outline" onClick={() => navigate('/admin/calendar')}>
              View Calendar
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container animate-slide-up">
      <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <button onClick={() => navigate('/admin/calendar')} className="btn btn-outline" style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '6px 12px' }}>
          <span style={{ fontSize: '1.2rem', lineHeight: '1' }}>&lsaquo;</span> Back to Calendar
        </button>
      </div>
      <div style={{ marginBottom: '2rem' }}>
        <h1>Book Appointment</h1>
        <p>Schedule an appointment for an existing patient.</p>
      </div>

      <div className="card" style={{ maxWidth: '700px', margin: '0 auto' }}>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Select Patient *</label>
            <select name="patient_id" className="form-control" value={formData.patient_id} onChange={handleChange} required>
              <option value="">-- Choose Patient --</option>
              {patients.map(p => (
                <option key={p.id} value={p.id}>{p.first_name} {p.last_name} — {p.email}</option>
              ))}
            </select>
          </div>

          <div style={{ display: 'flex', gap: '15px' }}>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label">Appointment Type *</label>
              <select name="appointment_type" className="form-control" value={formData.appointment_type} onChange={handleChange} required>
                {APPOINTMENT_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label">Provider *</label>
              <select name="provider" className="form-control" value={formData.provider} onChange={handleChange} required>
                {PROVIDERS.map(p => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '15px' }}>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label">Date *</label>
              <input type="date" name="appointment_date" className="form-control" value={formData.appointment_date} onChange={handleChange} required />
            </div>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label">Time *</label>
              <input type="time" name="appointment_time" className="form-control" value={formData.appointment_time} onChange={handleChange} required />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Reason for Visit *</label>
            <textarea name="reason_for_visit" className="form-control" rows="3" value={formData.reason_for_visit} onChange={handleChange} required></textarea>
          </div>

          <div style={{ display: 'flex', gap: '15px' }}>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label">Insurance Provider</label>
              <input type="text" name="insurance_provider" className="form-control" value={formData.insurance_provider} onChange={handleChange} placeholder="Auto-filled from patient" />
            </div>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label">Status</label>
              <select name="status" className="form-control" value={formData.status} onChange={handleChange}>
                <option value="Pending">Pending</option>
                <option value="Confirmed">Confirmed</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Notes (optional)</label>
            <textarea name="notes" className="form-control" rows="2" value={formData.notes} onChange={handleChange} placeholder="Additional notes for this appointment..."></textarea>
          </div>

          <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '15px', fontSize: '1.1rem', marginTop: '1rem' }}>
            Book Appointment
          </button>
        </form>
      </div>
    </div>
  );
};

export default AdminBooking;
