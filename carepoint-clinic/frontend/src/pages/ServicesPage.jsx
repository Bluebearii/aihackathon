import React from 'react';
import { Link } from 'react-router-dom';

const ServicesPage = () => {
  const services = [
    { title: "Annual Checkup", desc: "Comprehensive physical exam to assess your overall health and well-being." },
    { title: "Eye Exam / General Exam", desc: "Routine vision testing and general wellness screenings." },
    { title: "Follow-up Appointment", desc: "Check-in on previous conditions, medication adjustments, or recent treatments." },
    { title: "Lab Result Discussion", desc: "Detailed review of your recent blood work or diagnostic tests with a provider." },
    { title: "Preventive Care Visit", desc: "Focused visit on screenings, immunizations, and healthy lifestyle counseling." },
    { title: "Insurance Verification", desc: "Consultation with our billing team to understand your coverage and out-of-pocket costs." }
  ];

  return (
    <div className="container animate-slide-up">
      <h1 style={{ textAlign: 'center', marginBottom: '3rem' }}>Our Medical Services</h1>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '2rem' }}>
        {services.map((svc, idx) => (
          <div key={idx} className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div>
              <h3>{svc.title}</h3>
              <p>{svc.desc}</p>
            </div>
            <div style={{ marginTop: '1.5rem' }}>
              <Link to="/book" className="btn btn-outline" style={{ width: '100%' }}>Schedule Now</Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ServicesPage;
