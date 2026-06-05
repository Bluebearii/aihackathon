import React from 'react';
import { Link } from 'react-router-dom';
import { CalendarCheck, ShieldCheck, Award, ArrowRight } from 'lucide-react';

const HomePage = () => {
  return (
    <div className="container animate-slide-up">
      <div style={{ textAlign: 'center', padding: '4rem 0', background: 'var(--color-surface)', borderRadius: 'var(--border-radius-lg)', boxShadow: 'var(--shadow-md)', marginBottom: '3rem' }}>
        <h1 style={{ fontSize: '3rem', marginBottom: '1rem' }}>Healthcare That Rewards Consistency</h1>
        <p style={{ fontSize: '1.2rem', maxWidth: '800px', margin: '0 auto 2rem auto', color: 'var(--color-text-main)' }}>
          Book your appointment, show up for your visit, and earn <strong>WeCarePeople Points</strong> every time our staff confirms your attendance.
        </p>
        <div style={{ display: 'flex', justifyContent: 'center', gap: '15px' }}>
          <Link to="/book" className="btn btn-primary" style={{ fontSize: '1.1rem', padding: '15px 30px' }}>Book Appointment</Link>
          <Link to="/dashboard" className="btn btn-outline" style={{ fontSize: '1.1rem', padding: '15px 30px' }}>Patient Login</Link>
          <Link to="/rewards" className="btn btn-secondary" style={{ fontSize: '1.1rem', padding: '15px 30px' }}>View Rewards</Link>
        </div>
      </div>

      <h2 style={{ textAlign: 'center', marginBottom: '2rem' }}>How Our Point System Works</h2>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '2rem', marginBottom: '4rem' }}>
        <div className="card" style={{ textAlign: 'center' }}>
          <div style={{ background: '#e0fbfc', width: '60px', height: '60px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem auto' }}>
            <CalendarCheck size={30} color="var(--color-primary)" />
          </div>
          <h3>Step 1</h3>
          <p>Book an appointment online or call our clinic.</p>
        </div>
        <div className="card" style={{ textAlign: 'center' }}>
          <div style={{ background: '#e0fbfc', width: '60px', height: '60px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem auto' }}>
            <ArrowRight size={30} color="var(--color-primary)" />
          </div>
          <h3>Step 2</h3>
          <p>Check in at the office on the day of your visit.</p>
        </div>
        <div className="card" style={{ textAlign: 'center' }}>
          <div style={{ background: '#e0fbfc', width: '60px', height: '60px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem auto' }}>
            <ShieldCheck size={30} color="var(--color-primary)" />
          </div>
          <h3>Step 3</h3>
          <p>Our staff securely confirms your attendance.</p>
        </div>
        <div className="card" style={{ textAlign: 'center' }}>
          <div style={{ background: '#d4edda', width: '60px', height: '60px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem auto' }}>
            <Award size={30} color="var(--color-success)" />
          </div>
          <h3>Step 4</h3>
          <p>Points are automatically added to your account!</p>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
