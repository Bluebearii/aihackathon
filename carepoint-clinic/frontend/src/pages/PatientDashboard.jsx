import React from 'react';
import { useAppContext } from '../context/AppContext';
import { History, Calendar } from 'lucide-react';

const PatientDashboard = () => {
  const { user, appointments, points } = useAppContext();

  if (!user || user.role !== 'patient') {
    return (
      <div className="container">
        <div className="card" style={{ textAlign: 'center' }}>
          <h2>Access Denied</h2>
          <p>Please log in as a patient to view this dashboard.</p>
        </div>
      </div>
    );
  }

  const totalPoints = points.reduce((sum, p) => sum + p.points_added, 0);
  const nextRewardTier = totalPoints < 100 ? 100 : (totalPoints < 200 ? 200 : 300);
  const pointsAway = nextRewardTier - totalPoints;
  const progressPercent = Math.min((totalPoints / nextRewardTier) * 100, 100);

  return (
    <div className="container animate-slide-up">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1>Welcome, {user.first_name} {user.last_name}</h1>
        <button className="btn btn-outline">Update Contact Info</button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem', marginBottom: '2rem' }}>
        {/* Points Card */}
        <div className="card" style={{ background: 'var(--color-primary)', color: 'white' }}>
          <h3 style={{ color: 'white', display: 'flex', justifyContent: 'space-between' }}>
            Current Points <span>{totalPoints}</span>
          </h3>
          <div className="progress-container" style={{ background: 'rgba(255,255,255,0.2)' }}>
            <div className="progress-bar" style={{ width: `${progressPercent}%`, background: 'var(--color-accent)' }}></div>
          </div>
          <p style={{ color: '#e0fbfc', margin: 0 }}>Next Reward: {nextRewardTier} points</p>
          <p style={{ color: '#e0fbfc', margin: 0 }}><strong>{pointsAway} points away</strong> from your next reward!</p>
        </div>

        {/* Upcoming Appointment */}
        <div className="card">
          <h3>Upcoming Appointment</h3>
          {appointments.filter(a => a.status === 'Pending' || a.status === 'Confirmed').length > 0 ? (
            appointments.filter(a => a.status === 'Pending' || a.status === 'Confirmed').map(appt => (
              <div key={appt.id} style={{ borderBottom: '1px solid var(--color-border)', paddingBottom: '10px', marginBottom: '10px' }}>
                <p style={{ fontWeight: 'bold', margin: 0, color: 'var(--color-primary)' }}>{appt.appointment_type}</p>
                <p style={{ margin: 0 }}><Calendar size={14}/> {appt.appointment_date} at {appt.appointment_time}</p>
                <span className={`badge ${appt.status === 'Confirmed' ? 'badge-success' : 'badge-warning'}`} style={{ marginTop: '5px' }}>{appt.status}</span>
              </div>
            ))
          ) : (
            <p>No upcoming appointments.</p>
          )}
        </div>
      </div>

      {/* Point Activity Log */}
      <div className="card">
        <h3><History size={20} style={{ verticalAlign: 'middle', marginRight: '8px' }}/> Recent Point Activity</h3>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Reason / Appointment</th>
                <th>Points Added</th>
              </tr>
            </thead>
            <tbody>
              {points.length > 0 ? points.map((p, idx) => (
                <tr key={idx}>
                  <td>{new Date(p.created_at).toLocaleDateString()}</td>
                  <td>{p.reason}</td>
                  <td style={{ color: 'var(--color-success)', fontWeight: 'bold' }}>+{p.points_added} pts</td>
                </tr>
              )) : (
                <tr>
                  <td colSpan="3" style={{ textAlign: 'center' }}>No point activity yet. Attend your next appointment to earn points!</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        <div style={{ textAlign: 'center', marginTop: '1rem' }}>
          <button className="btn btn-outline">View Full Appointment History</button>
        </div>
      </div>
    </div>
  );
};

export default PatientDashboard;
