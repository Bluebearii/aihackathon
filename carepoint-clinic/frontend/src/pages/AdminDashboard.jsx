import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAppContext } from '../context/AppContext';
import { Search, CheckCircle, XCircle } from 'lucide-react';
import WeatherWidget from '../components/WeatherWidget';

const AdminDashboard = () => {
  const { user, API_URL } = useAppContext();
  const [allAppointments, setAllAppointments] = useState([]);
  const [allPatients, setAllPatients] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [manualPoints, setManualPoints] = useState({ patientId: '', points: 10, reason: 'Manual adjustment' });

  useEffect(() => {
    if (user?.role === 'admin') {
      fetchAdminData();
    }
  }, [user]);

  const fetchAdminData = async () => {
    try {
      const apptRes = await axios.get(`${API_URL}/appointments/`);
      setAllAppointments(apptRes.data);
      const userRes = await axios.get(`${API_URL}/users/`);
      setAllPatients(userRes.data.filter(u => u.role === 'patient'));
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
          // Add points
          await axios.post(`${API_URL}/points/`, {
            points_added: addPoints,
            reason: `Attendance for ${status}`,
            appointment_id: apptId,
            added_by_staff_id: user.id,
            patient_id: patientId
          });
          alert(`Success! Marked as ${status} and ${addPoints} points added to patient account.`);
        } else {
          alert(`Appointment marked as ${status}. No points added.`);
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

  return (
    <div className="container animate-slide-up">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h1>Staff & Admin Dashboard</h1>
          <p>Manage today's appointments, confirm patient attendance, and add points securely.</p>
        </div>
        <button className="btn btn-secondary">Export Attendance Report</button>
      </div>

      <WeatherWidget />

      <div className="card">
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
                <th>Time / Date</th>
                <th>Appointment Type</th>
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
                    <td>
                      <span className={`badge ${appt.status === 'Completed' ? 'badge-success' : (appt.status === 'No Show' ? 'badge-danger' : 'badge-warning')}`}>
                        {appt.status}
                      </span>
                    </td>
                    <td>
                      {appt.status === 'Pending' || appt.status === 'Confirmed' ? (
                        <div style={{ display: 'flex', gap: '5px' }}>
                          <button 
                            className="btn btn-outline" 
                            style={{ padding: '6px 10px', fontSize: '0.85rem' }}
                            onClick={() => handleUpdateStatus(appt.id, 'Completed', ptsToAdd, appt.patient_id)}
                          >
                            <CheckCircle size={14} style={{ verticalAlign: 'middle' }}/> Check In & +{ptsToAdd} pts
                          </button>
                          <button 
                            className="btn btn-outline" 
                            style={{ padding: '6px 10px', fontSize: '0.85rem', borderColor: 'var(--color-error)', color: 'var(--color-error)' }}
                            onClick={() => handleUpdateStatus(appt.id, 'No Show', 0, appt.patient_id)}
                          >
                            <XCircle size={14} style={{ verticalAlign: 'middle' }}/> No Show
                          </button>
                        </div>
                      ) : (
                        <span style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem' }}>Action Completed</span>
                      )}
                    </td>
                  </tr>
                )
              })}
              {filteredAppts.length === 0 && (
                <tr><td colSpan="5" style={{ textAlign: 'center' }}>No appointments found.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
      <div className="card" style={{ marginTop: '2rem' }}>
        <h3>Manual Point Assignment</h3>
        <p style={{ color: 'var(--color-text-muted)', marginBottom: '1rem' }}>Use this tool to award points to any patient for a demonstration, without needing a scheduled appointment.</p>
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
