import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AppContext = createContext();

export const AppProvider = ({ children }) => {
  const [user, setUser] = useState(null); // Current logged in user
  const [appointments, setAppointments] = useState([]);
  const [points, setPoints] = useState([]);
  
  const API_URL = 'http://localhost:8000';

  useEffect(() => {
    // We start logged out, but if we had localStorage token we'd check it here
  }, []);

  const login = async (email, password) => {
    try {
      const res = await axios.post(`${API_URL}/auth/login`, { email, password });
      setUser(res.data);
      fetchAppointments(res.data.id);
      fetchPoints(res.data.id);
      return res.data;
    } catch (err) {
      console.error("Error logging in", err);
      return false;
    }
  };

  const signup = async (userData) => {
    try {
      const res = await axios.post(`${API_URL}/auth/signup`, userData);
      setUser(res.data);
      setAppointments([]);
      setPoints([]);
      return res.data;
    } catch (err) {
      console.error("Error signing up", err);
      return false;
    }
  };

  const logout = () => {
    setUser(null);
    setAppointments([]);
    setPoints([]);
  };

  const fetchAppointments = async (userId) => {
    try {
      const res = await axios.get(`${API_URL}/appointments/`);
      const userAppts = res.data.filter(a => a.patient_id === userId);
      setAppointments(userAppts);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchPoints = async (userId) => {
    try {
      const res = await axios.get(`${API_URL}/users/${userId}/points`);
      setPoints(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const bookAppointment = async (apptData) => {
    if (!user) return false;
    try {
      const res = await axios.post(`${API_URL}/appointments/`, {
        ...apptData,
        patient_id: user.id
      });
      setAppointments([...appointments, res.data]);
      return true;
    } catch (err) {
      console.error(err);
      return false;
    }
  };

  return (
    <AppContext.Provider value={{
      user,
      appointments,
      points,
      bookAppointment,
      login,
      signup,
      logout,
      API_URL,
      fetchAppointments,
      fetchPoints
    }}>
      {children}
    </AppContext.Provider>
  );
};

export const useAppContext = () => useContext(AppContext);
