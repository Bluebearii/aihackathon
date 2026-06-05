import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Sun, Cloud, CloudRain, CloudLightning, CloudSnow, CloudFog, CloudDrizzle, Wind, Thermometer, Calendar, ChevronDown, ChevronUp, Clock, Activity } from 'lucide-react';
import { useAppContext } from '../context/AppContext';

const LOCATIONS = {
  'San Francisco': { lat: 37.7749, lon: -122.4194 },
  'Dallas': { lat: 32.7767, lon: -96.7970 },
  'New York': { lat: 40.7128, lon: -74.0060 }
};

const toFahrenheit = (celsius) => Math.round((celsius * 9) / 5 + 32);

const WeatherWidget = () => {
  const { API_URL } = useAppContext();
  const [location, setLocation] = useState('San Francisco');
  const [forecastType, setForecastType] = useState('Week'); // 'Today', 'Week', 'Month'
  const [weatherData, setWeatherData] = useState(null);
  
  const [dailyForecast, setDailyForecast] = useState([]);
  const [hourlyForecast, setHourlyForecast] = useState([]);
  
  const [selectedDayIndex, setSelectedDayIndex] = useState(0);
  
  const [overallPrediction, setOverallPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    fetchWeatherAndPrediction();
  }, [location, forecastType]);

  const fetchWeatherAndPrediction = async () => {
    setLoading(true);
    try {
      const { lat, lon } = LOCATIONS[location];
      const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&hourly=temperature_2m,weathercode&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max&current_weather=true&timezone=auto&forecast_days=16`;
      
      const res = await axios.get(url);
      const data = res.data;
      
      let targetTempC, targetRain, targetCode, targetWind, isStorm;
      
      if (forecastType === 'Today') {
        targetTempC = data.current_weather.temperature;
        targetCode = data.current_weather.weathercode;
        targetWind = data.current_weather.windspeed;
        targetRain = data.daily.precipitation_sum[0] || 0;
        isStorm = [95, 96, 99].includes(targetCode) ? 1 : 0;
      } else if (forecastType === 'Week') {
        targetTempC = data.daily.temperature_2m_max.slice(0,7).reduce((a, b) => a + b, 0) / 7;
        targetRain = data.daily.precipitation_sum.slice(0,7).reduce((a, b) => a + b, 0) / 7;
        targetCode = data.daily.weathercode[3] || 0; 
        targetWind = data.daily.windspeed_10m_max.slice(0,7).reduce((a, b) => a + b, 0) / 7;
        isStorm = data.daily.weathercode.slice(0,7).some(c => [95, 96, 99].includes(c)) ? 1 : 0;
      } else {
        targetTempC = data.daily.temperature_2m_max.reduce((a, b) => a + b, 0) / 16;
        targetRain = data.daily.precipitation_sum.reduce((a, b) => a + b, 0) / 16;
        targetCode = data.daily.weathercode[7] || 0; 
        targetWind = data.daily.windspeed_10m_max.reduce((a, b) => a + b, 0) / 16;
        isStorm = data.daily.weathercode.some(c => [95, 96, 99].includes(c)) ? 1 : 0;
      }
      
      setWeatherData({ tempC: targetTempC, rain: targetRain, code: targetCode, wind: targetWind });
      
      // Fetch predictions for all 16 days in parallel
      const daysArray = await Promise.all(data.daily.time.map(async (timeStr, index) => {
        const d = new Date(timeStr + "T12:00:00Z");
        const days = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT'];
        
        const dayTemp = data.daily.temperature_2m_max[index];
        const dayRain = data.daily.precipitation_sum[index];
        const dayCode = data.daily.weathercode[index];
        const dayStorm = [95, 96, 99].includes(dayCode) ? 1 : 0;
        
        let pred = null;
        try {
            const pRes = await axios.get(`${API_URL}/predict-attendance?temp=${dayTemp}&rain=${dayRain}&storm=${dayStorm}`);
            pred = pRes.data.predicted_show_rate_pct;
        } catch(e) {}

        return {
          dayName: days[d.getDay()],
          dateLabel: `${d.getMonth()+1}/${d.getDate()}`,
          maxC: dayTemp,
          minC: data.daily.temperature_2m_min[index],
          code: dayCode,
          wind: data.daily.windspeed_10m_max[index],
          rain: dayRain,
          prediction: pred
        };
      }));
      setDailyForecast(daysArray);

      // 24-hour setup
      const currentHourStr = data.current_weather.time; 
      let startIndex = data.hourly.time.findIndex(t => t === currentHourStr);
      if (startIndex === -1) startIndex = 0;
      
      const hoursArray = [];
      for (let i = 0; i < 24; i++) {
        const idx = startIndex + i;
        if (idx >= data.hourly.time.length) break;
        let hourLabel = parseInt(data.hourly.time[idx].split('T')[1].split(':')[0]);
        let ampm = hourLabel >= 12 ? 'PM' : 'AM';
        hourLabel = hourLabel % 12 || 12;

        hoursArray.push({
          timeLabel: `${hourLabel} ${ampm}`,
          tempC: data.hourly.temperature_2m[idx],
          code: data.hourly.weathercode[idx]
        });
      }
      setHourlyForecast(hoursArray);
      
      const predRes = await axios.get(`${API_URL}/predict-attendance?temp=${targetTempC}&rain=${targetRain}&storm=${isStorm}`);
      setOverallPrediction(predRes.data.predicted_show_rate_pct);
      setSelectedDayIndex(0); // reset selection
      
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const getWeatherIcon = (code, size=32) => {
    if (code === 0) return <Sun size={size} color="#f59e0b" />;
    if (code <= 3) return <Cloud size={size} color="#94a3b8" />;
    if (code <= 48) return <CloudFog size={size} color="#64748b" />;
    if (code <= 55) return <CloudDrizzle size={size} color="#3b82f6" />;
    if (code <= 65 || (code >= 80 && code <= 82)) return <CloudRain size={size} color="#2563eb" />;
    if (code <= 77 || code === 85 || code === 86) return <CloudSnow size={size} color="#bae6fd" />;
    if (code >= 95) return <CloudLightning size={size} color="#eab308" />;
    return <Sun size={size} color="#f59e0b" />;
  };

  const getWeatherDesc = (code) => {
    if (code === 0) return "Clear Sky";
    if (code <= 3) return "Partly Cloudy";
    if (code <= 48) return "Foggy";
    if (code <= 55) return "Drizzle";
    if (code <= 65 || (code >= 80 && code <= 82)) return "Rainy";
    if (code <= 77 || code === 85 || code === 86) return "Snow";
    if (code >= 95) return "Thunderstorms";
    return "Clear";
  };

  if (!weatherData) return null;

  const daysToShow = forecastType === 'Week' ? dailyForecast.slice(0, 7) : dailyForecast.slice(0, 16);
  
  // Calculate what to show in the big right-hand prediction box
  let displayPrediction = overallPrediction;
  let displayContext = `Overall patient show-rate based on ${forecastType.toLowerCase()} weather.`;
  let displayNoShow = 100 - overallPrediction;
  
  if (forecastType !== 'Today' && dailyForecast[selectedDayIndex]) {
     displayPrediction = dailyForecast[selectedDayIndex].prediction;
     displayNoShow = 100 - displayPrediction;
     displayContext = `Predicted for ${dailyForecast[selectedDayIndex].dayName}, ${dailyForecast[selectedDayIndex].dateLabel} specifically.`;
  }

  const currentTempF = toFahrenheit(weatherData.tempC);

  return (
    <div className="card" style={{ marginBottom: '2rem', padding: 0, overflow: 'hidden', border: '1px solid #e2e8f0', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)' }}>
      {/* Sleek Top Tab */}
      <div 
        onClick={() => setIsExpanded(!isExpanded)}
        style={{
          background: '#ffffff',
          padding: '16px 24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          cursor: 'pointer',
          borderBottom: isExpanded ? '1px solid #f1f5f9' : 'none'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ background: '#f8fafc', padding: '8px', borderRadius: '12px' }}>
            {getWeatherIcon(weatherData.code, 28)}
          </div>
          <div>
            <div style={{ fontWeight: '700', fontSize: '1.25rem', color: '#0f172a' }}>
              {currentTempF}°F <span style={{ fontWeight: '400', color: '#64748b', fontSize: '1rem', marginLeft: '6px' }}>{getWeatherDesc(weatherData.code)} in {location}</span>
            </div>
            <div style={{ fontSize: '0.85rem', color: '#94a3b8', marginTop: '2px' }}>Click to adjust forecast settings</div>
          </div>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
            <span style={{ fontSize: '0.8rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: '600' }}>Expected Show Rate</span>
            <strong style={{ color: overallPrediction < 85 ? '#ef4444' : '#0d9488', fontSize: '1.3rem', lineHeight: '1.2' }}>
              {loading || overallPrediction === null ? '...' : `${overallPrediction}%`}
            </strong>
          </div>
          <div style={{ background: '#f1f5f9', padding: '6px', borderRadius: '50%' }}>
            {isExpanded ? <ChevronUp size={20} color="#64748b" /> : <ChevronDown size={20} color="#64748b" />}
          </div>
        </div>
      </div>

      {/* Expanded Detail Panel */}
      {isExpanded && (
        <div style={{
          background: '#f8fafc',
          padding: '24px',
          animation: 'slideDown 0.3s ease-out forwards',
          transformOrigin: 'top',
          borderTop: '1px solid #e2e8f0'
        }}>
          
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
            <div style={{ display: 'flex', gap: '12px' }}>
              <select className="form-control" value={location} onChange={e => setLocation(e.target.value)} style={{ padding: '8px 12px', width: 'auto', fontWeight: '500', color: '#0f172a', border: '1px solid #cbd5e1', boxShadow: '0 1px 2px rgba(0,0,0,0.05)' }}>
                <option value="San Francisco">San Francisco, CA</option>
                <option value="Dallas">Dallas, TX</option>
                <option value="New York">New York, NY</option>
              </select>
              <select className="form-control" value={forecastType} onChange={e => setForecastType(e.target.value)} style={{ padding: '8px 12px', width: 'auto', fontWeight: '500', color: '#0f172a', border: '1px solid #cbd5e1', boxShadow: '0 1px 2px rgba(0,0,0,0.05)' }}>
                <option value="Today">24-Hour Forecast</option>
                <option value="Week">7-Day Forecast</option>
                <option value="Month">Extended Outlook (16 Days)</option>
              </select>
            </div>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', color: '#64748b', fontSize: '0.9rem' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><CloudRain size={16}/> {forecastType !== 'Today' && dailyForecast[selectedDayIndex] ? dailyForecast[selectedDayIndex].rain.toFixed(1) : weatherData.rain.toFixed(1)} mm</span>
              <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><Wind size={16}/> {forecastType !== 'Today' && dailyForecast[selectedDayIndex] ? dailyForecast[selectedDayIndex].wind.toFixed(1) : weatherData.wind.toFixed(1)} km/h</span>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '20px', alignItems: 'stretch' }}>
            {/* Left side: Weather Display */}
            <div style={{ flex: 1, background: 'white', padding: '20px', borderRadius: '8px', border: '1px solid #e2e8f0', overflow: 'hidden' }}>
              
              {/* Horizontal Scrollable Forecast Area */}
              <div style={{ 
                display: 'flex', 
                overflowX: 'auto', 
                paddingBottom: '8px',
                gap: '12px',
                scrollbarWidth: 'thin',
                scrollbarColor: '#cbd5e1 transparent'
              }}>
                {forecastType === 'Today' ? (
                  // 24-Hour View
                  hourlyForecast.map((hour, idx) => (
                    <div key={idx} style={{ 
                      flex: '0 0 auto',
                      display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'space-between',
                      background: idx === 0 ? '#0f766e' : 'white',
                      color: idx === 0 ? 'white' : '#334155',
                      padding: '16px 12px', borderRadius: '12px', minWidth: '80px',
                      border: idx === 0 ? 'none' : '1px solid #e2e8f0',
                      boxShadow: idx === 0 ? '0 4px 12px rgba(15, 118, 110, 0.2)' : '0 1px 3px rgba(0,0,0,0.02)'
                    }}>
                      <div style={{ fontSize: '0.85rem', fontWeight: '600', marginBottom: '12px' }}>{hour.timeLabel}</div>
                      <div style={{ marginBottom: '12px' }}>{getWeatherIcon(hour.code, 28)}</div>
                      <div style={{ fontSize: '1.25rem', fontWeight: '700' }}>{toFahrenheit(hour.tempC)}°</div>
                    </div>
                  ))
                ) : (
                  // 7-Day or 16-Day View (Clickable)
                  daysToShow.map((day, idx) => {
                    const isSelected = selectedDayIndex === idx;
                    return (
                      <div 
                        key={idx} 
                        onClick={() => setSelectedDayIndex(idx)}
                        style={{ 
                        flex: '0 0 auto',
                        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'space-between',
                        background: isSelected ? '#0f766e' : 'white',
                        color: isSelected ? 'white' : '#334155',
                        padding: '16px 12px', borderRadius: '12px', minWidth: '90px',
                        border: isSelected ? 'none' : '1px solid #e2e8f0',
                        boxShadow: isSelected ? '0 4px 12px rgba(15, 118, 110, 0.3)' : '0 1px 3px rgba(0,0,0,0.02)',
                        cursor: 'pointer',
                        transition: 'all 0.2s ease',
                        transform: isSelected ? 'scale(1.02)' : 'scale(1)'
                      }}>
                        <div style={{ fontSize: '0.9rem', fontWeight: '700', letterSpacing: '0.5px' }}>{day.dayName}</div>
                        <div style={{ fontSize: '0.75rem', color: isSelected ? 'rgba(255,255,255,0.7)' : '#94a3b8', marginBottom: '12px' }}>{day.dateLabel}</div>
                        <div style={{ marginBottom: '12px' }}>{getWeatherIcon(day.code, 32)}</div>
                        <div style={{ fontSize: '1.25rem', fontWeight: '700' }}>{toFahrenheit(day.maxC)}°</div>
                        <div style={{ fontSize: '0.9rem', color: isSelected ? 'rgba(255,255,255,0.7)' : '#64748b' }}>{toFahrenheit(day.minC)}°</div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>

            {/* Right side: ML Prediction Box */}
            <div style={{ 
              width: '280px', 
              background: 'white', 
              borderRadius: '8px', 
              border: '1px solid #e2e8f0',
              padding: '20px', 
              display: 'flex', 
              flexDirection: 'column', 
              justifyContent: 'center', 
              borderLeft: `5px solid ${displayPrediction < 85 ? '#ef4444' : '#0d9488'}` 
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#64748b', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '8px', fontWeight: '600' }}>
                <Activity size={16} color={displayPrediction < 85 ? '#ef4444' : '#0d9488'} />
                {displayPrediction < 85 ? 'High Risk Alert' : 'Normal Operations'}
              </div>
              <div style={{ fontSize: '3rem', fontWeight: 'bold', color: displayPrediction < 85 ? '#ef4444' : '#0d9488', lineHeight: '1' }}>
                {loading || displayPrediction === null ? '...' : `${displayPrediction.toFixed(1)}%`}
              </div>
              <div style={{ fontSize: '0.95rem', fontWeight: '600', color: '#334155', marginTop: '10px' }}>
                Expected Show Rate
              </div>
              
              <div style={{ fontSize: '0.85rem', color: '#64748b', marginTop: '6px', lineHeight: '1.4' }}>
                {displayContext}
              </div>
              
              <div style={{ marginTop: '15px', background: '#f1f5f9', padding: '10px', borderRadius: '6px', fontSize: '0.85rem', color: '#475569' }}>
                <strong>{displayNoShow?.toFixed(1)}% No-Show Risk:</strong> The model expects {Math.round(displayNoShow)} out of every 100 scheduled patients to miss their appointment.
              </div>
            </div>
            
          </div>
        </div>
      )}
    </div>
  );
};

export default WeatherWidget;
