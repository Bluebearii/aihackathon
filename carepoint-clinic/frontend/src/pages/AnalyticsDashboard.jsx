import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAppContext } from '../context/AppContext';

const AnalyticsDashboard = () => {
  const { user, API_URL } = useAppContext();
  const [dashboards, setDashboards] = useState([]);
  const [activeUrl, setActiveUrl] = useState('');
  const [newDash, setNewDash] = useState({ name: '', url: '', description: '' });

  useEffect(() => {
    if (user?.role === 'admin') {
      fetchDashboards();
    }
  }, [user]);

  const fetchDashboards = async () => {
    try {
      const res = await axios.get(`${API_URL}/dashboards/`);
      setDashboards(res.data);
      if (res.data.length > 0 && !activeUrl) {
        setActiveUrl(res.data[0].url);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleAddDashboard = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/dashboards/`, newDash);
      setNewDash({ name: '', url: '', description: '' });
      fetchDashboards();
    } catch (err) {
      console.error(err);
      alert("Error adding dashboard");
    }
  };

  const handleDeleteDashboard = async (id) => {
    if (window.confirm("Are you sure you want to remove this dashboard?")) {
      try {
        await axios.delete(`${API_URL}/dashboards/${id}`);
        fetchDashboards();
      } catch (err) {
        console.error(err);
        alert("Error deleting dashboard");
      }
    }
  };

  if (!user || user.role !== 'admin') {
    return (
      <div className="container">
        <div className="card" style={{ textAlign: 'center' }}>
          <h2>Access Denied</h2>
          <p>Please log in as an administrator to view the Analytics Hub.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="animate-slide-up" style={{ display: 'flex', gap: '20px', height: 'calc(100vh - 150px)', padding: '0 2rem 1rem 2rem' }}>
      
      {/* Sidebar for Dashboard Management */}
      <div style={{ width: '300px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div className="card" style={{ padding: '1rem' }}>
          <h3>Analytics Hub</h3>
          <p style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem' }}>Select a dashboard to view</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {dashboards.map(dash => (
              <div 
                key={dash.id} 
                className={`btn ${activeUrl === dash.url ? 'btn-primary' : 'btn-outline'}`}
                style={{ textAlign: 'left', display: 'flex', justifyContent: 'space-between', padding: '10px' }}
                onClick={() => setActiveUrl(dash.url)}
              >
                <span>{dash.name}</span>
                {dash.id !== 1 && ( // Don't allow deleting the default dashboard easily
                  <span 
                    style={{ color: activeUrl === dash.url ? 'white' : 'red', cursor: 'pointer', padding: '0 5px' }}
                    onClick={(e) => { e.stopPropagation(); handleDeleteDashboard(dash.id); }}
                  >
                    ×
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="card" style={{ padding: '1rem' }}>
          <h4>Add New Dashboard</h4>
          <form onSubmit={handleAddDashboard}>
            <div className="form-group">
              <input type="text" className="form-control" placeholder="Dashboard Name (e.g. Alice's Model)" value={newDash.name} onChange={e => setNewDash({...newDash, name: e.target.value})} required style={{ fontSize: '0.85rem' }}/>
            </div>
            <div className="form-group">
              <input type="url" className="form-control" placeholder="URL (e.g. http://localhost:8502)" value={newDash.url} onChange={e => setNewDash({...newDash, url: e.target.value})} required style={{ fontSize: '0.85rem' }}/>
            </div>
            <button type="submit" className="btn btn-secondary" style={{ width: '100%', padding: '8px', fontSize: '0.9rem' }}>+ Register URL</button>
          </form>
        </div>
      </div>

      {/* Main Iframe Viewer */}
      <div style={{ flex: 1, height: '100%' }}>
        {activeUrl ? (
          <iframe 
            src={activeUrl} 
            width="100%" 
            height="100%" 
            style={{ border: 'none', borderRadius: '8px', boxShadow: 'var(--shadow-lg)' }}
            title="Streamlit Analytics"
          />
        ) : (
          <div className="card" style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <p style={{ color: 'var(--color-text-muted)' }}>Select or add a dashboard from the menu.</p>
          </div>
        )}
      </div>

    </div>
  );
};

export default AnalyticsDashboard;
