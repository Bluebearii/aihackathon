import React, { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import { useAppContext } from '../context/AppContext';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, ChevronRight, Plus, X, Clock, User, Filter, Eye } from 'lucide-react';

const STATUS_COLORS = {
  'Pending': { bg: '#fef3c7', color: '#92400e', border: '#fbbf24' },
  'Confirmed': { bg: '#dbeafe', color: '#1e40af', border: '#3b82f6' },
  'Completed': { bg: '#dcfce7', color: '#166534', border: '#22c55e' },
  'Cancelled': { bg: '#f3f4f6', color: '#4b5563', border: '#9ca3af' },
  'No Show': { bg: '#fee2e2', color: '#991b1b', border: '#ef4444' },
  'Rescheduled': { bg: '#fae8ff', color: '#86198f', border: '#c084fc' },
};

const VIEWS = ['Month', 'Week', 'Day'];
const APPOINTMENT_TYPES = ['Annual Eye Exam', 'Contact Lens Exam', 'Follow-up Visit', 'Medical Office Visit', 'New Patient Visit', 'Emergency Visit', 'Consultation'];
const PROVIDERS = ['Dr. Smith', 'Dr. Patel', 'Dr. Lee'];

const CalendarPage = ({ isWidget = false }) => {
  const { user, API_URL } = useAppContext();
  const navigateUrl = useNavigate();
  const [currentDate, setCurrentDate] = useState(new Date());
  const [view, setView] = useState('Month');
  const [appointments, setAppointments] = useState([]);
  const [selectedAppointment, setSelectedAppointment] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [filterProvider, setFilterProvider] = useState('');
  const [filterType, setFilterType] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [patientProfile, setPatientProfile] = useState(null);

  useEffect(() => {
    if (showModal && selectedAppointment) {
      axios.get(`${API_URL}/patients/${selectedAppointment.patient_id}/profile`)
        .then(res => setPatientProfile(res.data))
        .catch(err => {
          console.error(err);
          setPatientProfile(null);
        });
    } else {
      setPatientProfile(null);
    }
  }, [showModal, selectedAppointment, API_URL]);

  useEffect(() => {
    fetchAppointments();
  }, [currentDate]);

  const fetchAppointments = async () => {
    try {
      const res = await axios.get(`${API_URL}/appointments/calendar`);
      setAppointments(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const filteredAppointments = useMemo(() => {
    return appointments.filter(a => {
      if (filterProvider && a.provider !== filterProvider) return false;
      if (filterType && a.appointment_type !== filterType) return false;
      if (filterStatus && a.status !== filterStatus) return false;
      return true;
    });
  }, [appointments, filterProvider, filterType, filterStatus]);

  const navigate = (direction) => {
    const d = new Date(currentDate);
    if (view === 'Month') d.setMonth(d.getMonth() + direction);
    else if (view === 'Week') d.setDate(d.getDate() + direction * 7);
    else d.setDate(d.getDate() + direction);
    setCurrentDate(d);
  };

  const goToToday = () => setCurrentDate(new Date());

  const handleStatusUpdate = async (apptId, status) => {
    try {
      await axios.put(`${API_URL}/appointments/${apptId}/status?status=${status}`);
      if (status === 'Completed') {
        const appt = appointments.find(a => a.id === apptId);
        if (appt) {
          try {
            await axios.post(`${API_URL}/points/`, {
              points_added: 10,
              reason: `Showed up - ${appt.appointment_type}`,
              appointment_id: apptId,
              added_by_staff_id: user.id,
              patient_id: appt.patient_id
            });
          } catch (e) { /* points may already exist */ }
        }
      }
      fetchAppointments();
      setShowModal(false);
    } catch (err) {
      alert(err.response?.data?.detail || 'Error updating status');
    }
  };

  // ==========================================
  // Calendar Rendering Helpers
  // ==========================================

  const getDaysInMonth = (year, month) => new Date(year, month + 1, 0).getDate();
  const getFirstDayOfMonth = (year, month) => new Date(year, month, 1).getDay();

  const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const hours = Array.from({ length: 12 }, (_, i) => i + 7); // 7 AM to 6 PM

  const formatDateStr = (d) => {
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  const getAppointmentsForDate = (dateStr) => {
    return filteredAppointments.filter(a => a.appointment_date === dateStr);
  };

  const isToday = (dateStr) => formatDateStr(new Date()) === dateStr;

  // ==========================================
  // Month View
  // ==========================================
  const renderMonthView = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    const daysInMonth = getDaysInMonth(year, month);
    const firstDay = getFirstDayOfMonth(year, month);
    const cells = [];

    // Empty cells before first day
    for (let i = 0; i < firstDay; i++) {
      cells.push(<div key={`empty-${i}`} style={{ background: '#f8fafc', borderRadius: '8px', minHeight: '120px' }}></div>);
    }

    for (let day = 1; day <= daysInMonth; day++) {
      const dateStr = formatDateStr(new Date(year, month, day));
      const dayAppts = getAppointmentsForDate(dateStr);
      const today = isToday(dateStr);

      cells.push(
        <div key={day} style={{
          background: today ? '#f0fdf4' : (isWidget ? 'transparent' : 'white'),
          borderRadius: '10px',
          border: today ? '2px solid #22c55e' : '1px solid #e2e8f0',
          minHeight: '120px',
          padding: '10px',
          cursor: 'pointer',
          transition: 'all 0.2s',
          position: 'relative',
        }}
        onClick={(e) => {
          setCurrentDate(new Date(year, month, day));
          setView('Day');
        }}
        onMouseEnter={e => {
          e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
          e.currentTarget.style.background = '#f8fafc';
        }}
        onMouseLeave={e => {
          e.currentTarget.style.boxShadow = 'none';
          e.currentTarget.style.background = today ? '#f0fdf4' : (isWidget ? 'transparent' : 'white');
        }}
        >
          <div style={{
            fontWeight: today ? '700' : '600',
            fontSize: '0.9rem',
            color: today ? '#22c55e' : '#334155',
            marginBottom: '8px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <span>{day}</span>
            {today && <span style={{ fontSize: '0.65rem', background: '#22c55e', color: 'white', padding: '2px 6px', borderRadius: '10px' }}>TODAY</span>}
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
            {dayAppts.slice(0, 3).map((appt, idx) => {
              const isOwnOrAdmin = user?.role === 'admin' || user?.id === appt.patient_id;
              const statusColor = STATUS_COLORS[appt.status] || STATUS_COLORS['Pending'];
              return (
                <div
                  key={idx}
                  onClick={(e) => { 
                    e.stopPropagation(); 
                    if (isOwnOrAdmin) { setSelectedAppointment(appt); setShowModal(true); } 
                  }}
                  style={{
                    background: isOwnOrAdmin ? statusColor.bg : '#fee2e2',
                    color: isOwnOrAdmin ? statusColor.color : '#991b1b',
                    borderLeft: `3px solid ${isOwnOrAdmin ? statusColor.border : '#ef4444'}`,
                    padding: '3px 6px',
                    borderRadius: '4px',
                    fontSize: '0.7rem',
                    fontWeight: '600',
                    cursor: isOwnOrAdmin ? 'pointer' : 'default',
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis'
                  }}
                >
                  {isOwnOrAdmin 
                    ? `${appt.appointment_time?.substring(0, 5)} ${appt.patient_name?.split(' ')[0]}`
                    : `${appt.appointment_time?.substring(0, 5)} Unavailable`}
                </div>
              );
            })}
            {dayAppts.length > 3 && (
              <div style={{ fontSize: '0.65rem', color: '#64748b', fontWeight: '600' }}>
                +{dayAppts.length - 3} more
              </div>
            )}
          </div>
        </div>
      );
    }

    return (
      <div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '4px', marginBottom: '4px' }}>
          {dayNames.map(d => (
            <div key={d} style={{ textAlign: 'center', fontWeight: '700', fontSize: '0.85rem', color: '#64748b', padding: '10px 0' }}>
              {d}
            </div>
          ))}
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '4px' }}>
          {cells}
        </div>
      </div>
    );
  };

  // ==========================================
  // Week View
  // ==========================================
  const renderWeekView = () => {
    const startOfWeek = new Date(currentDate);
    startOfWeek.setDate(currentDate.getDate() - currentDate.getDay());

    const weekDays = Array.from({ length: 7 }, (_, i) => {
      const d = new Date(startOfWeek);
      d.setDate(startOfWeek.getDate() + i);
      return d;
    });

    return (
      <div style={{ display: 'flex', gap: '2px', overflow: 'hidden' }}>
        {/* Time column */}
        <div style={{ width: '60px', flexShrink: 0 }}>
          <div style={{ height: '50px' }}></div>
          {hours.map(h => (
            <div key={h} style={{ height: '80px', fontSize: '0.75rem', color: '#94a3b8', textAlign: 'right', paddingRight: '8px', paddingTop: '2px' }}>
              {h > 12 ? `${h - 12} PM` : h === 12 ? '12 PM' : `${h} AM`}
            </div>
          ))}
        </div>

        {/* Day columns */}
        {weekDays.map((day, dayIdx) => {
          const dateStr = formatDateStr(day);
          const dayAppts = getAppointmentsForDate(dateStr);
          const today = isToday(dateStr);

          return (
            <div key={dayIdx} style={{ flex: 1, minWidth: 0, borderLeft: '1px solid #e2e8f0' }}>
              <div style={{
                height: '50px',
                textAlign: 'center',
                padding: '6px',
                background: today ? '#f0fdf4' : '#fafafa',
                borderBottom: '1px solid #e2e8f0',
                borderRadius: '6px 6px 0 0'
              }}>
                <div style={{ fontSize: '0.75rem', color: '#94a3b8', fontWeight: '600' }}>{dayNames[dayIdx]}</div>
                <div style={{
                  fontSize: '1.1rem',
                  fontWeight: '700',
                  background: today ? '#22c55e' : 'transparent',
                  color: today ? 'white' : '#334155',
                  width: '28px',
                  height: '28px',
                  borderRadius: '50%',
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  {day.getDate()}
                </div>
              </div>
              <div style={{ position: 'relative' }}>
                {hours.map(h => (
                  <div key={h} style={{ height: '80px', borderBottom: '1px solid #f1f5f9' }}></div>
                ))}
                {/* Render appointments */}
                {dayAppts.map((appt, idx) => {
                  const timeParts = appt.appointment_time?.split(':') || ['9', '0'];
                  const hour = parseInt(timeParts[0]);
                  const minute = parseInt(timeParts[1]);
                  const top = (hour - 7) * 80 + (minute / 60) * 80;
                  const isOwnOrAdmin = user?.role === 'admin' || user?.id === appt.patient_id;
                  const statusColor = STATUS_COLORS[appt.status] || STATUS_COLORS['Pending'];

                  return (
                    <div
                      key={idx}
                      onClick={(e) => { 
                        e.stopPropagation();
                        if (isOwnOrAdmin) { setSelectedAppointment(appt); setShowModal(true); } 
                      }}
                      style={{
                        position: 'absolute',
                        top: `${top}px`,
                        left: '2px',
                        right: '2px',
                        height: '70px',
                        background: isOwnOrAdmin ? statusColor.bg : '#fee2e2',
                        borderLeft: `3px solid ${isOwnOrAdmin ? statusColor.border : '#ef4444'}`,
                        borderRadius: '4px',
                        padding: '4px 6px',
                        fontSize: '0.7rem',
                        overflow: 'hidden',
                        cursor: isOwnOrAdmin ? 'pointer' : 'default',
                        zIndex: 2,
                        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                        transition: 'transform 0.1s'
                      }}
                      onMouseEnter={e => e.currentTarget.style.transform = isOwnOrAdmin ? 'scale(1.02)' : 'scale(1)'}
                      onMouseLeave={e => e.currentTarget.style.transform = 'scale(1)'}
                    >
                      <div style={{ fontWeight: '700', color: isOwnOrAdmin ? statusColor.color : '#991b1b', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {isOwnOrAdmin ? appt.patient_name : 'Unavailable'}
                      </div>
                      <div style={{ color: isOwnOrAdmin ? statusColor.color : '#991b1b', opacity: 0.8 }}>
                        {appt.appointment_time?.substring(0, 5)} {isOwnOrAdmin ? `· ${appt.appointment_type}` : ''}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  // ==========================================
  // Day View
  // ==========================================
  const renderDayView = () => {
    const dateStr = formatDateStr(currentDate);
    const dayAppts = getAppointmentsForDate(dateStr);
    const today = isToday(dateStr);

    return (
      <div style={{ display: 'flex', gap: '2px' }}>
        {/* Time column */}
        <div style={{ width: '80px', flexShrink: 0 }}>
          {hours.map(h => (
            <div key={h} style={{ height: '100px', fontSize: '0.85rem', color: '#94a3b8', textAlign: 'right', paddingRight: '12px', paddingTop: '2px', fontWeight: '500' }}>
              {h > 12 ? `${h - 12}:00 PM` : h === 12 ? '12:00 PM' : `${h}:00 AM`}
            </div>
          ))}
        </div>

        {/* Main area */}
        <div style={{ flex: 1, position: 'relative', borderLeft: '2px solid #e2e8f0' }}>
          {hours.map(h => {
            const timeStr = `${h < 10 ? '0' + h : h}:00`;
            return (
              <div key={h} style={{ height: '100px', borderBottom: '1px solid #f1f5f9', cursor: 'pointer' }}
                   onClick={() => navigateUrl(user?.role === 'admin' ? `/admin/book?date=${dateStr}&time=${timeStr}` : `/book?date=${dateStr}&time=${timeStr}`)}
                   onMouseEnter={e => e.currentTarget.style.background = '#f8fafc'}
                   onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
              ></div>
            );
          })}
          {dayAppts.map((appt, idx) => {
            const timeParts = appt.appointment_time?.split(':') || ['9', '0'];
            const hour = parseInt(timeParts[0]);
            const minute = parseInt(timeParts[1]);
            const top = (hour - 7) * 100 + (minute / 60) * 100;
            const isOwnOrAdmin = user?.role === 'admin' || user?.id === appt.patient_id;
            const statusColor = STATUS_COLORS[appt.status] || STATUS_COLORS['Pending'];

            return (
              <div
                key={idx}
                onClick={(e) => { 
                  e.stopPropagation(); 
                  if (isOwnOrAdmin) { setSelectedAppointment(appt); setShowModal(true); } 
                }}
                style={{
                  position: 'absolute',
                  top: `${top}px`,
                  left: '8px',
                  right: '8px',
                  height: '90px',
                  background: isOwnOrAdmin ? statusColor.bg : '#fee2e2',
                  borderLeft: `4px solid ${isOwnOrAdmin ? statusColor.border : '#ef4444'}`,
                  borderRadius: '8px',
                  padding: '10px 14px',
                  cursor: isOwnOrAdmin ? 'pointer' : 'default',
                  boxShadow: '0 2px 6px rgba(0,0,0,0.08)',
                  display: 'flex',
                  gap: '16px',
                  alignItems: 'center',
                  transition: 'transform 0.1s, box-shadow 0.2s'
                }}
                onMouseEnter={e => { 
                  if (isOwnOrAdmin) {
                    e.currentTarget.style.transform = 'scale(1.01)'; 
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)'; 
                  }
                }}
                onMouseLeave={e => { 
                  if (isOwnOrAdmin) {
                    e.currentTarget.style.transform = 'scale(1)'; 
                    e.currentTarget.style.boxShadow = '0 2px 6px rgba(0,0,0,0.08)'; 
                  }
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Clock size={14} color={isOwnOrAdmin ? statusColor.color : '#991b1b'} />
                  <span style={{ fontWeight: '700', color: isOwnOrAdmin ? statusColor.color : '#991b1b', fontSize: '0.9rem' }}>{appt.appointment_time?.substring(0, 5)}</span>
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: '700', color: isOwnOrAdmin ? statusColor.color : '#991b1b', fontSize: '0.95rem' }}>
                    {isOwnOrAdmin ? appt.patient_name : 'Unavailable Slot'}
                  </div>
                  {isOwnOrAdmin && (
                    <div style={{ fontSize: '0.8rem', color: statusColor.color, opacity: 0.75 }}>
                      {appt.appointment_type} · {appt.provider}
                    </div>
                  )}
                </div>
                {isOwnOrAdmin && (
                  <span style={{
                    background: statusColor.border,
                    color: 'white',
                    padding: '4px 10px',
                    borderRadius: '12px',
                    fontSize: '0.75rem',
                    fontWeight: '600'
                  }}>
                    {appt.status}
                  </span>
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  if (!user) {
    return (
      <div className="container">
        <div className="card" style={{ textAlign: 'center' }}>
          <h2>Access Denied</h2>
          <p>Please log in to view the calendar.</p>
        </div>
      </div>
    );
  }

  const headerLabel = view === 'Month'
    ? `${monthNames[currentDate.getMonth()]} ${currentDate.getFullYear()}`
    : view === 'Week'
    ? (() => {
        const start = new Date(currentDate);
        start.setDate(currentDate.getDate() - currentDate.getDay());
        const end = new Date(start);
        end.setDate(start.getDate() + 6);
        return `${monthNames[start.getMonth()]} ${start.getDate()} - ${monthNames[end.getMonth()]} ${end.getDate()}, ${end.getFullYear()}`;
      })()
    : `${monthNames[currentDate.getMonth()]} ${currentDate.getDate()}, ${currentDate.getFullYear()}`;

  return (
    <div className={isWidget ? "" : "container animate-slide-up"}>
      {!isWidget && (
        <div style={{ marginBottom: '1.5rem' }}>
          <h1 style={{ marginBottom: '0.5rem' }}>📅 Clinic Calendar</h1>
          <p>Manage appointment schedules and track patient visits.</p>
        </div>
      )}

      {/* Controls Bar */}
      <div className={isWidget ? "" : "card"} style={{ 
        padding: isWidget ? '16px 20px' : '16px 24px', 
        marginBottom: '1.5rem',
        background: 'white',
        border: isWidget ? 'none' : '1px solid #e2e8f0',
        borderRadius: '12px'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <button onClick={() => navigate(-1)} style={{ background: '#f1f5f9', border: 'none', borderRadius: '8px', padding: '8px', cursor: 'pointer', display: 'flex' }}>
              <ChevronLeft size={20} />
            </button>
            <h2 style={{ margin: 0, fontSize: '1.3rem', minWidth: '250px', textAlign: 'center' }}>{headerLabel}</h2>
            <button onClick={() => navigate(1)} style={{ background: '#f1f5f9', border: 'none', borderRadius: '8px', padding: '8px', cursor: 'pointer', display: 'flex' }}>
              <ChevronRight size={20} />
            </button>
            <button onClick={goToToday} className="btn btn-outline" style={{ padding: '6px 16px', fontSize: '0.85rem' }}>Today</button>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {/* View Buttons */}
            <div style={{ display: 'flex', background: '#f1f5f9', borderRadius: '8px', overflow: 'hidden' }}>
              {VIEWS.map(v => (
                <button
                  key={v}
                  onClick={() => setView(v)}
                  style={{
                    padding: '8px 16px',
                    border: 'none',
                    background: view === v ? '#005f73' : 'transparent',
                    color: view === v ? 'white' : '#64748b',
                    fontWeight: '600',
                    fontSize: '0.85rem',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                >
                  {v}
                </button>
              ))}
            </div>
            <button onClick={() => setShowFilters(!showFilters)} style={{
              background: showFilters ? '#005f73' : '#f1f5f9',
              color: showFilters ? 'white' : '#64748b',
              border: 'none',
              borderRadius: '8px',
              padding: '8px 12px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontWeight: '600',
              fontSize: '0.85rem'
            }}>
              <Filter size={16} /> Filters
            </button>
          </div>
        </div>

        {/* Filter Row */}
        {showFilters && (
          <div style={{ display: 'flex', gap: '12px', marginTop: '16px', paddingTop: '16px', borderTop: '1px solid #e2e8f0', flexWrap: 'wrap' }}>
            <select className="form-control" value={filterProvider} onChange={e => setFilterProvider(e.target.value)} style={{ width: 'auto', padding: '8px 12px' }}>
              <option value="">All Providers</option>
              {PROVIDERS.map(p => <option key={p} value={p}>{p}</option>)}
            </select>
            <select className="form-control" value={filterType} onChange={e => setFilterType(e.target.value)} style={{ width: 'auto', padding: '8px 12px' }}>
              <option value="">All Types</option>
              {APPOINTMENT_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
            <select className="form-control" value={filterStatus} onChange={e => setFilterStatus(e.target.value)} style={{ width: 'auto', padding: '8px 12px' }}>
              <option value="">All Statuses</option>
              {Object.keys(STATUS_COLORS).map(s => <option key={s} value={s}>{s}</option>)}
            </select>
            {(filterProvider || filterType || filterStatus) && (
              <button onClick={() => { setFilterProvider(''); setFilterType(''); setFilterStatus(''); }} className="btn btn-outline" style={{ padding: '6px 12px', fontSize: '0.85rem' }}>Clear</button>
            )}
          </div>
        )}

        {/* Status Legend */}
        <div style={{ display: 'flex', gap: '16px', marginTop: '12px', flexWrap: 'wrap' }}>
          {Object.entries(STATUS_COLORS).map(([status, colors]) => (
            <div key={status} style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem' }}>
              <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: colors.border }}></div>
              <span style={{ color: '#64748b' }}>{status}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="card" style={{ 
        padding: view === 'Month' ? '16px' : '0', 
        overflow: 'auto', 
        maxHeight: view === 'Month' ? 'none' : '800px',
        background: 'white',
        border: isWidget ? 'none' : '1px solid #e2e8f0',
      }}>
        {view === 'Month' && renderMonthView()}
        {view === 'Week' && renderWeekView()}
        {view === 'Day' && renderDayView()}
      </div>

      {/* Appointment Detail Modal */}
      {showModal && selectedAppointment && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center',
          zIndex: 1000, animation: 'fadeIn 0.2s ease'
        }} onClick={() => setShowModal(false)}>
          <div style={{
            background: 'white', borderRadius: '16px', padding: '32px', maxWidth: '500px', width: '90%',
            boxShadow: '0 20px 60px rgba(0,0,0,0.3)', animation: 'slideUp 0.3s ease'
          }} onClick={e => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
              <h3 style={{ margin: 0 }}>Appointment Details</h3>
              <button onClick={() => setShowModal(false)} style={{ background: '#f1f5f9', border: 'none', borderRadius: '8px', padding: '6px', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{ background: '#f0f9ff', padding: '10px', borderRadius: '50%' }}>
                  <User size={20} color="#005f73" />
                </div>
                <div>
                  <div style={{ fontWeight: '700', fontSize: '1.1rem' }}>{selectedAppointment.patient_name}</div>
                  <div style={{ color: '#64748b', fontSize: '0.9rem' }}>Patient ID: {selectedAppointment.patient_id}</div>
                </div>
              </div>

              <div style={{ background: '#f8fafc', borderRadius: '12px', padding: '16px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div><strong style={{ color: '#64748b', fontSize: '0.8rem' }}>DATE</strong><br />{selectedAppointment.appointment_date}</div>
                <div><strong style={{ color: '#64748b', fontSize: '0.8rem' }}>TIME</strong><br />{selectedAppointment.appointment_time}</div>
                <div><strong style={{ color: '#64748b', fontSize: '0.8rem' }}>TYPE</strong><br />{selectedAppointment.appointment_type}</div>
                <div><strong style={{ color: '#64748b', fontSize: '0.8rem' }}>PROVIDER</strong><br />{selectedAppointment.provider || 'Unassigned'}</div>
              </div>

              <div>
                <strong style={{ color: '#64748b', fontSize: '0.8rem' }}>STATUS</strong>
                <div style={{ marginTop: '4px' }}>
                  <span style={{
                    background: (STATUS_COLORS[selectedAppointment.status] || STATUS_COLORS['Pending']).bg,
                    color: (STATUS_COLORS[selectedAppointment.status] || STATUS_COLORS['Pending']).color,
                    padding: '4px 12px', borderRadius: '12px', fontWeight: '600', fontSize: '0.85rem'
                  }}>
                    {selectedAppointment.status}
                  </span>
                </div>
              </div>

              {selectedAppointment.reason_for_visit && (
                <div>
                  <strong style={{ color: '#64748b', fontSize: '0.8rem' }}>REASON</strong>
                  <p style={{ margin: '4px 0 0', color: '#334155' }}>{selectedAppointment.reason_for_visit}</p>
                </div>
              )}
              {selectedAppointment.notes && (
                <div>
                  <strong style={{ color: '#64748b', fontSize: '0.8rem' }}>NOTES</strong>
                  <p style={{ margin: '4px 0 0', color: '#334155' }}>{selectedAppointment.notes}</p>
                </div>
              )}

              {patientProfile && (
                <div style={{ marginTop: '12px', borderTop: '1px solid #e2e8f0', paddingTop: '16px' }}>
                  <strong style={{ color: '#0f172a', fontSize: '1rem', display: 'block', marginBottom: '8px' }}>Patient Profile</strong>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', fontSize: '0.9rem', color: '#334155' }}>
                    <div><strong>DOB:</strong> {patientProfile.patient.date_of_birth || 'N/A'}</div>
                    <div><strong>Phone:</strong> {patientProfile.patient.phone || 'N/A'}</div>
                    <div style={{ gridColumn: '1 / -1' }}><strong>Email:</strong> {patientProfile.patient.email}</div>
                  </div>
                  
                  {patientProfile.medical_history ? (
                    <div style={{ marginTop: '16px' }}>
                      <strong style={{ color: '#0f172a', fontSize: '0.95rem' }}>Medical History</strong>
                      <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px', marginTop: '8px', fontSize: '0.85rem', color: '#475569', maxHeight: '150px', overflowY: 'auto' }}>
                        <div><strong>Diagnosis:</strong> {patientProfile.medical_history.diagnosis || 'None'}</div>
                        <div><strong>Allergies:</strong> {patientProfile.medical_history.latex_allergy_yes ? 'Latex ' : ''} {patientProfile.medical_history.topical_allergy}</div>
                        <div><strong>Surgeries:</strong> {patientProfile.medical_history.surgery ? patientProfile.medical_history.surgery_type : 'None'}</div>
                        {patientProfile.medical_history.asthma && <div>• Asthma</div>}
                        {patientProfile.medical_history.diabetes && <div>• Diabetes</div>}
                        {patientProfile.medical_history.high_blood_pressure && <div>• High Blood Pressure</div>}
                      </div>
                    </div>
                  ) : (
                    <div style={{ marginTop: '12px', color: '#94a3b8', fontSize: '0.9rem', fontStyle: 'italic' }}>No medical history submitted yet.</div>
                  )}
                </div>
              )}

              {/* Action Buttons */}
              {(selectedAppointment.status === 'Pending' || selectedAppointment.status === 'Confirmed') && (
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginTop: '8px' }}>
                  <button onClick={() => handleStatusUpdate(selectedAppointment.id, 'Completed')} className="btn" style={{ background: '#22c55e', color: 'white', flex: 1, padding: '10px' }}>
                    ✓ Mark Showed Up (+10 pts)
                  </button>
                  <button onClick={() => handleStatusUpdate(selectedAppointment.id, 'No Show')} className="btn" style={{ background: '#ef4444', color: 'white', flex: 1, padding: '10px' }}>
                    ✗ No Show
                  </button>
                  <button onClick={() => handleStatusUpdate(selectedAppointment.id, 'Cancelled')} className="btn" style={{ background: '#9ca3af', color: 'white', flex: 1, padding: '10px' }}>
                    Cancel
                  </button>
                  <button onClick={() => handleStatusUpdate(selectedAppointment.id, 'Rescheduled')} className="btn" style={{ background: '#c084fc', color: 'white', flex: 1, padding: '10px' }}>
                    Reschedule
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      <style>{`
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
      `}</style>
    </div>
  );
};

export default CalendarPage;
