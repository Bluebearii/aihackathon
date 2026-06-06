import { useState, useEffect } from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, RadialBarChart, RadialBar, Legend
} from "recharts";

const FONT_LINK = "https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=Space+Mono:wght@400;700&display=swap";

const COLORS = {
  bg: "#0a0f1a",
  card: "#111827",
  cardHover: "#1a2236",
  border: "#1e293b",
  accent: "#06d6a0",
  accentDim: "#06d6a020",
  danger: "#ef4444",
  dangerDim: "#ef444420",
  warning: "#f59e0b",
  warningDim: "#f59e0b20",
  text: "#e2e8f0",
  textDim: "#94a3b8",
  white: "#ffffff",
};

const featureImportance = [
  { name: "Encounter Type", value: 0.2733, fill: COLORS.accent },
  { name: "Marital Status", value: 0.1688, fill: "#22d3ee" },
  { name: "Distance (km)", value: 0.1627, fill: "#818cf8" },
  { name: "Prior Visits", value: 0.1615, fill: "#a78bfa" },
  { name: "Age", value: 0.1175, fill: "#f472b6" },
  { name: "Day of Week", value: 0.0527, fill: "#fb923c" },
  { name: "Month", value: 0.036, fill: "#facc15" },
  { name: "Education", value: 0.0233, fill: "#4ade80" },
  { name: "Gender", value: 0.0041, fill: COLORS.textDim },
];

const modelMetrics = [
  { label: "AUC-ROC", value: "0.6104", color: COLORS.accent },
  { label: "Accuracy", value: "59%", color: "#818cf8" },
  { label: "No-Show Recall", value: "56%", color: "#f472b6" },
  { label: "Records", value: "64,956", color: "#22d3ee" },
];

const classReport = [
  { name: "Show", precision: 0.77, recall: 0.60, f1: 0.68 },
  { name: "No-Show", precision: 0.36, recall: 0.56, f1: 0.44 },
];

function predictNoShow({ age, gender, marital, education, distance, priorVisits, dayOfWeek, encounterType }) {
  let p = 0.2019;
  if (age < 18) p += 0.0234;
  else if (age < 30) p += 0.0452;
  else if (age < 60) p -= 0.0064;
  else p -= 0.0498;

  if (gender === "F") p += 0.0012;
  else if (gender === "M") p -= 0.0023;

  if (marital === "S") p += 0.05;
  else if (marital === "D") p += 0.04;
  else if (marital === "W") p += 0.02;
  else if (marital === "M") p -= 0.03;
  else p += 0.01;

  if (distance > 50) p += 0.12;
  else if (distance > 20) p += 0.07;
  else if (distance > 10) p += 0.03;

  if (education === "Low") p += 0.06;
  else if (education === "Medium") p += 0.02;
  else if (education === "High") p -= 0.04;

  if (priorVisits > 10) p -= 0.08;
  else if (priorVisits > 5) p -= 0.04;
  else if (priorVisits === 0) p += 0.06;

  if (dayOfWeek === "Monday") p += 0.04;
  else if (dayOfWeek === "Friday") p += 0.03;
  else if (dayOfWeek === "Wednesday") p -= 0.02;

  const enc = encounterType.toLowerCase();
  if (enc === "wellness") p += 0.05;
  else if (enc === "urgentcare") p -= 0.10;
  else if (enc === "emergency") p -= 0.15;

  return Math.min(Math.max(p, 0.01), 0.95);
}

function MetricCard({ label, value, color }) {
  return (
    <div style={{
      background: COLORS.card,
      border: `1px solid ${COLORS.border}`,
      borderRadius: 12,
      padding: "20px 24px",
      display: "flex",
      flexDirection: "column",
      gap: 4,
      transition: "all 0.2s",
    }}>
      <span style={{ fontFamily: "'Space Mono', monospace", fontSize: 11, color: COLORS.textDim, textTransform: "uppercase", letterSpacing: 1.5 }}>{label}</span>
      <span style={{ fontFamily: "'Space Mono', monospace", fontSize: 28, fontWeight: 700, color }}>{value}</span>
    </div>
  );
}

function SelectField({ label, value, onChange, options }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
      <label style={{ fontFamily: "'Space Mono', monospace", fontSize: 10, color: COLORS.textDim, textTransform: "uppercase", letterSpacing: 1.5 }}>{label}</label>
      <select
        value={value}
        onChange={e => onChange(e.target.value)}
        style={{
          background: COLORS.bg,
          border: `1px solid ${COLORS.border}`,
          borderRadius: 8,
          padding: "10px 12px",
          color: COLORS.text,
          fontFamily: "'DM Sans', sans-serif",
          fontSize: 14,
          outline: "none",
          cursor: "pointer",
          appearance: "none",
          WebkitAppearance: "none",
        }}
      >
        {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
    </div>
  );
}

function SliderField({ label, value, onChange, min, max, step = 1, unit = "" }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <label style={{ fontFamily: "'Space Mono', monospace", fontSize: 10, color: COLORS.textDim, textTransform: "uppercase", letterSpacing: 1.5 }}>{label}</label>
        <span style={{ fontFamily: "'Space Mono', monospace", fontSize: 13, color: COLORS.accent }}>{value}{unit}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={e => onChange(Number(e.target.value))}
        style={{
          width: "100%",
          accentColor: COLORS.accent,
          cursor: "pointer",
        }}
      />
    </div>
  );
}

function RiskGauge({ probability }) {
  const pct = Math.round(probability * 100);
  const riskLevel = pct < 20 ? "LOW" : pct < 40 ? "MODERATE" : pct < 60 ? "HIGH" : "CRITICAL";
  const riskColor = pct < 20 ? COLORS.accent : pct < 40 ? COLORS.warning : pct < 60 ? "#f97316" : COLORS.danger;

  const data = [{ name: "risk", value: pct, fill: riskColor }];

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8 }}>
      <div style={{ position: "relative", width: 200, height: 200 }}>
        <RadialBarChart
          width={200} height={200}
          cx={100} cy={100}
          innerRadius={65} outerRadius={90}
          barSize={18}
          data={data}
          startAngle={225} endAngle={-45}
        >
          <RadialBar dataKey="value" cornerRadius={10} max={100} background={{ fill: COLORS.border }} />
        </RadialBarChart>
        <div style={{
          position: "absolute", top: "50%", left: "50%", transform: "translate(-50%, -50%)",
          display: "flex", flexDirection: "column", alignItems: "center", gap: 2,
        }}>
          <span style={{ fontFamily: "'Space Mono', monospace", fontSize: 36, fontWeight: 700, color: riskColor }}>{pct}%</span>
        </div>
      </div>
      <div style={{
        padding: "6px 20px",
        borderRadius: 100,
        background: `${riskColor}18`,
        border: `1px solid ${riskColor}40`,
      }}>
        <span style={{ fontFamily: "'Space Mono', monospace", fontSize: 12, fontWeight: 700, color: riskColor, letterSpacing: 2 }}>{riskLevel} RISK</span>
      </div>
    </div>
  );
}

function CustomTooltip({ active, payload }) {
  if (active && payload?.length) {
    return (
      <div style={{
        background: COLORS.card,
        border: `1px solid ${COLORS.border}`,
        borderRadius: 8,
        padding: "10px 14px",
        fontFamily: "'DM Sans', sans-serif",
        fontSize: 13,
        color: COLORS.text,
      }}>
        <div style={{ fontWeight: 600 }}>{payload[0].payload.name}</div>
        <div style={{ color: COLORS.accent, fontFamily: "'Space Mono', monospace", marginTop: 4 }}>
          {(payload[0].value * 100).toFixed(2)}%
        </div>
      </div>
    );
  }
  return null;
}

export default function NoShowDashboard() {
  const [age, setAge] = useState(28);
  const [gender, setGender] = useState("M");
  const [marital, setMarital] = useState("S");
  const [education, setEducation] = useState("Low");
  const [distance, setDistance] = useState(15);
  const [priorVisits, setPriorVisits] = useState(2);
  const [dayOfWeek, setDayOfWeek] = useState("Monday");
  const [encounterType, setEncounterType] = useState("ambulatory");
  const [activeTab, setActiveTab] = useState("predictor");

  const probability = predictNoShow({ age, gender, marital, education, distance, priorVisits, dayOfWeek, encounterType });

  useEffect(() => {
    const link = document.createElement("link");
    link.href = FONT_LINK;
    link.rel = "stylesheet";
    document.head.appendChild(link);
    return () => document.head.removeChild(link);
  }, []);

  const tabs = [
    { id: "predictor", label: "Risk Predictor" },
    { id: "model", label: "Model Performance" },
    { id: "features", label: "Feature Analysis" },
  ];

  return (
    <div style={{
      background: COLORS.bg,
      minHeight: "100vh",
      color: COLORS.text,
      fontFamily: "'DM Sans', sans-serif",
      padding: 0,
    }}>
      {/* Header */}
      <div style={{
        borderBottom: `1px solid ${COLORS.border}`,
        padding: "28px 40px 0",
        background: `linear-gradient(180deg, #111827 0%, ${COLORS.bg} 100%)`,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 6 }}>
          <div style={{
            width: 40, height: 40, borderRadius: 10,
            background: `linear-gradient(135deg, ${COLORS.accent}, #22d3ee)`,
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 20,
          }}>🏥</div>
          <div>
            <h1 style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 22, fontWeight: 700, margin: 0, color: COLORS.white }}>
              Patient No-Show Predictor
            </h1>
            <p style={{ fontSize: 13, color: COLORS.textDim, margin: 0, marginTop: 2 }}>
              Gradient Boosted Model · Synthea + Kaggle Calibrated · Texas Region
            </p>
          </div>
        </div>

        {/* Tabs */}
        <div style={{ display: "flex", gap: 0, marginTop: 20 }}>
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                background: "none",
                border: "none",
                borderBottom: activeTab === tab.id ? `2px solid ${COLORS.accent}` : "2px solid transparent",
                padding: "10px 20px",
                color: activeTab === tab.id ? COLORS.accent : COLORS.textDim,
                fontFamily: "'DM Sans', sans-serif",
                fontSize: 14,
                fontWeight: activeTab === tab.id ? 600 : 400,
                cursor: "pointer",
                transition: "all 0.2s",
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div style={{ padding: "28px 40px" }}>

        {/* ─── PREDICTOR TAB ─── */}
        {activeTab === "predictor" && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 28 }}>
            {/* Input Panel */}
            <div style={{
              background: COLORS.card,
              border: `1px solid ${COLORS.border}`,
              borderRadius: 16,
              padding: 28,
            }}>
              <h2 style={{ fontSize: 16, fontWeight: 600, margin: "0 0 24px", color: COLORS.white }}>Patient Information</h2>
              <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
                <SliderField label="Age" value={age} onChange={setAge} min={0} max={100} unit=" yrs" />
                <SliderField label="Distance to Hospital" value={distance} onChange={setDistance} min={1} max={100} unit=" km" />
                <SliderField label="Prior Visits" value={priorVisits} onChange={setPriorVisits} min={0} max={30} />
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
                  <SelectField label="Gender" value={gender} onChange={setGender} options={[
                    { value: "M", label: "Male" }, { value: "F", label: "Female" }
                  ]} />
                  <SelectField label="Marital Status" value={marital} onChange={setMarital} options={[
                    { value: "S", label: "Single" }, { value: "M", label: "Married" },
                    { value: "D", label: "Divorced" }, { value: "W", label: "Widowed" },
                    { value: "U", label: "Unknown" },
                  ]} />
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
                  <SelectField label="Education / Income" value={education} onChange={setEducation} options={[
                    { value: "Low", label: "Low" }, { value: "Medium", label: "Medium" }, { value: "High", label: "High" },
                  ]} />
                  <SelectField label="Day of Week" value={dayOfWeek} onChange={setDayOfWeek} options={[
                    { value: "Monday", label: "Monday" }, { value: "Tuesday", label: "Tuesday" },
                    { value: "Wednesday", label: "Wednesday" }, { value: "Thursday", label: "Thursday" },
                    { value: "Friday", label: "Friday" },
                  ]} />
                </div>
                <SelectField label="Encounter Type" value={encounterType} onChange={setEncounterType} options={[
                  { value: "ambulatory", label: "Ambulatory" }, { value: "wellness", label: "Wellness" },
                  { value: "outpatient", label: "Outpatient" }, { value: "urgentcare", label: "Urgent Care" },
                  { value: "emergency", label: "Emergency" }, { value: "inpatient", label: "Inpatient" },
                ]} />
              </div>
            </div>

            {/* Result Panel */}
            <div style={{
              background: COLORS.card,
              border: `1px solid ${COLORS.border}`,
              borderRadius: 16,
              padding: 28,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              gap: 28,
            }}>
              <h2 style={{ fontSize: 16, fontWeight: 600, margin: 0, color: COLORS.white }}>No-Show Risk Assessment</h2>
              <RiskGauge probability={probability} />

              <div style={{
                width: "100%",
                background: COLORS.bg,
                borderRadius: 12,
                padding: 20,
                marginTop: 8,
              }}>
                <div style={{ fontFamily: "'Space Mono', monospace", fontSize: 10, color: COLORS.textDim, textTransform: "uppercase", letterSpacing: 1.5, marginBottom: 12 }}>
                  Risk Factors Contributing
                </div>
                {[
                  { label: "Age", impact: age < 18 ? "+2.3%" : age < 30 ? "+4.5%" : age < 60 ? "-0.6%" : "-5.0%", positive: age < 30 },
                  { label: "Distance", impact: distance > 50 ? "+12%" : distance > 20 ? "+7%" : distance > 10 ? "+3%" : "±0%", positive: distance > 10 },
                  { label: "Marital", impact: marital === "S" ? "+5%" : marital === "M" ? "-3%" : marital === "D" ? "+4%" : "+1%", positive: marital !== "M" },
                  { label: "Encounter", impact: encounterType === "wellness" ? "+5%" : encounterType === "urgentcare" ? "-10%" : encounterType === "emergency" ? "-15%" : "±0%", positive: encounterType === "wellness" },
                  { label: "Prior Visits", impact: priorVisits > 10 ? "-8%" : priorVisits > 5 ? "-4%" : priorVisits === 0 ? "+6%" : "±0%", positive: priorVisits < 3 },
                ].map((factor, i) => (
                  <div key={i} style={{
                    display: "flex", justifyContent: "space-between", alignItems: "center",
                    padding: "6px 0",
                    borderBottom: i < 4 ? `1px solid ${COLORS.border}` : "none",
                  }}>
                    <span style={{ fontSize: 13, color: COLORS.textDim }}>{factor.label}</span>
                    <span style={{
                      fontFamily: "'Space Mono', monospace",
                      fontSize: 12,
                      color: factor.positive ? COLORS.danger : COLORS.accent,
                      fontWeight: 600,
                    }}>{factor.impact}</span>
                  </div>
                ))}
              </div>

              <div style={{
                width: "100%",
                padding: "14px 18px",
                borderRadius: 10,
                background: probability > 0.4 ? COLORS.dangerDim : probability > 0.25 ? COLORS.warningDim : COLORS.accentDim,
                border: `1px solid ${probability > 0.4 ? COLORS.danger : probability > 0.25 ? COLORS.warning : COLORS.accent}30`,
              }}>
                <p style={{ fontSize: 13, color: COLORS.text, margin: 0, lineHeight: 1.5 }}>
                  <strong>Recommendation: </strong>
                  {probability > 0.4
                    ? "High risk — send SMS + phone reminder 48hrs and 24hrs before appointment."
                    : probability > 0.25
                    ? "Moderate risk — send automated SMS reminder 24hrs before appointment."
                    : "Low risk — standard email confirmation sufficient."
                  }
                </p>
              </div>
            </div>
          </div>
        )}

        {/* ─── MODEL PERFORMANCE TAB ─── */}
        {activeTab === "model" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16 }}>
              {modelMetrics.map(m => <MetricCard key={m.label} {...m} />)}
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
              {/* Classification Report */}
              <div style={{
                background: COLORS.card,
                border: `1px solid ${COLORS.border}`,
                borderRadius: 16,
                padding: 28,
              }}>
                <h3 style={{ fontSize: 16, fontWeight: 600, margin: "0 0 20px", color: COLORS.white }}>Classification Report</h3>
                <table style={{ width: "100%", borderCollapse: "collapse" }}>
                  <thead>
                    <tr>
                      {["Class", "Precision", "Recall", "F1-Score"].map(h => (
                        <th key={h} style={{
                          fontFamily: "'Space Mono', monospace", fontSize: 10, color: COLORS.textDim,
                          textTransform: "uppercase", letterSpacing: 1.5, textAlign: "left",
                          padding: "8px 12px", borderBottom: `1px solid ${COLORS.border}`,
                        }}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {classReport.map(row => (
                      <tr key={row.name}>
                        <td style={{ padding: "14px 12px", fontSize: 14, fontWeight: 600, color: COLORS.white }}>{row.name}</td>
                        {[row.precision, row.recall, row.f1].map((v, i) => (
                          <td key={i} style={{ padding: "14px 12px" }}>
                            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                              <div style={{ width: 60, height: 6, borderRadius: 3, background: COLORS.border, overflow: "hidden" }}>
                                <div style={{ width: `${v * 100}%`, height: "100%", borderRadius: 3, background: v > 0.6 ? COLORS.accent : v > 0.4 ? COLORS.warning : COLORS.danger }} />
                              </div>
                              <span style={{ fontFamily: "'Space Mono', monospace", fontSize: 13, color: COLORS.text }}>{v.toFixed(2)}</span>
                            </div>
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Data Distribution */}
              <div style={{
                background: COLORS.card,
                border: `1px solid ${COLORS.border}`,
                borderRadius: 16,
                padding: 28,
              }}>
                <h3 style={{ fontSize: 16, fontWeight: 600, margin: "0 0 20px", color: COLORS.white }}>Class Distribution</h3>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 200 }}>
                  <PieChart width={300} height={200}>
                    <Pie
                      data={[
                        { name: "Show (71.5%)", value: 71.54 },
                        { name: "No-Show (28.5%)", value: 28.46 },
                      ]}
                      cx={150} cy={100}
                      innerRadius={55} outerRadius={80}
                      paddingAngle={4}
                      dataKey="value"
                    >
                      <Cell fill={COLORS.accent} />
                      <Cell fill={COLORS.danger} />
                    </Pie>
                    <Tooltip
                      contentStyle={{ background: COLORS.card, border: `1px solid ${COLORS.border}`, borderRadius: 8, fontFamily: "'DM Sans', sans-serif", fontSize: 13 }}
                      itemStyle={{ color: COLORS.text }}
                    />
                    <Legend
                      verticalAlign="bottom"
                      iconType="circle"
                      formatter={(value) => <span style={{ color: COLORS.textDim, fontSize: 12, fontFamily: "'DM Sans', sans-serif" }}>{value}</span>}
                    />
                  </PieChart>
                </div>
              </div>
            </div>

            {/* Methodology */}
            <div style={{
              background: COLORS.card,
              border: `1px solid ${COLORS.border}`,
              borderRadius: 16,
              padding: 28,
            }}>
              <h3 style={{ fontSize: 16, fontWeight: 600, margin: "0 0 16px", color: COLORS.white }}>Methodology</h3>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 20 }}>
                {[
                  { title: "Data Generation", desc: "10,000 synthetic patients generated via Synthea for Texas region with realistic demographics and encounter histories." },
                  { title: "Label Calibration", desc: "No-show probabilities calibrated using 110,000 real Brazilian medical appointments (Kaggle), supplemented with healthcare literature." },
                  { title: "Model Training", desc: "Gradient Boosted Classifier with class-balanced sample weights, 200 estimators, learning rate 0.05, 80/20 train-test split." },
                ].map((item, i) => (
                  <div key={i} style={{ padding: 16, background: COLORS.bg, borderRadius: 10 }}>
                    <h4 style={{ fontSize: 13, fontWeight: 600, color: COLORS.accent, margin: "0 0 8px" }}>{item.title}</h4>
                    <p style={{ fontSize: 13, color: COLORS.textDim, margin: 0, lineHeight: 1.6 }}>{item.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ─── FEATURE ANALYSIS TAB ─── */}
        {activeTab === "features" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
            <div style={{
              background: COLORS.card,
              border: `1px solid ${COLORS.border}`,
              borderRadius: 16,
              padding: 28,
            }}>
              <h3 style={{ fontSize: 16, fontWeight: 600, margin: "0 0 24px", color: COLORS.white }}>Feature Importance (Gradient Boosted Model)</h3>
              <ResponsiveContainer width="100%" height={380}>
                <BarChart data={featureImportance} layout="vertical" margin={{ left: 20, right: 30 }}>
                  <XAxis type="number" domain={[0, 0.3]} tick={{ fill: COLORS.textDim, fontFamily: "'Space Mono', monospace", fontSize: 11 }} tickFormatter={v => `${(v * 100).toFixed(0)}%`} />
                  <YAxis type="category" dataKey="name" width={120} tick={{ fill: COLORS.text, fontFamily: "'DM Sans', sans-serif", fontSize: 13 }} />
                  <Tooltip content={<CustomTooltip />} cursor={{ fill: COLORS.border + "40" }} />
                  <Bar dataKey="value" radius={[0, 6, 6, 0]} barSize={24}>
                    {featureImportance.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Feature insights */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16 }}>
              {[
                {
                  title: "Encounter Type",
                  pct: "27.3%",
                  color: COLORS.accent,
                  insight: "The strongest predictor. Emergency & urgent care patients almost always show up. Wellness visit patients are most likely to skip.",
                },
                {
                  title: "Marital + Distance + Visits",
                  pct: "~16% each",
                  color: "#818cf8",
                  insight: "Mid-tier predictors forming a cluster. Single patients, those living far away, and first-time visitors are all higher risk.",
                },
                {
                  title: "Gender",
                  pct: "0.4%",
                  color: COLORS.textDim,
                  insight: "Nearly irrelevant — confirmed by both the Kaggle calibration data and our model. Gender should not drive clinical decisions.",
                },
              ].map((card, i) => (
                <div key={i} style={{
                  background: COLORS.card,
                  border: `1px solid ${COLORS.border}`,
                  borderRadius: 16,
                  padding: 24,
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                    <h4 style={{ fontSize: 14, fontWeight: 600, margin: 0, color: COLORS.white }}>{card.title}</h4>
                    <span style={{ fontFamily: "'Space Mono', monospace", fontSize: 14, fontWeight: 700, color: card.color }}>{card.pct}</span>
                  </div>
                  <p style={{ fontSize: 13, color: COLORS.textDim, margin: 0, lineHeight: 1.6 }}>{card.insight}</p>
                </div>
              ))}
            </div>

            {/* Calibration sources */}
            <div style={{
              background: COLORS.card,
              border: `1px solid ${COLORS.border}`,
              borderRadius: 16,
              padding: 24,
            }}>
              <h4 style={{ fontSize: 14, fontWeight: 600, margin: "0 0 12px", color: COLORS.white }}>Calibration Sources</h4>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                {[
                  { feat: "Age, Gender", src: "Kaggle Medical Appointments (110K records, Brazil)" , tag: "Empirical" },
                  { feat: "Base no-show rate (20.19%)", src: "Kaggle Medical Appointments dataset", tag: "Empirical" },
                  { feat: "Distance, Education", src: "Healthcare no-show literature (Dantas et al. 2018)", tag: "Literature" },
                  { feat: "Marital, Day of Week, Encounter Type", src: "Healthcare operations research estimates", tag: "Literature" },
                ].map((item, i) => (
                  <div key={i} style={{ display: "flex", gap: 10, padding: "10px 14px", background: COLORS.bg, borderRadius: 8, alignItems: "flex-start" }}>
                    <span style={{
                      fontFamily: "'Space Mono', monospace", fontSize: 9, padding: "3px 8px", borderRadius: 4,
                      background: item.tag === "Empirical" ? COLORS.accentDim : "#818cf820",
                      color: item.tag === "Empirical" ? COLORS.accent : "#818cf8",
                      fontWeight: 700, letterSpacing: 1, textTransform: "uppercase", whiteSpace: "nowrap", marginTop: 2,
                    }}>{item.tag}</span>
                    <div>
                      <div style={{ fontSize: 13, fontWeight: 600, color: COLORS.text }}>{item.feat}</div>
                      <div style={{ fontSize: 12, color: COLORS.textDim, marginTop: 2 }}>{item.src}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
