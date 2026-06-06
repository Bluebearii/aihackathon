import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { MessageSquare, X, Send, Bot, User, Loader2, FileText } from 'lucide-react';
import { useAppContext } from '../context/AppContext';
import { useNavigate } from 'react-router-dom';

const ChatbotWidget = () => {
  const { API_URL, user } = useAppContext();
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hi! I am CareBot. I can help you navigate the app, book appointments, or fill out your medical history. How can I help?' }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isOpen]);

  const handleSend = async (overrideText = null) => {
    const textToSend = typeof overrideText === 'string' ? overrideText : inputValue;
    
    if (!textToSend.trim()) return;

    const newMsg = { role: 'user', content: textToSend };
    const updatedMessages = [...messages, newMsg];
    
    setMessages(updatedMessages);
    setInputValue('');
    setIsLoading(true);

    try {
      const payload = { 
        messages: updatedMessages,
        user_context: user ? { name: `${user.first_name} ${user.last_name}`, dob: user.date_of_birth, email: user.email } : null
      };
      const res = await axios.post(`${API_URL}/api/ai/chat`, payload);
      
      const aiResponse = res.data.message;
      const action = res.data.action;
      
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: aiResponse,
        showMedicalForm: action && action.type === 'show_medical_history_form',
        showMedicalOptions: action && action.type === 'show_medical_options_ui' // legacy support
      }]);

      // Execute Action Command if provided
      if (action) {
        if (action.type === 'navigate') {
          setTimeout(() => {
            navigate(action.payload.page);
            setIsOpen(false);
          }, 1500);
        } else if (action.type === 'show_medical_history_form') {
          // Don't navigate - the form is shown inline in the chat
        } else if (action.type === 'update_medical_history') {
          const conditions = action.payload.conditions;
          localStorage.setItem('pending_medical_conditions', JSON.stringify(conditions));
          window.dispatchEvent(new Event('bot_medical_update'));
        } else if (action.type === 'contact_agent') {
          alert(`Support agent has been notified with ${action.payload.urgency} urgency.`);
        }
      }

    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: "Sorry, I'm having trouble connecting right now." }]);
    }
    
    setIsLoading(false);
  };

  // All 44 conditions from the medical history form
  const ALL_CONDITIONS = [
    "Acquired Respiratory Distress Syndrome", "Angina", "Anxiety or Panic Disorders",
    "Arthritis (RA, OA)", "Asthma", "Chronic Obstructive Pulmonary Disease (COPD)",
    "Congestive Heart Failure (CHF)", "Degenerative Disc Disease", "Depression",
    "Diabetes", "Emphysema", "Hearing Impairment", "Heart Attack",
    "Multiple Sclerosis", "Osteoporosis", "Parkinson's Disease",
    "Peripheral Vascular Disease", "Stroke or TIA",
    "Upper Gastrointestinal Disease", "Visual Impairment",
    "Allergies", "Headaches", "Back Injury", "Bleeding Disorders",
    "Bowel / Bladder Abnormalities", "Cancer", "Dizzy or Fainting Spells",
    "Epilepsy or Seizure Disorder", "Fracture", "Hepatitis A, B, C",
    "Hernia", "High Blood Pressure", "Hypoglycemia",
    "Immunosuppressant Condition or Medication", "Kidney Problems",
    "Liver / Gallbladder Problems", "Metal Implants", "Nausea / Vomiting",
    "Pacemaker", "Pregnancy", "Ringing in Your Ears",
    "Sexual Dysfunction", "Skin Abnormalities", "Smoking",
    "Special Diet Guidelines", "Tuberculosis"
  ];

  // Medical History Form component for inline display
  const MedicalHistoryForm = ({ onComplete }) => {
    const [selected, setSelected] = useState([]);
    const [step, setStep] = useState(1);
    const [formInfo, setFormInfo] = useState({
      patient_name: user ? `${user.first_name} ${user.last_name}` : '',
      dob: user ? user.date_of_birth || '' : '',
      height_ft: '', height_in: '', weight: '',
      diagnosis: '',
      hospitalized: false,
      surgery: false,
      current_medications: '',
      emergency_contact: ''
    });
    
    const toggle = (c) => setSelected(prev => prev.includes(c) ? prev.filter(x => x !== c) : [...prev, c]);

    const handleSave = async () => {
      if (user) {
        try {
          // Map selected conditions to boolean fields
          const conditionMap = {
            "Acquired Respiratory Distress Syndrome": "acquired_respiratory_distress",
            "Angina": "angina", "Anxiety or Panic Disorders": "anxiety_panic",
            "Arthritis (RA, OA)": "arthritis", "Asthma": "asthma",
            "Chronic Obstructive Pulmonary Disease (COPD)": "copd",
            "Congestive Heart Failure (CHF)": "chf", "Degenerative Disc Disease": "degenerative_disc",
            "Depression": "depression", "Diabetes": "diabetes",
            "Emphysema": "emphysema", "Hearing Impairment": "hearing_impairment",
            "Heart Attack": "heart_attack", "Multiple Sclerosis": "multiple_sclerosis",
            "Osteoporosis": "osteoporosis", "Parkinson's Disease": "parkinsons",
            "Peripheral Vascular Disease": "peripheral_vascular",
            "Stroke or TIA": "stroke_tia", "Upper Gastrointestinal Disease": "upper_gi_disease",
            "Visual Impairment": "visual_impairment",
            "Allergies": "allergies", "Headaches": "headaches",
            "Back Injury": "back_injury", "Bleeding Disorders": "bleeding_disorders",
            "Bowel / Bladder Abnormalities": "bowel_bladder", "Cancer": "cancer",
            "Dizzy or Fainting Spells": "dizzy_fainting",
            "Epilepsy or Seizure Disorder": "epilepsy_seizure",
            "Fracture": "fracture", "Hepatitis A, B, C": "hepatitis",
            "Hernia": "hernia", "High Blood Pressure": "high_blood_pressure",
            "Hypoglycemia": "hypoglycemia",
            "Immunosuppressant Condition or Medication": "immunosuppressant",
            "Kidney Problems": "kidney_problems",
            "Liver / Gallbladder Problems": "liver_gallbladder",
            "Metal Implants": "metal_implants", "Nausea / Vomiting": "nausea_vomiting",
            "Pacemaker": "pacemaker", "Pregnancy": "pregnancy",
            "Ringing in Your Ears": "ringing_ears",
            "Sexual Dysfunction": "sexual_dysfunction",
            "Skin Abnormalities": "skin_abnormalities", "Smoking": "smoking",
            "Special Diet Guidelines": "special_diet", "Tuberculosis": "tuberculosis"
          };

          const payload = {
            patient_id: user.id, // Only works if logged in currently, but the UI supports collecting the name
            patient_name: formInfo.patient_name || `${user.first_name} ${user.last_name}`,
            dob: formInfo.dob || null,
            height_ft: formInfo.height_ft ? parseInt(formInfo.height_ft) : null,
            height_in: formInfo.height_in ? parseInt(formInfo.height_in) : null,
            weight: formInfo.weight ? parseFloat(formInfo.weight) : null,
            diagnosis: formInfo.diagnosis || null,
            hospitalized: formInfo.hospitalized,
            surgery: formInfo.surgery,
            current_medications: formInfo.current_medications || null,
            emergency_contact_name: formInfo.emergency_contact || null,
          };

          // Set all conditions to false first, then true for selected
          Object.values(conditionMap).forEach(key => { payload[key] = false; });
          selected.forEach(cond => {
            const key = conditionMap[cond];
            if (key) payload[key] = true;
          });

          await axios.post(`${API_URL}/medical-history/`, payload);
          onComplete(selected);
        } catch (err) {
          console.error(err);
          onComplete(selected);
        }
      } else {
        onComplete(selected);
      }
    };

    return (
      <div style={{ marginTop: '12px', background: 'white', borderRadius: '12px', padding: '16px', border: '1px solid #e2e8f0', boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }}>
        {step === 1 && (
          <>
            <h4 style={{ margin: '0 0 12px 0', fontSize: '0.95rem', color: '#005f73', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <FileText size={16} /> Basic Information
            </h4>
            {!user && (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '10px' }}>
                <input type="text" placeholder="Full Name" value={formInfo.patient_name} onChange={e => setFormInfo(p => ({...p, patient_name: e.target.value}))}
                  style={{ padding: '8px', borderRadius: '6px', border: '1px solid #e2e8f0', fontSize: '0.8rem' }} />
                <input type="date" placeholder="DOB" value={formInfo.dob} onChange={e => setFormInfo(p => ({...p, dob: e.target.value}))}
                  style={{ padding: '8px', borderRadius: '6px', border: '1px solid #e2e8f0', fontSize: '0.8rem', color: formInfo.dob ? '#0f172a' : '#94a3b8' }} />
              </div>
            )}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '8px', marginBottom: '10px' }}>
              <input type="number" placeholder="Height (ft)" value={formInfo.height_ft} onChange={e => setFormInfo(p => ({...p, height_ft: e.target.value}))}
                style={{ padding: '8px', borderRadius: '6px', border: '1px solid #e2e8f0', fontSize: '0.8rem' }} />
              <input type="number" placeholder="Height (in)" value={formInfo.height_in} onChange={e => setFormInfo(p => ({...p, height_in: e.target.value}))}
                style={{ padding: '8px', borderRadius: '6px', border: '1px solid #e2e8f0', fontSize: '0.8rem' }} />
              <input type="number" placeholder="Weight (lbs)" value={formInfo.weight} onChange={e => setFormInfo(p => ({...p, weight: e.target.value}))}
                style={{ padding: '8px', borderRadius: '6px', border: '1px solid #e2e8f0', fontSize: '0.8rem' }} />
            </div>
            <input type="text" placeholder="Diagnosis (if any)" value={formInfo.diagnosis} onChange={e => setFormInfo(p => ({...p, diagnosis: e.target.value}))}
              style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #e2e8f0', fontSize: '0.8rem', marginBottom: '8px', boxSizing: 'border-box' }} />
            <input type="text" placeholder="Current Medications" value={formInfo.current_medications} onChange={e => setFormInfo(p => ({...p, current_medications: e.target.value}))}
              style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #e2e8f0', fontSize: '0.8rem', marginBottom: '8px', boxSizing: 'border-box' }} />
            <input type="text" placeholder="Emergency Contact Name" value={formInfo.emergency_contact} onChange={e => setFormInfo(p => ({...p, emergency_contact: e.target.value}))}
              style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #e2e8f0', fontSize: '0.8rem', marginBottom: '8px', boxSizing: 'border-box' }} />
            <div style={{ display: 'flex', gap: '16px', marginBottom: '8px' }}>
              <label style={{ fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
                <input type="checkbox" checked={formInfo.hospitalized} onChange={e => setFormInfo(p => ({...p, hospitalized: e.target.checked}))} style={{ accentColor: '#005f73' }} />
                Hospitalized before?
              </label>
              <label style={{ fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
                <input type="checkbox" checked={formInfo.surgery} onChange={e => setFormInfo(p => ({...p, surgery: e.target.checked}))} style={{ accentColor: '#005f73' }} />
                Had surgery?
              </label>
            </div>
            <button onClick={() => setStep(2)} style={{
              width: '100%', padding: '10px', background: '#005f73', color: 'white',
              border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: '600', fontSize: '0.85rem'
            }}>
              Next: Medical Conditions &rarr;
            </button>
          </>
        )}

        {step === 2 && (
          <>
            <h4 style={{ margin: '0 0 8px 0', fontSize: '0.95rem', color: '#005f73' }}>Select all conditions that apply:</h4>
            <p style={{ fontSize: '0.75rem', color: '#94a3b8', margin: '0 0 10px 0' }}>All conditions are shown. Check any that you have or have been treated for.</p>
            <div style={{ maxHeight: '250px', overflowY: 'auto', display: 'flex', flexWrap: 'wrap', gap: '5px', paddingRight: '4px' }}>
              {ALL_CONDITIONS.map(cond => (
                <button 
                  key={cond}
                  onClick={() => toggle(cond)}
                  style={{
                    background: selected.includes(cond) ? '#0f766e' : '#f8fafc', 
                    color: selected.includes(cond) ? 'white' : '#334155', 
                    border: selected.includes(cond) ? '1px solid #0f766e' : '1px solid #cbd5e1',
                    padding: '5px 9px', borderRadius: '14px', fontSize: '0.72rem', cursor: 'pointer',
                    transition: 'all 0.2s', whiteSpace: 'nowrap'
                  }}
                >
                  {cond}
                </button>
              ))}
            </div>
            <div style={{ display: 'flex', gap: '8px', marginTop: '12px' }}>
              <button onClick={() => setStep(1)} style={{
                flex: 1, padding: '10px', background: '#f1f5f9', color: '#64748b',
                border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: '600', fontSize: '0.85rem'
              }}>
                &larr; Back
              </button>
              <button onClick={handleSave} style={{
                flex: 2, padding: '10px', background: '#0d9488', color: 'white',
                border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold', fontSize: '0.85rem'
              }}>
                Save Medical History
              </button>
            </div>
          </>
        )}
      </div>
    );
  };

  return (
    <>
      {/* Floating Toggle Button */}
      <button 
        onClick={() => setIsOpen(!isOpen)}
        style={{
          position: 'fixed',
          bottom: '30px',
          right: '30px',
          width: '60px',
          height: '60px',
          borderRadius: '50%',
          background: 'linear-gradient(135deg, #0f766e 0%, #0d9488 100%)',
          color: 'white',
          border: 'none',
          boxShadow: '0 10px 25px rgba(13, 148, 136, 0.4)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          cursor: 'pointer',
          zIndex: 1000,
          transition: 'transform 0.3s ease'
        }}
        onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.1)'}
        onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
      >
        {isOpen ? <X size={28} /> : <MessageSquare size={28} />}
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div style={{
          position: 'fixed',
          bottom: '100px',
          right: '30px',
          width: '400px',
          height: '600px',
          backgroundColor: '#ffffff',
          borderRadius: '20px',
          boxShadow: '0 20px 40px rgba(0,0,0,0.15)',
          display: 'flex',
          flexDirection: 'column',
          zIndex: 999,
          overflow: 'hidden',
          animation: 'slideUp 0.3s ease-out'
        }}>
          {/* Header */}
          <div style={{
            background: 'linear-gradient(135deg, #0f766e 0%, #0d9488 100%)',
            padding: '20px',
            color: 'white',
            display: 'flex',
            alignItems: 'center',
            gap: '15px'
          }}>
            <div style={{ background: 'rgba(255,255,255,0.2)', padding: '10px', borderRadius: '50%' }}>
              <Bot size={24} />
            </div>
            <div>
              <h3 style={{ margin: 0, fontSize: '1.1rem' }}>CareBot Assistant</h3>
              <span style={{ fontSize: '0.85rem', color: 'rgba(255,255,255,0.8)' }}>Powered by OpenAI</span>
            </div>
          </div>

          {/* Messages Area */}
          <div style={{
            flex: 1,
            padding: '20px',
            overflowY: 'auto',
            display: 'flex',
            flexDirection: 'column',
            gap: '15px',
            background: '#f8fafc'
          }}>
            {messages.map((msg, idx) => (
              <div key={idx} style={{
                alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                maxWidth: (msg.showMedicalForm || msg.showMedicalOptions) ? '95%' : '80%',
                display: 'flex',
                flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
                gap: '10px',
                alignItems: (msg.showMedicalForm || msg.showMedicalOptions) ? 'flex-start' : 'flex-end'
              }}>
                <div style={{
                  background: msg.role === 'user' ? '#e2e8f0' : '#0f766e',
                  color: msg.role === 'user' ? '#334155' : 'white',
                  width: '30px', height: '30px', borderRadius: '50%',
                  display: 'flex', justifyContent: 'center', alignItems: 'center', flexShrink: 0,
                  marginTop: (msg.showMedicalForm || msg.showMedicalOptions) ? '5px' : '0'
                }}>
                  {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
                </div>
                <div style={{
                  background: msg.role === 'user' ? '#ffffff' : '#e0f2fe',
                  color: '#334155',
                  padding: '12px 16px',
                  borderRadius: msg.role === 'user' ? '18px 18px 0 18px' : '18px 18px 18px 0',
                  boxShadow: '0 2px 5px rgba(0,0,0,0.05)',
                  fontSize: '0.95rem',
                  lineHeight: '1.4',
                  width: '100%'
                }}>
                  {msg.content}
                  {(msg.showMedicalForm || msg.showMedicalOptions) && (
                    <MedicalHistoryForm 
                      onComplete={(conditions) => {
                        const count = conditions.length;
                        handleSend(count > 0 
                          ? `I've completed my medical history form. I have ${count} condition(s) checked.`
                          : "I've completed my medical history form with no conditions checked."
                        );
                      }} 
                    />
                  )}
                </div>
              </div>
            ))}
            {isLoading && (
              <div style={{ alignSelf: 'flex-start', display: 'flex', gap: '10px', alignItems: 'center', color: '#64748b' }}>
                <Loader2 size={18} className="spin-animation" /> <span>Thinking...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Actions */}
          <div style={{
            display: 'flex',
            gap: '8px',
            padding: '10px 20px',
            background: '#f8fafc',
            borderTop: '1px solid #e2e8f0',
            overflowX: 'auto',
            scrollbarWidth: 'none',
            msOverflowStyle: 'none'
          }}>
            {[
              "Book Appointment", 
              "Talk to Agent", 
              "Medical History", 
              "Check Insurance", 
              "Fill HIPAA Form"
            ].map((option, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(option)}
                style={{
                  whiteSpace: 'nowrap',
                  background: 'white',
                  color: '#0f766e',
                  border: '1px solid #0f766e',
                  padding: '6px 12px',
                  borderRadius: '16px',
                  fontSize: '0.8rem',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => { e.target.style.background = '#0f766e'; e.target.style.color = 'white'; }}
                onMouseLeave={(e) => { e.target.style.background = 'white'; e.target.style.color = '#0f766e'; }}
              >
                {option}
              </button>
            ))}
          </div>

          {/* Input Area */}
          <div style={{
            padding: '15px 20px',
            background: 'white',
            display: 'flex',
            gap: '10px'
          }}>
            <input 
              type="text" 
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask me anything..."
              style={{
                flex: 1,
                padding: '12px 16px',
                borderRadius: '24px',
                border: '1px solid #cbd5e1',
                outline: 'none',
                fontSize: '0.95rem',
                background: '#f8fafc'
              }}
            />
            <button 
              onClick={handleSend}
              disabled={isLoading || !inputValue.trim()}
              style={{
                background: '#0f766e',
                color: 'white',
                border: 'none',
                width: '44px', height: '44px',
                borderRadius: '50%',
                display: 'flex', justifyContent: 'center', alignItems: 'center',
                cursor: 'pointer',
                opacity: (isLoading || !inputValue.trim()) ? 0.5 : 1
              }}
            >
              <Send size={18} style={{ marginLeft: '2px' }} />
            </button>
          </div>
        </div>
      )}

      <style>{`
        @keyframes slideUp {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .spin-animation {
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </>
  );
};

export default ChatbotWidget;
