import React from 'react';

const AboutPage = () => {
  return (
    <div className="container animate-slide-up">
      <div className="card" style={{ padding: '4rem 2rem', textAlign: 'center' }}>
        <h1>About Care Flow AI</h1>
        <p style={{ fontSize: '1.2rem', maxWidth: '800px', margin: '0 auto' }}>
          At Care Flow AI, our mission is to provide accessible, high-quality healthcare while ensuring our patients feel valued and respected. We focus on patient care, convenience, preventive health, and improving patient attendance through positive reinforcement.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem' }}>
        <div className="card">
          <h3>Our Provider Team</h3>
          <p>Our team consists of board-certified physicians, skilled nurses, and friendly administrative staff dedicated to your well-being. We treat every patient like family.</p>
        </div>
        <div className="card">
          <h3>Patient-Centered Care</h3>
          <p>We believe that healthcare should revolve around you. From easy scheduling to clear communication and our unique rewards program, we prioritize your convenience and health.</p>
        </div>
        <div className="card">
          <h3>Our Office Values</h3>
          <p>Trust, transparency, and consistency. We value your time as much as you do, which is why we created the Care Flow AI Points system to thank you for showing up to your scheduled visits.</p>
        </div>
      </div>
    </div>
  );
};

export default AboutPage;
