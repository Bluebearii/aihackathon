import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAppContext } from '../context/AppContext';
import { FileText, Download, CheckCircle } from 'lucide-react';

const ALL_CONDITIONS_LEFT = [
  { key: 'acquired_respiratory_distress', label: 'Acquired Respiratory Distress Syndrome' },
  { key: 'angina', label: 'Angina' },
  { key: 'anxiety_panic', label: 'Anxiety or Panic Disorders' },
  { key: 'arthritis', label: 'Arthritis (RA, OA)' },
  { key: 'asthma', label: 'Asthma' },
  { key: 'copd', label: 'Chronic Obstructive Pulmonary Disease (COPD)' },
  { key: 'chf', label: 'Congestive Heart Failure (CHF)' },
  { key: 'degenerative_disc', label: 'Degenerative Disc Disease' },
  { key: 'depression', label: 'Depression' },
  { key: 'diabetes', label: 'Diabetes' },
  { key: 'emphysema', label: 'Emphysema' },
  { key: 'hearing_impairment', label: 'Hearing Impairment' },
  { key: 'heart_attack', label: 'Heart Attack' },
  { key: 'multiple_sclerosis', label: 'Multiple Sclerosis' },
  { key: 'osteoporosis', label: 'Osteoporosis' },
  { key: 'parkinsons', label: "Parkinson's Disease" },
  { key: 'peripheral_vascular', label: 'Peripheral Vascular Disease' },
  { key: 'stroke_tia', label: 'Stroke or TIA' },
  { key: 'upper_gi_disease', label: 'Upper Gastrointestinal Disease' },
  { key: 'visual_impairment', label: 'Visual Impairment' },
];

const ALL_CONDITIONS_RIGHT = [
  { key: 'allergies', label: 'Allergies' },
  { key: 'headaches', label: 'Headaches' },
  { key: 'back_injury', label: 'Back Injury' },
  { key: 'bleeding_disorders', label: 'Bleeding Disorders' },
  { key: 'bowel_bladder', label: 'Bowel / Bladder Abnormalities' },
  { key: 'cancer', label: 'Cancer' },
  { key: 'dizzy_fainting', label: 'Dizzy or Fainting Spells' },
  { key: 'epilepsy_seizure', label: 'Epilepsy or Seizure Disorder' },
  { key: 'fracture', label: 'Fracture' },
  { key: 'hepatitis', label: 'Hepatitis A, B, C' },
  { key: 'hernia', label: 'Hernia' },
  { key: 'high_blood_pressure', label: 'High Blood Pressure' },
  { key: 'hypoglycemia', label: 'Hypoglycemia' },
  { key: 'immunosuppressant', label: 'Immunosuppressant Condition or Medication' },
  { key: 'kidney_problems', label: 'Kidney Problems' },
  { key: 'liver_gallbladder', label: 'Liver / Gallbladder Problems' },
  { key: 'metal_implants', label: 'Metal Implants' },
  { key: 'nausea_vomiting', label: 'Nausea / Vomiting' },
  { key: 'pacemaker', label: 'Pacemaker' },
  { key: 'pregnancy', label: 'Pregnancy' },
  { key: 'ringing_ears', label: 'Ringing in Your Ears' },
  { key: 'sexual_dysfunction', label: 'Sexual Dysfunction' },
  { key: 'skin_abnormalities', label: 'Skin Abnormalities' },
  { key: 'smoking', label: 'Smoking' },
  { key: 'special_diet', label: 'Special Diet Guidelines' },
  { key: 'tuberculosis', label: 'Tuberculosis' },
];

const MedicalHistoryPage = () => {
  const { user, API_URL } = useAppContext();
  const [submitted, setSubmitted] = useState(false);
  const [existingHistory, setExistingHistory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    patient_name: '',
    height_ft: '', height_in: '', weight: '',
    date_of_injury: '',
    latex_allergy_yes: false, latex_allergy_no: true,
    topical_allergy: '',
    diagnosis: '', injury_description: '',
    hospitalized: false, hospitalized_date: '',
    surgery: false, surgery_date: '', surgery_type: '',
    falls_past_year: false, falls_count: '',
    previous_treatment: false, treatment_date: '', treatment_summary: '',
    emg: false, ct_scan: false, myelogram: false, mri: false, xray: false,
    // All conditions default to false
    ...Object.fromEntries([...ALL_CONDITIONS_LEFT, ...ALL_CONDITIONS_RIGHT].map(c => [c.key, false])),
    emergency_contact_name: '', emergency_contact_phone: '',
    current_medications: '', family_history: '',
    reason_for_visit: '', additional_notes: ''
  });

  useEffect(() => {
    if (user) {
      // Auto-fill from user profile
      setFormData(prev => ({
        ...prev,
        patient_name: `${user.first_name} ${user.last_name}`
      }));
      // Load existing medical history
      loadExistingHistory();
    } else {
      setLoading(false);
    }
  }, [user]);

  const loadExistingHistory = async () => {
    try {
      const res = await axios.get(`${API_URL}/medical-history/${user.id}`);
      if (res.data) {
        setExistingHistory(res.data);
        // Merge existing data into form
        const existingData = res.data;
        setFormData(prev => {
          const merged = { ...prev };
          Object.keys(existingData).forEach(key => {
            if (key in merged && existingData[key] !== null && existingData[key] !== undefined) {
              merged[key] = existingData[key];
            }
          });
          return merged;
        });
      }
    } catch (err) {
      // No history exists yet - that's fine
    }
    setLoading(false);
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    if (type === 'checkbox') {
      setFormData(prev => ({ ...prev, [name]: checked }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        ...formData,
        patient_id: user.id,
        height_ft: formData.height_ft ? parseInt(formData.height_ft) : null,
        height_in: formData.height_in ? parseInt(formData.height_in) : null,
        weight: formData.weight ? parseFloat(formData.weight) : null,
        falls_count: formData.falls_count ? parseInt(formData.falls_count) : null,
      };
      await axios.post(`${API_URL}/medical-history/`, payload);
      setSubmitted(true);
    } catch (err) {
      alert('Error saving medical history. Please try again.');
      console.error(err);
    }
  };

  const exportToPDF = () => {
    import('jspdf').then(({ jsPDF }) => {
      const doc = new jsPDF();
      let y = 20;
      const lh = 6;
      const pw = doc.internal.pageSize.getWidth();

      doc.setFontSize(16);
      doc.setTextColor(0, 95, 115);
      doc.text('Medical History Form', pw / 2, y, { align: 'center' });
      y += 8;
      doc.setFontSize(9);
      doc.setTextColor(100);
      doc.text('Care Flow AI - CarePoint Clinic | Dallas, TX', pw / 2, y, { align: 'center' });
      y += 4;
      doc.setDrawColor(0, 95, 115);
      doc.line(20, y, pw - 20, y);
      y += 8;

      doc.setFontSize(10);
      doc.setTextColor(0);
      doc.text(`Patient Name: ${formData.patient_name}`, 20, y); y += lh;
      if (user) {
        doc.text(`Date of Birth: ${user.date_of_birth}   Phone: ${user.phone}`, 20, y); y += lh;
        doc.text(`Email: ${user.email}   Address: ${user.address}`, 20, y); y += lh;
        doc.text(`Insurance: ${user.insurance_provider || 'N/A'}`, 20, y); y += lh;
      }
      doc.text(`Height: ${formData.height_ft || '-'}ft ${formData.height_in || '-'}in   Weight: ${formData.weight || '-'} lbs`, 20, y); y += lh;
      doc.text(`Latex Allergy: ${formData.latex_allergy_yes ? 'Yes' : 'No'}   Topical: ${formData.topical_allergy || 'None'}`, 20, y); y += lh;
      y += 3;

      if (formData.diagnosis) { doc.text(`Diagnosis: ${formData.diagnosis}`, 20, y); y += lh; }
      doc.text(`Hospitalized: ${formData.hospitalized ? 'Yes' : 'No'}${formData.hospitalized_date ? ' (' + formData.hospitalized_date + ')' : ''}`, 20, y); y += lh;
      doc.text(`Surgery: ${formData.surgery ? 'Yes' : 'No'}${formData.surgery_type ? ' - ' + formData.surgery_type : ''}`, 20, y); y += lh;
      doc.text(`Falls Past Year: ${formData.falls_past_year ? 'Yes (' + (formData.falls_count || 'N/A') + ')' : 'No'}`, 20, y); y += lh;
      doc.text(`Previous Treatment: ${formData.previous_treatment ? 'Yes' : 'No'}`, 20, y); y += lh;
      if (formData.treatment_summary) { doc.text(`  Summary: ${formData.treatment_summary}`, 25, y); y += lh; }

      const imaging = [];
      if (formData.emg) imaging.push('EMG');
      if (formData.ct_scan) imaging.push('CT Scan');
      if (formData.myelogram) imaging.push('Myelogram');
      if (formData.mri) imaging.push('MRI');
      if (formData.xray) imaging.push('X-Ray');
      doc.text(`Imaging: ${imaging.length > 0 ? imaging.join(', ') : 'None'}`, 20, y); y += lh;
      y += 4;

      doc.setFont(undefined, 'bold');
      doc.text('Medical Conditions', 20, y); y += lh;
      doc.setFont(undefined, 'normal');

      const allConds = [...ALL_CONDITIONS_LEFT, ...ALL_CONDITIONS_RIGHT];
      const mid = Math.ceil(allConds.length / 2);
      for (let i = 0; i < mid; i++) {
        if (y > 270) { doc.addPage(); y = 20; }
        const left = allConds[i];
        const right = allConds[i + mid];
        doc.text(`${formData[left.key] ? '[X]' : '[ ]'} ${left.label}`, 20, y);
        if (right) doc.text(`${formData[right.key] ? '[X]' : '[ ]'} ${right.label}`, 110, y);
        y += lh;
      }

      if (y > 250) { doc.addPage(); y = 20; }
      y += 4;
      if (formData.emergency_contact_name) { doc.text(`Emergency Contact: ${formData.emergency_contact_name} (${formData.emergency_contact_phone || 'N/A'})`, 20, y); y += lh; }
      if (formData.current_medications) { doc.text(`Medications: ${formData.current_medications}`, 20, y); y += lh; }

      y += 12;
      doc.setFontSize(8);
      doc.setTextColor(150);
      doc.text(`Generated: ${new Date().toLocaleString()}`, 20, y); y += 10;
      doc.setTextColor(0);
      doc.setFontSize(10);
      doc.line(20, y, 90, y);
      doc.text('Patient Signature', 20, y + 5);
      doc.line(110, y, 180, y);
      doc.text('Date', 110, y + 5);

      doc.save(`medical_history_${formData.patient_name.replace(/\s/g, '_')}.pdf`);
    });
  };

  if (loading) return <div className="container"><div className="card" style={{ textAlign: 'center' }}>Loading...</div></div>;

  if (submitted) {
    return (
      <div className="container animate-pop">
        <div className="card" style={{ textAlign: 'center', padding: '4rem 2rem', maxWidth: '600px', margin: '0 auto' }}>
          <div style={{ background: '#d4edda', width: '80px', height: '80px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1.5rem auto' }}>
            <CheckCircle size={40} color="#155724" />
          </div>
          <h2>Medical History Saved!</h2>
          <p style={{ fontSize: '1.1rem', color: '#005f73' }}>Your medical history has been saved to your profile successfully.</p>
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', marginTop: '1.5rem' }}>
            <button className="btn btn-primary" onClick={exportToPDF} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Download size={18} /> Export to PDF
            </button>
            <button className="btn btn-outline" onClick={() => setSubmitted(false)}>Edit Form</button>
          </div>
        </div>
      </div>
    );
  }

  const sectionStyle = {
    borderBottom: '2px solid #f1f5f9',
    paddingBottom: '10px',
    marginBottom: '20px',
    marginTop: '30px',
    color: '#334155'
  };

  return (
    <div className="container animate-slide-up" style={{ maxWidth: '900px' }}>
      <div className="card" style={{ margin: '2rem auto', padding: '2.5rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '12px', marginBottom: '0.5rem' }}>
            <FileText size={28} color="#005f73" />
            <h2 style={{ margin: 0, fontSize: '1.8rem', color: '#0f172a' }}>Medical History Form</h2>
          </div>
          <p style={{ color: '#64748b' }}>Please fill out all sections. Your known information has been auto-filled.</p>
          {existingHistory && (
            <div style={{ background: '#f0fdf4', padding: '8px 16px', borderRadius: '8px', display: 'inline-block', fontSize: '0.85rem', color: '#16a34a', fontWeight: '600', marginTop: '8px' }}>
              Previously completed on {new Date(existingHistory.completed_at).toLocaleDateString()} - Editing will update your record
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit}>
          {/* Section 1: Patient Info */}
          <h3 style={sectionStyle}>1. Patient Information</h3>
          <div className="form-group">
            <label className="form-label">Patient Name</label>
            <input type="text" name="patient_name" className="form-control" value={formData.patient_name} onChange={handleChange} style={{ background: '#f0fdf4' }} />
          </div>
          <div style={{ display: 'flex', gap: '15px' }}>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label">Height (ft)</label>
              <input type="number" name="height_ft" className="form-control" value={formData.height_ft} onChange={handleChange} />
            </div>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label">Height (in)</label>
              <input type="number" name="height_in" className="form-control" value={formData.height_in} onChange={handleChange} />
            </div>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label">Weight (lbs)</label>
              <input type="number" name="weight" className="form-control" value={formData.weight} onChange={handleChange} />
            </div>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label">Date of Injury</label>
              <input type="date" name="date_of_injury" className="form-control" value={formData.date_of_injury} onChange={handleChange} />
            </div>
          </div>

          <div style={{ display: 'flex', gap: '20px', marginBottom: '1rem' }}>
            <div>
              <label className="form-label">Latex Allergy</label>
              <div style={{ display: 'flex', gap: '16px' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
                  <input type="radio" name="latex_allergy" checked={formData.latex_allergy_yes} onChange={() => setFormData(prev => ({ ...prev, latex_allergy_yes: true, latex_allergy_no: false }))} />
                  Yes
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
                  <input type="radio" name="latex_allergy" checked={formData.latex_allergy_no} onChange={() => setFormData(prev => ({ ...prev, latex_allergy_yes: false, latex_allergy_no: true }))} />
                  No
                </label>
              </div>
            </div>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label">Topical Allergy</label>
              <input type="text" name="topical_allergy" className="form-control" value={formData.topical_allergy} onChange={handleChange} placeholder="Specify if any" />
            </div>
          </div>

          {/* Section 2: Medical History */}
          <h3 style={sectionStyle}>2. Medical History</h3>
          <p style={{ color: '#64748b', fontSize: '0.9rem', marginBottom: '16px' }}>Please type "N/A" in the text fields if they do not apply to you.</p>
          <div className="form-group">
            <label className="form-label">Diagnosis (as stated by your physician)</label>
            <textarea name="diagnosis" className="form-control" rows="2" value={formData.diagnosis} onChange={handleChange} placeholder="Type 'N/A' if none"></textarea>
          </div>
          <div className="form-group">
            <label className="form-label">How did this injury/exacerbation occur?</label>
            <textarea name="injury_description" className="form-control" rows="2" value={formData.injury_description} onChange={handleChange} placeholder="Type 'N/A' if none"></textarea>
          </div>

          <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', marginBottom: '1rem' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
              <input type="checkbox" name="hospitalized" checked={formData.hospitalized} onChange={handleChange} style={{ width: '18px', height: '18px', accentColor: '#005f73' }} />
              <span>Hospitalized for present condition?</span>
            </label>
            {formData.hospitalized && (
              <input type="text" name="hospitalized_date" className="form-control" value={formData.hospitalized_date} onChange={handleChange} placeholder="Date" style={{ width: '150px' }} />
            )}
          </div>

          <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', marginBottom: '1rem' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
              <input type="checkbox" name="surgery" checked={formData.surgery} onChange={handleChange} style={{ width: '18px', height: '18px', accentColor: '#005f73' }} />
              <span>Had surgery for present condition?</span>
            </label>
            {formData.surgery && (
              <>
                <input type="text" name="surgery_date" className="form-control" value={formData.surgery_date} onChange={handleChange} placeholder="Date" style={{ width: '150px' }} />
                <input type="text" name="surgery_type" className="form-control" value={formData.surgery_type} onChange={handleChange} placeholder="Surgery type" style={{ width: '200px' }} />
              </>
            )}
          </div>

          <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', marginBottom: '1rem' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
              <input type="checkbox" name="falls_past_year" checked={formData.falls_past_year} onChange={handleChange} style={{ width: '18px', height: '18px', accentColor: '#005f73' }} />
              <span>Any falls this past year?</span>
            </label>
            {formData.falls_past_year && (
              <input type="number" name="falls_count" className="form-control" value={formData.falls_count} onChange={handleChange} placeholder="How many?" style={{ width: '120px' }} />
            )}
          </div>

          <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', marginBottom: '1rem' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
              <input type="checkbox" name="previous_treatment" checked={formData.previous_treatment} onChange={handleChange} style={{ width: '18px', height: '18px', accentColor: '#005f73' }} />
              <span>Received previous treatment for this condition?</span>
            </label>
            {formData.previous_treatment && (
              <input type="text" name="treatment_date" className="form-control" value={formData.treatment_date} onChange={handleChange} placeholder="Date" style={{ width: '150px' }} />
            )}
          </div>
          {formData.previous_treatment && (
            <div className="form-group">
              <label className="form-label">Please summarize treatment</label>
              <textarea name="treatment_summary" className="form-control" rows="2" value={formData.treatment_summary} onChange={handleChange} placeholder="Type 'N/A' if none"></textarea>
            </div>
          )}

          {/* Section 3: Imaging */}
          <h3 style={sectionStyle}>3. Imaging Tests</h3>
          <p style={{ color: '#64748b', fontSize: '0.9rem', marginBottom: '12px' }}>Have you ever had any of the following?</p>
          <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap', marginBottom: '1.5rem' }}>
            {[
              { key: 'emg', label: 'EMG' },
              { key: 'ct_scan', label: 'CT Scan' },
              { key: 'myelogram', label: 'Myelogram' },
              { key: 'mri', label: 'MRI' },
              { key: 'xray', label: 'X-Ray' },
            ].map(test => (
              <label key={test.key} style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '0.95rem' }}>
                <input type="checkbox" name={test.key} checked={formData[test.key]} onChange={handleChange} style={{ width: '18px', height: '18px', accentColor: '#005f73' }} />
                {test.label}
              </label>
            ))}
          </div>

          {/* Section 4: Medical Conditions */}
          <h3 style={sectionStyle}>4. Medical Conditions</h3>
          <p style={{ color: '#64748b', fontSize: '0.9rem', marginBottom: '16px' }}>
            Have you ever been treated for any of the following conditions? Check Yes or No for each.
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0', background: '#f8fafc', borderRadius: '12px', border: '1px solid #e2e8f0', overflow: 'hidden' }}>
            {/* Left Column */}
            <div style={{ borderRight: '1px solid #e2e8f0' }}>
              {ALL_CONDITIONS_LEFT.map((cond, idx) => (
                <div key={cond.key} style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  padding: '10px 16px', borderBottom: idx < ALL_CONDITIONS_LEFT.length - 1 ? '1px solid #e2e8f0' : 'none',
                  background: formData[cond.key] ? '#f0fdf4' : 'white'
                }}>
                  <span style={{ fontSize: '0.88rem', color: '#334155', fontWeight: formData[cond.key] ? '600' : '400' }}>{cond.label}</span>
                  <div style={{ display: 'flex', gap: '12px' }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.8rem', cursor: 'pointer' }}>
                      <input type="checkbox" name={cond.key} checked={formData[cond.key]} onChange={handleChange} style={{ accentColor: '#005f73' }} /> Yes
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.8rem', cursor: 'pointer', color: '#94a3b8' }}>
                      <input type="radio" checked={!formData[cond.key]} onChange={() => setFormData(prev => ({ ...prev, [cond.key]: false }))} /> No
                    </label>
                  </div>
                </div>
              ))}
            </div>
            {/* Right Column */}
            <div>
              {ALL_CONDITIONS_RIGHT.map((cond, idx) => (
                <div key={cond.key} style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  padding: '10px 16px', borderBottom: idx < ALL_CONDITIONS_RIGHT.length - 1 ? '1px solid #e2e8f0' : 'none',
                  background: formData[cond.key] ? '#f0fdf4' : 'white'
                }}>
                  <span style={{ fontSize: '0.88rem', color: '#334155', fontWeight: formData[cond.key] ? '600' : '400' }}>{cond.label}</span>
                  <div style={{ display: 'flex', gap: '12px' }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.8rem', cursor: 'pointer' }}>
                      <input type="checkbox" name={cond.key} checked={formData[cond.key]} onChange={handleChange} style={{ accentColor: '#005f73' }} /> Yes
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.8rem', cursor: 'pointer', color: '#94a3b8' }}>
                      <input type="radio" checked={!formData[cond.key]} onChange={() => setFormData(prev => ({ ...prev, [cond.key]: false }))} /> No
                    </label>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Section 5: Additional Info */}
          <h3 style={sectionStyle}>5. Additional Information</h3>
          <div style={{ display: 'flex', gap: '15px' }}>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label">Emergency Contact Name</label>
              <input type="text" name="emergency_contact_name" className="form-control" value={formData.emergency_contact_name} onChange={handleChange} />
            </div>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label">Emergency Contact Phone</label>
              <input type="tel" name="emergency_contact_phone" className="form-control" value={formData.emergency_contact_phone} onChange={handleChange} />
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">Current Medications</label>
            <textarea name="current_medications" className="form-control" rows="2" value={formData.current_medications} onChange={handleChange} placeholder="List all current medications and dosages. Type 'N/A' if none"></textarea>
          </div>
          <div className="form-group">
            <label className="form-label">Family Medical History</label>
            <textarea name="family_history" className="form-control" rows="2" value={formData.family_history} onChange={handleChange} placeholder="Any relevant family medical history. Type 'N/A' if none"></textarea>
          </div>
          <div className="form-group">
            <label className="form-label">Reason for Visit</label>
            <textarea name="reason_for_visit" className="form-control" rows="2" value={formData.reason_for_visit} onChange={handleChange} placeholder="Type 'N/A' if none"></textarea>
          </div>
          <div className="form-group">
            <label className="form-label">Additional Notes</label>
            <textarea name="additional_notes" className="form-control" rows="2" value={formData.additional_notes} onChange={handleChange} placeholder="Type 'N/A' if none"></textarea>
          </div>

          <div style={{ display: 'flex', gap: '12px', marginTop: '2rem' }}>
            <button type="submit" className="btn btn-primary" style={{ flex: 1, padding: '16px', fontSize: '1.1rem' }}>
              Save Medical History
            </button>
            <button type="button" className="btn btn-outline" onClick={exportToPDF} style={{ padding: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Download size={18} /> Export to PDF
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default MedicalHistoryPage;
