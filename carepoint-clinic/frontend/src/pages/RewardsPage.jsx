import React from 'react';

const RewardsPage = () => {
  return (
    <div className="container animate-slide-up">
      <div className="card" style={{ textAlign: 'center', background: 'var(--color-primary)', color: 'white' }}>
        <h1 style={{ color: 'white' }}>WeCarePeople Points System</h1>
        <p style={{ color: '#e0fbfc', fontSize: '1.1rem', maxWidth: '800px', margin: '0 auto' }}>
          WeCarePeople Points are our way of encouraging patients to stay consistent with their appointments. Points are added only after a patient arrives at the office and the visit is confirmed by staff.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginTop: '3rem' }}>
        <div className="card">
          <h3>How to Earn Points</h3>
          <p>Patients earn points <strong>only when they show up</strong> to the office for a scheduled appointment.</p>
          <ul style={{ listStyle: 'none', padding: 0, marginTop: '1.5rem' }}>
            <li style={{ padding: '10px 0', borderBottom: '1px solid var(--color-border)', display: 'flex', justifyContent: 'space-between' }}>
              <span>Standard visit check-in</span> <strong style={{ color: 'var(--color-success)' }}>+10 pts</strong>
            </li>
            <li style={{ padding: '10px 0', borderBottom: '1px solid var(--color-border)', display: 'flex', justifyContent: 'space-between' }}>
              <span>Follow-up visit</span> <strong style={{ color: 'var(--color-success)' }}>+10 pts</strong>
            </li>
            <li style={{ padding: '10px 0', borderBottom: '1px solid var(--color-border)', display: 'flex', justifyContent: 'space-between' }}>
              <span>Preventive annual visit</span> <strong style={{ color: 'var(--color-success)' }}>+15 pts</strong>
            </li>
            <li style={{ padding: '10px 0', borderBottom: '1px solid var(--color-border)', display: 'flex', justifyContent: 'space-between', color: 'var(--color-text-muted)' }}>
              <span>Same-day cancellation (with notice)</span> <strong>0 pts</strong>
            </li>
            <li style={{ padding: '10px 0', borderBottom: '1px solid var(--color-border)', display: 'flex', justifyContent: 'space-between', color: 'var(--color-error)' }}>
              <span>No-show appointment</span> <strong>0 pts</strong>
            </li>
          </ul>
        </div>

        <div className="card">
          <h3>Reward Examples</h3>
          <div style={{ marginTop: '1.5rem' }}>
            <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '15px' }}>
              <div style={{ background: '#e9ecef', padding: '10px 15px', borderRadius: '8px', fontWeight: 'bold' }}>100 pts</div>
              <div>Small clinic gift or wellness item (e.g. water bottle, tote bag).</div>
            </div>
            <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '15px' }}>
              <div style={{ background: '#e9ecef', padding: '10px 15px', borderRadius: '8px', fontWeight: 'bold' }}>200 pts</div>
              <div>Discount on eligible non-medical retail items (like vitamins or optical accessories, if allowed).</div>
            </div>
            <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '15px' }}>
              <div style={{ background: '#e9ecef', padding: '10px 15px', borderRadius: '8px', fontWeight: 'bold' }}>300 pts</div>
              <div>Premium wellness reward (e.g. premium hygiene kit).</div>
            </div>
          </div>
        </div>
      </div>

      <div className="card" style={{ background: '#fff3cd', borderLeft: '5px solid #ffc107', marginTop: '2rem' }}>
        <p style={{ margin: 0, color: '#856404', fontWeight: 'bold' }}>Important Note:</p>
        <p style={{ margin: 0, color: '#856404', fontSize: '0.95rem' }}>
          Rewards are subject to clinic policy and cannot be exchanged for cash. Points do not affect medical care, insurance billing, diagnosis, or treatment. The point system rewards attendance only, not medical results or health outcomes.
        </p>
      </div>
    </div>
  );
};

export default RewardsPage;
