import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAppContext } from '../context/AppContext';
import { Search, User, Calendar, Award, FileText, Edit, Trash2, X, Eye, Download, Plus } from 'lucide-react';

const PatientDatabase = () => {
  const { user, API_URL } = useAppContext();
  const [patients, setPatients] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [patientProfile, setPatientProfile] = useState(null);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user?.role === 'admin') fetchPatients();
  }, [user]);

  const fetchPatients = async (search = '') => {
    try {
      const res = await axios.get(`${API_URL}/patients/${search ? `?search=${search}` : ''}`);
      setPatients(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSearch = (e) => {
    const val = e.target.value;
    setSearchTerm(val);
    fetchPatients(val);
  };

  const viewPatientProfile = async (patientId) => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_URL}/patients/${patientId}/profile`);
      setPatientProfile(res.data);
      setShowProfileModal(true);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const deletePatient = async (patientId) => {
    if (!window.confirm('Are you sure you want to delete this patient? This action cannot be undone.')) return;
    try {
      await axios.delete(`${API_URL}/users/${patientId}`);
      fetchPatients(searchTerm);
      alert('Patient deleted successfully.');
    } catch (err) {
      alert('Error deleting patient.');
    }
  };

  const exportMedicalHistoryPDF = (mh, patientInfo) => {
    import('jspdf').then(({ jsPDF }) => {
      const doc = new jsPDF();
      let y = 20;
      const lineHeight = 7;
      const pageWidth = doc.internal.pageSize.getWidth();

      // Header
      doc.setFontSize(18);
      doc.setTextColor(0, 95, 115);
      doc.text('Care Flow AI - Medical History Form', pageWidth / 2, y, { align: 'center' });
      y += 10;
      doc.setFontSize(9);
      doc.setTextColor(100, 100, 100);
      doc.text('CarePoint Clinic | Dallas, TX', pageWidth / 2, y, { align: 'center' });
      y += 4;
      doc.setDrawColor(0, 95, 115);
      doc.setLineWidth(0.5);
      doc.line(20, y, pageWidth - 20, y);
      y += 10;

      // Patient Info Section
      doc.setFontSize(12);
      doc.setTextColor(0, 0, 0);
      doc.setFont(undefined, 'bold');
      doc.text('Patient Information', 20, y);
      y += lineHeight;
      doc.setFont(undefined, 'normal');
      doc.setFontSize(10);

      const patientName = mh?.patient_name || `${patientInfo.first_name} ${patientInfo.last_name}`;
      doc.text(`Patient Name: ${patientName}`, 20, y); y += lineHeight;
      doc.text(`Date of Birth: ${patientInfo.date_of_birth}`, 20, y);
      doc.text(`Phone: ${patientInfo.phone}`, 110, y); y += lineHeight;
      doc.text(`Email: ${patientInfo.email}`, 20, y); y += lineHeight;
      doc.text(`Address: ${patientInfo.address}`, 20, y); y += lineHeight;
      doc.text(`Insurance: ${patientInfo.insurance_provider || 'N/A'}`, 20, y); y += lineHeight;

      if (mh) {
        doc.text(`Height: ${mh.height_ft || ''}ft ${mh.height_in || ''}in    Weight: ${mh.weight || 'N/A'} lbs`, 20, y); y += lineHeight;
        doc.text(`Latex Allergy: ${mh.latex_allergy_yes ? 'Yes' : 'No'}    Topical Allergy: ${mh.topical_allergy || 'None'}`, 20, y); y += lineHeight;
        y += 5;

        // Diagnosis
        if (mh.diagnosis) {
          doc.setFont(undefined, 'bold');
          doc.text('Diagnosis:', 20, y); y += lineHeight;
          doc.setFont(undefined, 'normal');
          doc.text(mh.diagnosis, 25, y); y += lineHeight;
        }

        // History
        doc.text(`Hospitalized: ${mh.hospitalized ? 'Yes' : 'No'}${mh.hospitalized_date ? ` (${mh.hospitalized_date})` : ''}`, 20, y); y += lineHeight;
        doc.text(`Surgery: ${mh.surgery ? 'Yes' : 'No'}${mh.surgery_type ? ` - ${mh.surgery_type}` : ''}`, 20, y); y += lineHeight;
        doc.text(`Falls Past Year: ${mh.falls_past_year ? `Yes (${mh.falls_count || 'N/A'})` : 'No'}`, 20, y); y += lineHeight;
        doc.text(`Previous Treatment: ${mh.previous_treatment ? 'Yes' : 'No'}`, 20, y); y += lineHeight;
        if (mh.treatment_summary) { doc.text(`  Summary: ${mh.treatment_summary}`, 25, y); y += lineHeight; }

        // Imaging
        y += 3;
        doc.setFont(undefined, 'bold');
        doc.text('Imaging Tests:', 20, y); y += lineHeight;
        doc.setFont(undefined, 'normal');
        const imaging = [];
        if (mh.emg) imaging.push('EMG');
        if (mh.ct_scan) imaging.push('CT Scan');
        if (mh.myelogram) imaging.push('Myelogram');
        if (mh.mri) imaging.push('MRI');
        if (mh.xray) imaging.push('X-Ray');
        doc.text(imaging.length > 0 ? imaging.join(', ') : 'None', 25, y); y += lineHeight;

        // Conditions
        y += 5;
        doc.setFont(undefined, 'bold');
        doc.setFontSize(12);
        doc.text('Medical Conditions', 20, y); y += lineHeight;
        doc.setFont(undefined, 'normal');
        doc.setFontSize(10);

        const conditions = [
          ['Acquired Respiratory Distress', mh.acquired_respiratory_distress],
          ['Angina', mh.angina], ['Anxiety/Panic', mh.anxiety_panic],
          ['Arthritis', mh.arthritis], ['Asthma', mh.asthma],
          ['COPD', mh.copd], ['CHF', mh.chf],
          ['Degenerative Disc Disease', mh.degenerative_disc],
          ['Depression', mh.depression], ['Diabetes', mh.diabetes],
          ['Emphysema', mh.emphysema], ['Hearing Impairment', mh.hearing_impairment],
          ['Heart Attack', mh.heart_attack], ['Multiple Sclerosis', mh.multiple_sclerosis],
          ['Osteoporosis', mh.osteoporosis], ['Parkinson\'s Disease', mh.parkinsons],
          ['Peripheral Vascular Disease', mh.peripheral_vascular],
          ['Stroke/TIA', mh.stroke_tia], ['Upper GI Disease', mh.upper_gi_disease],
          ['Visual Impairment', mh.visual_impairment],
          ['Allergies', mh.allergies], ['Headaches', mh.headaches],
          ['Back Injury', mh.back_injury], ['Bleeding Disorders', mh.bleeding_disorders],
          ['Bowel/Bladder Abnormalities', mh.bowel_bladder], ['Cancer', mh.cancer],
          ['Dizzy/Fainting', mh.dizzy_fainting], ['Epilepsy/Seizure', mh.epilepsy_seizure],
          ['Fracture', mh.fracture], ['Hepatitis', mh.hepatitis],
          ['Hernia', mh.hernia], ['High Blood Pressure', mh.high_blood_pressure],
          ['Hypoglycemia', mh.hypoglycemia], ['Immunosuppressant', mh.immunosuppressant],
          ['Kidney Problems', mh.kidney_problems], ['Liver/Gallbladder', mh.liver_gallbladder],
          ['Metal Implants', mh.metal_implants], ['Nausea/Vomiting', mh.nausea_vomiting],
          ['Pacemaker', mh.pacemaker], ['Pregnancy', mh.pregnancy],
          ['Ringing in Ears', mh.ringing_ears], ['Sexual Dysfunction', mh.sexual_dysfunction],
          ['Skin Abnormalities', mh.skin_abnormalities], ['Smoking', mh.smoking],
          ['Special Diet', mh.special_diet], ['Tuberculosis', mh.tuberculosis]
        ];

        // Render in two columns
        const midPoint = Math.ceil(conditions.length / 2);
        for (let i = 0; i < midPoint; i++) {
          if (y > 270) { doc.addPage(); y = 20; }
          const left = conditions[i];
          const right = conditions[i + midPoint];
          const leftMark = left[1] ? '[X]' : '[ ]';
          doc.text(`${leftMark} ${left[0]}`, 20, y);
          if (right) {
            const rightMark = right[1] ? '[X]' : '[ ]';
            doc.text(`${rightMark} ${right[0]}`, 110, y);
          }
          y += lineHeight;
        }

        // Additional info
        if (y > 250) { doc.addPage(); y = 20; }
        y += 5;
        if (mh.emergency_contact_name) {
          doc.text(`Emergency Contact: ${mh.emergency_contact_name} (${mh.emergency_contact_phone || 'N/A'})`, 20, y); y += lineHeight;
        }
        if (mh.current_medications) {
          doc.text(`Current Medications: ${mh.current_medications}`, 20, y); y += lineHeight;
        }

        // Completion timestamp
        y += 10;
        doc.setFontSize(8);
        doc.setTextColor(150, 150, 150);
        doc.text(`Form completed: ${mh.completed_at ? new Date(mh.completed_at).toLocaleString() : 'Pending'}`, 20, y);
        y += lineHeight;
        doc.text(`Generated: ${new Date().toLocaleString()}`, 20, y);

        // Signature line
        y += 15;
        doc.setTextColor(0, 0, 0);
        doc.setFontSize(10);
        doc.line(20, y, 90, y);
        doc.text('Patient Signature', 20, y + 5);
        doc.line(110, y, 180, y);
        doc.text('Date', 110, y + 5);
      }

      doc.save(`medical_history_${patientName.replace(/\s/g, '_')}.pdf`);
    });
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

  return (
    <div className="container animate-slide-up">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h1>Patient Database</h1>
          <p>View, search, and manage all patient records. {patients.length} patients registered.</p>
        </div>
      </div>

      <div className="card">
        <div style={{ display: 'flex', gap: '12px', marginBottom: '1.5rem', alignItems: 'center' }}>
          <div style={{ position: 'relative', flex: 1 }}>
            <Search size={18} style={{ position: 'absolute', top: '12px', left: '12px', color: '#94a3b8' }} />
            <input
              type="text"
              className="form-control"
              placeholder="Search by name, phone, email..."
              style={{ paddingLeft: '40px' }}
              value={searchTerm}
              onChange={handleSearch}
            />
          </div>
        </div>

        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Patient Name</th>
                <th>DOB</th>
                <th>Phone</th>
                <th>Insurance</th>
                <th>Last Visit</th>
                <th>No-Shows</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {patients.map(p => (
                <tr key={p.id}>
                  <td style={{ fontWeight: 'bold', color: '#005f73' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <div style={{ background: '#f0f9ff', width: '36px', height: '36px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <User size={16} color="#005f73" />
                      </div>
                      {p.first_name} {p.last_name}
                    </div>
                  </td>
                  <td>{p.date_of_birth}</td>
                  <td>{p.phone}</td>
                  <td>{p.insurance_provider || 'N/A'}</td>
                  <td>{p.last_visit_date || 'Never'}</td>
                  <td>
                    {p.no_show_count > 0 ? (
                      <span className="badge badge-danger">{p.no_show_count}</span>
                    ) : (
                      <span className="badge badge-success">0</span>
                    )}
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: '6px' }}>
                      <button
                        onClick={() => viewPatientProfile(p.id)}
                        title="View Profile"
                        style={{ background: '#f0f9ff', border: '1px solid #bae6fd', borderRadius: '6px', padding: '6px', cursor: 'pointer' }}
                      >
                        <Eye size={16} color="#0284c7" />
                      </button>
                      <button
                        onClick={() => deletePatient(p.id)}
                        title="Delete Patient"
                        style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '6px', padding: '6px', cursor: 'pointer' }}
                      >
                        <Trash2 size={16} color="#dc2626" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {patients.length === 0 && (
                <tr><td colSpan="7" style={{ textAlign: 'center', color: '#94a3b8' }}>No patients found.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Patient Profile Modal */}
      {showProfileModal && patientProfile && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center',
          zIndex: 1000
        }} onClick={() => setShowProfileModal(false)}>
          <div style={{
            background: 'white', borderRadius: '16px', padding: '32px', maxWidth: '700px', width: '95%',
            maxHeight: '85vh', overflow: 'auto',
            boxShadow: '0 20px 60px rgba(0,0,0,0.3)', animation: 'slideUp 0.3s ease'
          }} onClick={e => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
              <h2 style={{ margin: 0 }}>Patient Profile</h2>
              <button onClick={() => setShowProfileModal(false)} style={{ background: '#f1f5f9', border: 'none', borderRadius: '8px', padding: '8px', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>

            {/* Personal Info */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '24px' }}>
              <div style={{ background: 'linear-gradient(135deg, #005f73, #0a9396)', width: '60px', height: '60px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <User size={28} color="white" />
              </div>
              <div>
                <h3 style={{ margin: 0 }}>{patientProfile.patient.first_name} {patientProfile.patient.last_name}</h3>
                <div style={{ color: '#64748b' }}>{patientProfile.patient.email} · {patientProfile.patient.phone}</div>
                <div style={{ color: '#94a3b8', fontSize: '0.85rem' }}>DOB: {patientProfile.patient.date_of_birth} · {patientProfile.patient.gender || 'N/A'}</div>
              </div>
            </div>

            {/* Stats Row */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', marginBottom: '24px' }}>
              <div style={{ background: '#f0fdf4', padding: '16px', borderRadius: '12px', textAlign: 'center' }}>
                <Award size={20} color="#16a34a" />
                <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#16a34a' }}>{patientProfile.total_points}</div>
                <div style={{ fontSize: '0.8rem', color: '#64748b' }}>Total Points</div>
              </div>
              <div style={{ background: '#f0f9ff', padding: '16px', borderRadius: '12px', textAlign: 'center' }}>
                <Calendar size={20} color="#0284c7" />
                <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#0284c7' }}>{patientProfile.appointments.length}</div>
                <div style={{ fontSize: '0.8rem', color: '#64748b' }}>Appointments</div>
              </div>
              <div style={{ background: patientProfile.patient.no_show_count > 0 ? '#fef2f2' : '#f0fdf4', padding: '16px', borderRadius: '12px', textAlign: 'center' }}>
                <FileText size={20} color={patientProfile.patient.no_show_count > 0 ? '#dc2626' : '#16a34a'} />
                <div style={{ fontSize: '1.5rem', fontWeight: '700', color: patientProfile.patient.no_show_count > 0 ? '#dc2626' : '#16a34a' }}>{patientProfile.patient.no_show_count}</div>
                <div style={{ fontSize: '0.8rem', color: '#64748b' }}>No-Shows</div>
              </div>
            </div>

            {/* Medical History */}
            <div style={{ marginBottom: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <h4 style={{ margin: 0 }}>Medical History</h4>
                {patientProfile.medical_history && (
                  <button
                    onClick={() => exportMedicalHistoryPDF(patientProfile.medical_history, patientProfile.patient)}
                    className="btn btn-outline"
                    style={{ padding: '6px 12px', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '6px' }}
                  >
                    <Download size={14} /> Export to PDF
                  </button>
                )}
              </div>
              {patientProfile.medical_history ? (
                <div style={{ background: '#f8fafc', padding: '16px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                  <div style={{ fontSize: '0.85rem', color: '#16a34a', fontWeight: '600', marginBottom: '8px' }}>
                    ✓ Form completed on {new Date(patientProfile.medical_history.completed_at).toLocaleDateString()}
                  </div>
                  {patientProfile.medical_history.diagnosis && (
                    <div style={{ fontSize: '0.9rem', marginBottom: '4px' }}>
                      <strong>Diagnosis:</strong> {patientProfile.medical_history.diagnosis}
                    </div>
                  )}
                  {patientProfile.medical_history.current_medications && (
                    <div style={{ fontSize: '0.9rem' }}>
                      <strong>Medications:</strong> {patientProfile.medical_history.current_medications}
                    </div>
                  )}
                </div>
              ) : (
                <div style={{ background: '#fff7ed', padding: '16px', borderRadius: '8px', border: '1px solid #fed7aa', color: '#9a3412' }}>
                  Incomplete — Medical history form has not been submitted yet.
                </div>
              )}
            </div>

            {/* Appointment History */}
            <div style={{ marginBottom: '24px' }}>
              <h4>Appointment History</h4>
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Type</th>
                      <th>Provider</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {patientProfile.appointments.map((appt, idx) => (
                      <tr key={idx}>
                        <td>{appt.appointment_date} {appt.appointment_time}</td>
                        <td>{appt.appointment_type}</td>
                        <td>{appt.provider || 'N/A'}</td>
                        <td>
                          <span className={`badge ${appt.status === 'Completed' ? 'badge-success' : appt.status === 'No Show' ? 'badge-danger' : appt.status === 'Cancelled' ? 'badge-info' : 'badge-warning'}`}>
                            {appt.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                    {patientProfile.appointments.length === 0 && (
                      <tr><td colSpan="4" style={{ textAlign: 'center', color: '#94a3b8' }}>No appointments yet.</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Points History */}
            <div>
              <h4>Points History</h4>
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Reason</th>
                      <th>Points</th>
                    </tr>
                  </thead>
                  <tbody>
                    {patientProfile.points.map((pt, idx) => (
                      <tr key={idx}>
                        <td>{new Date(pt.created_at).toLocaleDateString()}</td>
                        <td>{pt.reason}</td>
                        <td style={{ color: '#16a34a', fontWeight: 'bold' }}>+{pt.points_added}</td>
                      </tr>
                    ))}
                    {patientProfile.points.length === 0 && (
                      <tr><td colSpan="3" style={{ textAlign: 'center', color: '#94a3b8' }}>No points earned yet.</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PatientDatabase;
