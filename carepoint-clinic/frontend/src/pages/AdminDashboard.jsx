import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAppContext } from '../context/AppContext';
import { Search, CheckCircle, XCircle, Users, Calendar, TrendingUp, AlertTriangle, FileText, Award, Clock, ArrowRight, RotateCcw } from 'lucide-react';
import { Link } from 'react-router-dom';
import WeatherWidget from '../components/WeatherWidget';
import CalendarPage from './CalendarPage';

const AdminDashboard = () => {
  const { user, API_URL } = useAppContext();
  const [allAppointments, setAllAppointments] = useState([]);
  const [allPatients, setAllPatients] = useState([]);
  const [stats, setStats] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [manualPoints, setManualPoints] = useState({ patientId: '', points: 10, reason: 'Manual adjustment' });

  useEffect(() => {
    if (user?.role === 'admin') {
      fetchAdminData();
    }
  }, [user]);

  const fetchAdminData = async () => {
    try {
      const [apptRes, userRes, statsRes] = await Promise.all([
        axios.get(`${API_URL}/appointments/`),
        axios.get(`${API_URL}/users/`),
        axios.get(`${API_URL}/admin/stats`)
      ]);
      setAllAppointments(apptRes.data);
      setAllPatients(userRes.data.filter(u => u.role === 'patient'));
      setStats(statsRes.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleManualPoints = async (e) => {
    e.preventDefault();
    if (!manualPoints.patientId) return alert("Select a patient");
    try {
      await axios.post(`${API_URL}/points/`, {
        points_added: manualPoints.points,
        reason: manualPoints.reason,
        added_by_staff_id: user.id,
        patient_id: manualPoints.patientId
      });
      alert(`Successfully added ${manualPoints.points} points.`);
      setManualPoints({ patientId: '', points: 10, reason: 'Manual adjustment' });
      fetchAdminData();
    } catch (err) {
      console.error(err);
      alert("Error adding points manually.");
    }
  };

  const handleUpdateStatus = async (apptId, status, addPoints = 0, patientId) => {
    if (window.confirm(`Are you sure you want to mark this appointment as ${status}?`)) {
      try {
        await axios.put(`${API_URL}/appointments/${apptId}/status?status=${status}`);
        
        if (addPoints > 0) {
          try {
            await axios.post(`${API_URL}/points/`, {
              points_added: addPoints,
              reason: `Showed up - Attendance`,
              appointment_id: apptId,
              added_by_staff_id: user.id,
              patient_id: patientId
            });
            alert(`Marked as ${status} and ${addPoints} points added!`);
          } catch (ptErr) {
            alert(`Marked as ${status}. Points may have already been awarded.`);
          }
        } else {
          alert(`Appointment marked as ${status}.`);
        }
        
        fetchAdminData();
      } catch (err) {
        console.error(err);
        alert(err.response?.data?.detail || "Error updating appointment.");
      }
    }
  };

  if (!user || user.role !== 'admin') {
    return (
      <div className="container">
        <div className="card" style={{ textAlign: 'center' }}>
          <h2>Access Denied</h2>
          <p>Please log in as an administrator to view this dashboard.</p>
        </div>
      </div>
    );
  }

  const filteredAppts = allAppointments.filter(a => 
    a.appointment_type.toLowerCase().includes(searchTerm.toLowerCase()) || 
    (a.patient && (`${a.patient.first_name} ${a.patient.last_name}`).toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const statCards = stats ? [
    { icon: <Users size={24} />, label: 'Total Patients', value: stats.total_patients, color: '#005f73', bg: '#f0f9ff' },
    { icon: <Calendar size={24} />, label: "Today's Appointments", value: stats.today_appointments, color: '#0284c7', bg: '#e0f2fe' },
    { icon: <Clock size={24} />, label: 'Upcoming', value: stats.upcoming_appointments, color: '#f59e0b', bg: '#fef3c7' },
    { icon: <TrendingUp size={24} />, label: 'Completed', value: stats.completed_appointments, color: '#16a34a', bg: '#f0fdf4' },
    { icon: <AlertTriangle size={24} />, label: 'No-Shows', value: stats.noshow_appointments, color: '#dc2626', bg: '#fef2f2' },
    { icon: <FileText size={24} />, label: 'Pending Forms', value: stats.pending_medical_forms, color: '#9333ea', bg: '#faf5ff' },
    { icon: <Award size={24} />, label: 'Points Awarded', value: stats.total_points_awarded, color: '#0d9488', bg: '#f0fdfa' },
  ] : [];

  return (
    <div className="container animate-slide-up">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h1>Admin Dashboard</h1>
          <p>Overview of clinic operations, appointments, and patient management.</p>
        </div>
      </div>

      {/* Stat Cards */}
      {stats && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '16px', marginBottom: '2rem' }}>
          {statCards.map((card, idx) => (
            <div key={idx} className="card" style={{ padding: '20px', textAlign: 'center', background: card.bg, border: 'none' }}>
              <div style={{ color: card.color, marginBottom: '8px' }}>{card.icon}</div>
              <div style={{ fontSize: '2rem', fontWeight: '800', color: card.color, lineHeight: '1' }}>{card.value}</div>
              <div style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '6px', fontWeight: '600' }}>{card.label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Quick Actions */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px', marginBottom: '2rem' }}>
        <Link to="/admin/book" className="card" style={{ textDecoration: 'none', padding: '20px', display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer', border: '2px solid transparent', transition: 'border-color 0.2s' }}
          onMouseEnter={e => e.currentTarget.style.borderColor = '#005f73'}
          onMouseLeave={e => e.currentTarget.style.borderColor = 'transparent'}
        >
          <Calendar size={24} color="#005f73" />
          <div>
            <div style={{ fontWeight: '700', color: '#0f172a' }}>Book Appointment</div>
            <div style={{ fontSize: '0.8rem', color: '#64748b' }}>Schedule for a patient</div>
          </div>
          <ArrowRight size={16} color="#94a3b8" style={{ marginLeft: 'auto' }} />
        </Link>
        <Link to="/admin/patients" className="card" style={{ textDecoration: 'none', padding: '20px', display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer', border: '2px solid transparent', transition: 'border-color 0.2s' }}
          onMouseEnter={e => e.currentTarget.style.borderColor = '#0284c7'}
          onMouseLeave={e => e.currentTarget.style.borderColor = 'transparent'}
        >
          <Users size={24} color="#0284c7" />
          <div>
            <div style={{ fontWeight: '700', color: '#0f172a' }}>Patient Database</div>
            <div style={{ fontSize: '0.8rem', color: '#64748b' }}>View all patients</div>
          </div>
          <ArrowRight size={16} color="#94a3b8" style={{ marginLeft: 'auto' }} />
        </Link>
        <Link to="/admin/calendar" className="card" style={{ textDecoration: 'none', padding: '20px', display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer', border: '2px solid transparent', transition: 'border-color 0.2s' }}
          onMouseEnter={e => e.currentTarget.style.borderColor = '#f59e0b'}
          onMouseLeave={e => e.currentTarget.style.borderColor = 'transparent'}
        >
          <Clock size={24} color="#f59e0b" />
          <div>
            <div style={{ fontWeight: '700', color: '#0f172a' }}>View Calendar</div>
            <div style={{ fontSize: '0.8rem', color: '#64748b' }}>Scheduling overview</div>
          </div>
          <ArrowRight size={16} color="#94a3b8" style={{ marginLeft: 'auto' }} />
        </Link>
        <Link to="/medical-history" className="card" style={{ textDecoration: 'none', padding: '20px', display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer', border: '2px solid transparent', transition: 'border-color 0.2s' }}
          onMouseEnter={e => e.currentTarget.style.borderColor = '#9333ea'}
          onMouseLeave={e => e.currentTarget.style.borderColor = 'transparent'}
        >
          <FileText size={24} color="#9333ea" />
          <div>
            <div style={{ fontWeight: '700', color: '#0f172a' }}>Medical History</div>
            <div style={{ fontSize: '0.8rem', color: '#64748b' }}>View & manage forms</div>
          </div>
          <ArrowRight size={16} color="#94a3b8" style={{ marginLeft: 'auto' }} />
        </Link>
      </div>

      <WeatherWidget />

      <div className="card" style={{ marginBottom: '2rem' }}>
        <CalendarPage isWidget={true} />
      </div>

      {/* Appointments Table */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h3 style={{ margin: 0 }}>Appointment Management</h3>
          <Link to="/admin/book" className="btn btn-secondary" style={{ textDecoration: 'none', padding: '8px 16px', fontSize: '0.85rem' }}>
            + New Appointment
          </Link>
        </div>
        <div style={{ display: 'flex', gap: '10px', marginBottom: '1.5rem' }}>
          <div style={{ position: 'relative', flex: 1 }}>
            <Search size={18} style={{ position: 'absolute', top: '12px', left: '12px', color: 'var(--color-text-muted)' }} />
            <input 
              type="text" 
              className="form-control" 
              placeholder="Search patients by name or appointment type..." 
              style={{ paddingLeft: '40px' }}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>

        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Patient Name</th>
                <th>Date / Time</th>
                <th>Type</th>
                <th>Provider</th>
                <th>Status</th>
                <th>Staff Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredAppts.map(appt => {
                let ptsToAdd = 10;
                if (appt.appointment_type.includes('Preventive') || appt.appointment_type.includes('Annual')) ptsToAdd = 15;

                return (
                  <tr key={appt.id}>
                    <td style={{ fontWeight: 'bold' }}>{appt.patient ? `${appt.patient.first_name} ${appt.patient.last_name}` : `Patient ID: ${appt.patient_id}`}</td>
                    <td>{appt.appointment_date} {appt.appointment_time}</td>
                    <td>{appt.appointment_type}</td>
                    <td>{appt.provider || 'N/A'}</td>
                    <td>
                      <span className={`badge ${appt.status === 'Completed' ? 'badge-success' : (appt.status === 'No Show' ? 'badge-danger' : appt.status === 'Cancelled' ? 'badge-info' : 'badge-warning')}`}>
                        {appt.status}
                      </span>
                    </td>
                    <td>
                      {appt.status === 'Pending' || appt.status === 'Confirmed' ? (
                        <div style={{ display: 'flex', gap: '5px', flexWrap: 'wrap' }}>
                          <button 
                            className="btn btn-outline" 
                            style={{ padding: '5px 8px', fontSize: '0.78rem' }}
                            onClick={() => handleUpdateStatus(appt.id, 'Completed', ptsToAdd, appt.patient_id)}
                          >
                            <CheckCircle size={13} style={{ verticalAlign: 'middle' }}/> Showed Up +{ptsToAdd}
                          </button>
                          <button 
                            className="btn btn-outline" 
                            style={{ padding: '5px 8px', fontSize: '0.78rem', borderColor: '#dc2626', color: '#dc2626' }}
                            onClick={() => handleUpdateStatus(appt.id, 'No Show', 0, appt.patient_id)}
                          >
                            <XCircle size={13} style={{ verticalAlign: 'middle' }}/> No Show
                          </button>
                          <button 
                            className="btn btn-outline" 
                            style={{ padding: '5px 8px', fontSize: '0.78rem', borderColor: '#9ca3af', color: '#9ca3af' }}
                            onClick={() => handleUpdateStatus(appt.id, 'Cancelled', 0, appt.patient_id)}
                          >
                            Cancel
                          </button>
                          <button 
                            className="btn btn-outline" 
                            style={{ padding: '5px 8px', fontSize: '0.78rem', borderColor: '#c084fc', color: '#9333ea' }}
                            onClick={() => handleUpdateStatus(appt.id, 'Rescheduled', 0, appt.patient_id)}
                          >
                            <RotateCcw size={13} style={{ verticalAlign: 'middle' }}/> Reschedule
                          </button>
                        </div>
                      ) : (
                        <span style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem' }}>Action Completed</span>
                      )}
                    </td>
                  </tr>
                )
              })}
              {filteredAppts.length === 0 && (
                <tr><td colSpan="6" style={{ textAlign: 'center' }}>No appointments found.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Manual Points */}
      <div className="card" style={{ marginTop: '2rem' }}>
        <h3>Manual Point Assignment</h3>
        <p style={{ color: 'var(--color-text-muted)', marginBottom: '1rem' }}>Award or adjust points for any patient.</p>
        <form onSubmit={handleManualPoints} style={{ display: 'flex', gap: '15px', alignItems: 'flex-end', flexWrap: 'wrap' }}>
          <div className="form-group" style={{ flex: 1, minWidth: '200px' }}>
            <label className="form-label">Select Patient</label>
            <select className="form-control" value={manualPoints.patientId} onChange={(e) => setManualPoints({...manualPoints, patientId: e.target.value})} required>
              <option value="">-- Choose Patient --</option>
              {allPatients.map(p => (
                <option key={p.id} value={p.id}>{p.first_name} {p.last_name} ({p.email})</option>
              ))}
            </select>
          </div>
          <div className="form-group" style={{ width: '100px' }}>
            <label className="form-label">Points</label>
            <input type="number" className="form-control" value={manualPoints.points} onChange={(e) => setManualPoints({...manualPoints, points: parseInt(e.target.value)})} required />
          </div>
          <div className="form-group" style={{ flex: 1, minWidth: '200px' }}>
            <label className="form-label">Reason</label>
            <input type="text" className="form-control" value={manualPoints.reason} onChange={(e) => setManualPoints({...manualPoints, reason: e.target.value})} required />
          </div>
          <button type="submit" className="btn btn-secondary" style={{ marginBottom: '15px', height: '42px' }}>Award Points</button>
        </form>
      </div>
    </div>
  );
};

export default AdminDashboard;
