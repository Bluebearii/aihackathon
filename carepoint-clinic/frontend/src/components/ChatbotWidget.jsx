import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { MessageSquare, X, Send, Bot, User, Loader2 } from 'lucide-react';
import { useAppContext } from '../context/AppContext';
import { useNavigate } from 'react-router-dom';

const ChatbotWidget = () => {
  const { API_URL, user } = useAppContext();
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hi! I am CareBot. I can help you navigate the app, book appointments, or update your medical history. How can I help?' }
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
    // If it's an event object (from onClick), ignore it. If it's a string, use it.
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
        showMedicalOptions: action && action.type === 'show_medical_options_ui'
      }]);

      // Execute Action Command if provided
      if (action) {
        if (action.type === 'navigate') {
          setTimeout(() => {
            navigate(action.payload.page);
            setIsOpen(false);
          }, 1500);
        } else if (action.type === 'update_medical_history') {
          // Store medical conditions in local storage or trigger a context update
          const conditions = action.payload.conditions;
          localStorage.setItem('pending_medical_conditions', JSON.stringify(conditions));
          // If they aren't on the medical history form, maybe send them to the signup or dashboard
        } else if (action.type === 'contact_agent') {
          alert(`Support agent has been notified with ${action.payload.urgency} urgency.`);
        }
      }

    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: "Sorry, I'm having trouble connecting right now." }]);
    }
    
    setIsLoading(false);
  };

  const COMMON_CONDITIONS = [
    "Acquired Respiratory Distress Syndrome", "Angina", "Anxiety or Panic Disorders",
    "Arthritis (RA, OA)", "Asthma", "Chronic Obstructive Pulmonary Disease (COPD)",
    "Congestive Heart Failure (CHF)", "Degenerative Disc Disease", "Depression",
    "Diabetes", "Emphysema", "Hearing Impairment", "Heart Attack",
    "Multiple Sclerosis", "Osteoporosis", "Parkinson's Disease", "Stroke or TIA",
    "Allergies", "Headaches", "Back Injury", "Bleeding Disorders", "Cancer",
    "Epilepsy or Seizure Disorder", "Hepatitis A, B, C", "High Blood Pressure"
  ];

  // Helper component to handle local selection state
  const MedicalOptionsList = ({ onSelect }) => {
    const [selected, setSelected] = useState([]);
    const toggle = (c) => setSelected(prev => prev.includes(c) ? prev.filter(x => x!==c) : [...prev, c]);
    
    return (
      <div style={{ marginTop: '15px', background: 'white', borderRadius: '12px', padding: '15px', border: '1px solid #e2e8f0', boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }}>
        <h4 style={{ margin: '0 0 10px 0', fontSize: '0.9rem', color: '#334155' }}>Select all that apply:</h4>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
          {COMMON_CONDITIONS.map(cond => (
            <button 
              key={cond}
              onClick={() => toggle(cond)}
              style={{
                background: selected.includes(cond) ? '#0f766e' : '#f8fafc', 
                color: selected.includes(cond) ? 'white' : '#334155', 
                border: selected.includes(cond) ? '1px solid #0f766e' : '1px solid #cbd5e1',
                padding: '6px 10px', borderRadius: '16px', fontSize: '0.8rem', cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              {cond}
            </button>
          ))}
        </div>
        <button 
          onClick={() => {
            if (selected.length > 0) {
              onSelect(`I have the following conditions: ${selected.join(', ')}`);
            } else {
              onSelect("I don't have any of these conditions.");
            }
          }}
          style={{
            marginTop: '15px', width: '100%', padding: '10px', background: '#0d9488', color: 'white',
            border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold'
          }}
        >
          Submit Medical History
        </button>
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
          width: '380px',
          height: '550px',
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
                maxWidth: msg.showMedicalOptions ? '95%' : '80%',
                display: 'flex',
                flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
                gap: '10px',
                alignItems: msg.showMedicalOptions ? 'flex-start' : 'flex-end'
              }}>
                <div style={{
                  background: msg.role === 'user' ? '#e2e8f0' : '#0f766e',
                  color: msg.role === 'user' ? '#334155' : 'white',
                  width: '30px', height: '30px', borderRadius: '50%',
                  display: 'flex', justifyContent: 'center', alignItems: 'center', flexShrink: 0,
                  marginTop: msg.showMedicalOptions ? '5px' : '0'
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
                  {msg.showMedicalOptions && <MedicalOptionsList onSelect={(res) => handleSend(res)} />}
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
            scrollbarWidth: 'none', // Hide scrollbar for Firefox
            msOverflowStyle: 'none' // Hide scrollbar for IE/Edge
          }}>
            <style>{`div::-webkit-scrollbar { display: none; }`}</style>
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
