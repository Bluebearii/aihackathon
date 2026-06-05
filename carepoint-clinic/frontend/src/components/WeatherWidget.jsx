import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Sun, Cloud, CloudRain, CloudLightning, CloudSnow, CloudFog, CloudDrizzle, Wind, Thermometer, Calendar } from 'lucide-react';
import { useAppContext } from '../context/AppContext';

const LOCATIONS = {
  'San Francisco': { lat: 37.7749, lon: -122.4194 },
  'Dallas': { lat: 32.7767, lon: -96.7970 },
  'New York': { lat: 40.7128, lon: -74.0060 }
};

const WeatherWidget = () => {
  const { API_URL } = useAppContext();
  const [location, setLocation] = useState('San Francisco');
  const [forecastType, setForecastType] = useState('Today'); // 'Today' or 'Week'
  const [weatherData, setWeatherData] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchWeatherAndPrediction();
  }, [location, forecastType]);

  const fetchWeatherAndPrediction = async () => {
    setLoading(true);
    try {
      const { lat, lon } = LOCATIONS[location];
      const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&daily=weathercode,temperature_2m_max,precipitation_sum,windspeed_10m_max&current_weather=true&timezone=auto`;
      
      const res = await axios.get(url);
      const data = res.data;
      
      let targetTemp, targetRain, targetCode, targetWind, isStorm;
      
      if (forecastType === 'Today') {
        targetTemp = data.current_weather.temperature;
        targetCode = data.current_weather.weathercode;
        targetWind = data.current_weather.windspeed;
        targetRain = data.daily.precipitation_sum[0] || 0;
        isStorm = [95, 96, 99].includes(targetCode) ? 1 : 0;
      } else {
        // Week: average over 7 days
        targetTemp = data.daily.temperature_2m_max.reduce((a, b) => a + b, 0) / 7;
        targetRain = data.daily.precipitation_sum.reduce((a, b) => a + b, 0) / 7;
        targetCode = data.daily.weathercode[3]; // pick middle of the week code
        targetWind = data.daily.windspeed_10m_max.reduce((a, b) => a + b, 0) / 7;
        isStorm = data.daily.weathercode.some(c => [95, 96, 99].includes(c)) ? 1 : 0;
      }
      
      setWeatherData({ temp: targetTemp, rain: targetRain, code: targetCode, wind: targetWind });
      
      // Fetch AI Prediction
      const predRes = await axios.get(`${API_URL}/predict-attendance?temp=${targetTemp}&rain=${targetRain}&storm=${isStorm}`);
      setPrediction(predRes.data.predicted_show_rate_pct);
      
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const getWeatherIcon = (code) => {
    if (code === 0) return <Sun size={32} color="#f59e0b" />;
    if (code <= 3) return <Cloud size={32} color="#94a3b8" />;
    if (code <= 48) return <CloudFog size={32} color="#64748b" />;
    if (code <= 55) return <CloudDrizzle size={32} color="#3b82f6" />;
    if (code <= 65 || code >= 80 && code <= 82) return <CloudRain size={32} color="#2563eb" />;
    if (code <= 77 || code === 85 || code === 86) return <CloudSnow size={32} color="#bae6fd" />;
    if (code >= 95) return <CloudLightning size={32} color="#eab308" />;
    return <Sun size={32} color="#f59e0b" />;
  };

  const getWeatherDesc = (code) => {
    if (code === 0) return "Clear Sky";
    if (code <= 3) return "Partly Cloudy";
    if (code <= 48) return "Foggy";
    if (code <= 55) return "Drizzle";
    if (code <= 65 || (code >= 80 && code <= 82)) return "Rainy";
    if (code <= 77 || code === 85 || code === 86) return "Snow";
    if (code >= 95) return "Thunderstorm";
    return "Clear";
  };

  return (
    <div className="card" style={{ marginBottom: '2rem', background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)', color: 'white', display: 'flex', gap: '20px', alignItems: 'stretch' }}>
      
      <div style={{ flex: 1 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
          <h3 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Calendar size={20} color="#38bdf8"/> AI Weather & Attendance Forecast
          </h3>
          <div style={{ display: 'flex', gap: '10px' }}>
            <select className="form-control" value={location} onChange={e => setLocation(e.target.value)} style={{ padding: '4px 8px', width: 'auto', background: '#334155', color: 'white', border: 'none' }}>
              <option value="San Francisco">San Francisco</option>
              <option value="Dallas">Dallas</option>
              <option value="New York">New York</option>
            </select>
            <select className="form-control" value={forecastType} onChange={e => setForecastType(e.target.value)} style={{ padding: '4px 8px', width: 'auto', background: '#334155', color: 'white', border: 'none' }}>
              <option value="Today">Today</option>
              <option value="Week">This Week</option>
            </select>
          </div>
        </div>

        {loading || !weatherData ? (
          <p>Analyzing satellite data and running XGBoost model...</p>
        ) : (
          <div style={{ display: 'flex', gap: '30px', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
              {getWeatherIcon(weatherData.code)}
              <div>
                <div style={{ fontSize: '1.8rem', fontWeight: 'bold' }}>{weatherData.temp.toFixed(1)}°C</div>
                <div style={{ color: '#94a3b8', fontSize: '0.9rem' }}>{getWeatherDesc(weatherData.code)}</div>
              </div>
            </div>
            <div style={{ borderLeft: '1px solid #334155', paddingLeft: '20px', display: 'flex', flexDirection: 'column', gap: '5px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#cbd5e1', fontSize: '0.9rem' }}><CloudRain size={16}/> {weatherData.rain.toFixed(1)} mm rain</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#cbd5e1', fontSize: '0.9rem' }}><Wind size={16}/> {weatherData.wind.toFixed(1)} km/h wind</div>
            </div>
          </div>
        )}
      </div>

      <div style={{ width: '250px', background: 'rgba(255,255,255,0.05)', borderRadius: '12px', padding: '15px', display: 'flex', flexDirection: 'column', justifyContent: 'center', borderLeft: '3px solid #10b981' }}>
        <div style={{ color: '#94a3b8', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '5px' }}>
          XGBoost Prediction
        </div>
        <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: prediction < 85 ? '#f43f5e' : '#10b981', lineHeight: '1' }}>
          {loading ? '...' : `${prediction}%`}
        </div>
        <div style={{ fontSize: '0.85rem', color: '#cbd5e1', marginTop: '8px' }}>
          Expected Show Rate
        </div>
      </div>
      
    </div>
  );
};

export default WeatherWidget;
