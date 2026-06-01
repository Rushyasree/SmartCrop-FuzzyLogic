import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { BeakerIcon, ChartBarIcon, HomeModernIcon, SparklesIcon, UserCircleIcon } from '@heroicons/react/24/outline';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Tooltip, Legend } from 'chart.js';
import { Bar, Line } from 'react-chartjs-2';
import './styles.css';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Tooltip, Legend);

const API_BASE = import.meta.env.VITE_API_URL || '/api';
const demoFarms = [
  { id: 1, name: 'North Field', district: 'Mandya', state: 'Karnataka', size_hectares: 2.5, soil_type: 'alluvial' },
  { id: 2, name: 'Canal Plot', district: 'Pune', state: 'Maharashtra', size_hectares: 1.8, soil_type: 'black' },
];
const demoSoil = [
  { id: 1, farm_id: 1, ph: 6.5, moisture: 58, nitrogen: 80, phosphorus: 42, potassium: 46, source: 'lab_test', created_at: '2026-05-25T08:00:00' },
  { id: 2, farm_id: 1, ph: 6.7, moisture: 62, nitrogen: 83, phosphorus: 41, potassium: 49, source: 'sensor', created_at: '2026-05-27T08:00:00' },
  { id: 3, farm_id: 2, ph: 7.4, moisture: 39, nitrogen: 62, phosphorus: 38, potassium: 60, source: 'farmer_input', created_at: '2026-05-29T08:00:00' },
];
const nav = [
  ['Dashboard', ChartBarIcon],
  ['Farms', HomeModernIcon],
  ['Soil History', BeakerIcon],
  ['Recommendations', SparklesIcon],
  ['Predictions', ChartBarIcon],
  ['Profile', UserCircleIcon],
];

async function api(path, options = {}, token = '') {
  const headers = { ...(options.headers || {}) };
  if (!(options.body instanceof FormData)) headers['Content-Type'] = headers['Content-Type'] || 'application/json';
  if (token) headers.Authorization = `Bearer ${token}`;
  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.message || 'Request failed');
  return payload;
}

function App() {
  const [active, setActive] = useState('Dashboard');
  const [token, setToken] = useState(localStorage.getItem('cropZenToken') || '');
  const [user, setUser] = useState(JSON.parse(localStorage.getItem('cropZenUser') || 'null'));
  const [farms, setFarms] = useState(demoFarms);
  const [soil, setSoil] = useState(demoSoil);
  const [predictions, setPredictions] = useState([]);
  const [notice, setNotice] = useState('Demo data loaded. Login to sync with the backend.');

  useEffect(() => {
    if (!token) return;
    Promise.all([api('/farms', {}, token), api('/soil-data', {}, token), api('/predictions', {}, token)])
      .then(([farmRes, soilRes, predRes]) => {
        setFarms(farmRes.data || []);
        setSoil(soilRes.data || []);
        setPredictions(predRes.data || []);
        setNotice('Synced with backend.');
      })
      .catch(() => setNotice('Backend sync failed. Demo data is still available.'));
  }, [token]);

  function onAuth(nextToken, nextUser) {
    localStorage.setItem('cropZenToken', nextToken);
    localStorage.setItem('cropZenUser', JSON.stringify(nextUser));
    setToken(nextToken);
    setUser(nextUser);
    setActive('Dashboard');
  }

  async function logout() {
    try {
      if (token) await api('/auth/logout', { method: 'POST', body: '{}' }, token);
    } catch {}
    localStorage.removeItem('cropZenToken');
    localStorage.removeItem('cropZenUser');
    setToken('');
    setUser(null);
    setNotice('Logged out locally.');
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><img src="/logo.png" alt="Crop Zen" /><div><strong>Crop Zen</strong><span>Farm intelligence</span></div></div>
        <nav>
          {nav.map(([label, Icon]) => (
            <button key={label} className={active === label ? 'active' : ''} onClick={() => setActive(label)}>
              <Icon aria-hidden="true" /><span>{label}</span>
            </button>
          ))}
        </nav>
        <button className="logout" onClick={logout}>{token ? 'Logout' : 'Demo mode'}</button>
      </aside>
      <main>
        <header className="topbar">
          <div><p>{token ? 'Connected workspace' : 'Offline workspace'}</p><h1>{active}</h1></div>
          <div className="user-pill"><UserCircleIcon aria-hidden="true" /><span>{user?.first_name || user?.email || 'Demo Farmer'}</span></div>
        </header>
        {notice && <div className="notice">{notice}</div>}
        {!token && <AuthPanel onAuth={onAuth} />}
        {active === 'Dashboard' && <Dashboard farms={farms} soil={soil} predictions={predictions} />}
        {active === 'Farms' && <Farms farms={farms} setFarms={setFarms} token={token} />}
        {active === 'Soil History' && <SoilHistory farms={farms} soil={soil} setSoil={setSoil} token={token} />}
        {active === 'Recommendations' && <Recommendations latest={soil[0] || demoSoil[0]} token={token} setPredictions={setPredictions} />}
        {active === 'Predictions' && <Predictions predictions={predictions} />}
        {active === 'Profile' && <Profile user={user} />}
      </main>
    </div>
  );
}

function AuthPanel({ onAuth }) {
  const [mode, setMode] = useState('login');
  const [form, setForm] = useState({ email: '', password: '', first_name: '', last_name: '' });
  const [message, setMessage] = useState('');
  async function submit(event) {
    event.preventDefault();
    try {
      const body = mode === 'login' ? { email: form.email, password: form.password } : form;
      const result = await api(mode === 'login' ? '/auth/login' : '/auth/register', { method: 'POST', body: JSON.stringify(body) });
      onAuth(result.data.access_token, result.data.user);
    } catch (error) {
      setMessage(error.message);
    }
  }
  return (
    <section className="auth-panel">
      <div><h2>Connect your farm account</h2><p>Sync farms, soil records, and recommendations through the Crop Zen API.</p></div>
      <form onSubmit={submit}>
        <div className="segmented"><button type="button" className={mode === 'login' ? 'selected' : ''} onClick={() => setMode('login')}>Login</button><button type="button" className={mode === 'register' ? 'selected' : ''} onClick={() => setMode('register')}>Register</button></div>
        <input type="email" placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
        <input type="password" placeholder="Password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
        {mode === 'register' && <div className="two-col"><input placeholder="First name" value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} /><input placeholder="Last name" value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} /></div>}
        <button className="primary" type="submit">{mode === 'login' ? 'Login' : 'Create account'}</button>
        {message && <small className="error">{message}</small>}
      </form>
    </section>
  );
}

function Dashboard({ farms, soil, predictions }) {
  const lineData = useMemo(() => ({
    labels: soil.map((item) => shortDate(item.created_at)),
    datasets: [
      { label: 'Soil pH', data: soil.map((item) => item.ph), borderColor: '#2563eb', backgroundColor: '#2563eb' },
      { label: 'Moisture', data: soil.map((item) => item.moisture), borderColor: '#059669', backgroundColor: '#059669' },
    ],
  }), [soil]);
  const stats = [['Farms', farms.length], ['Soil Records', soil.length], ['Avg pH', average(soil, 'ph')], ['Avg Moisture', `${average(soil, 'moisture')}%`]];
  return (
    <>
      <section className="stats-grid">{stats.map(([label, value]) => <article className="metric" key={label}><span>{label}</span><strong>{value}</strong><small>Current workspace</small></article>)}</section>
      <section className="dashboard-grid">
        <div className="panel chart-panel"><h2>Soil Trends</h2><Line data={lineData} options={{ responsive: true, maintainAspectRatio: false }} /></div>
        <div className="panel"><h2>Farm Overview</h2><div className="list">{farms.map((farm) => <FarmRow key={farm.id} farm={farm} />)}</div></div>
        <div className="panel wide"><h2>Recent Recommendations</h2><div className="list">{predictions.length ? predictions.slice(0, 4).map((item, index) => <Row key={index} title={item.crop_name || item.crop} detail={`${Math.round((item.confidence_score || item.confidence || 0) * 100)}% confidence`} />) : <p className="muted">Run a recommendation to populate history.</p>}</div></div>
      </section>
    </>
  );
}

function Farms({ farms, setFarms, token }) {
  const [form, setForm] = useState({ name: '', district: '', state: '', size_hectares: '', soil_type: '' });
  async function submit(event) {
    event.preventDefault();
    const optimistic = { ...form, id: Date.now(), size_hectares: Number(form.size_hectares || 0) };
    setFarms([optimistic, ...farms]);
    setForm({ name: '', district: '', state: '', size_hectares: '', soil_type: '' });
    if (token) {
      const result = await api('/farms', { method: 'POST', body: JSON.stringify(optimistic) }, token);
      setFarms((current) => current.map((farm) => farm.id === optimistic.id ? result.data : farm));
    }
  }
  return (
    <section className="split">
      <form className="panel form-panel" onSubmit={submit}>
        <h2>Add Farm</h2>
        <input placeholder="Farm name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
        <div className="two-col"><input placeholder="District" value={form.district} onChange={(e) => setForm({ ...form, district: e.target.value })} /><input placeholder="State" value={form.state} onChange={(e) => setForm({ ...form, state: e.target.value })} /></div>
        <div className="two-col"><input type="number" min="0" step="0.1" placeholder="Hectares" value={form.size_hectares} onChange={(e) => setForm({ ...form, size_hectares: e.target.value })} /><input placeholder="Soil type" value={form.soil_type} onChange={(e) => setForm({ ...form, soil_type: e.target.value })} /></div>
        <button className="primary" type="submit">Save farm</button>
      </form>
      <div className="panel"><h2>Managed Farms</h2><div className="list">{farms.map((farm) => <FarmRow key={farm.id} farm={farm} />)}</div></div>
    </section>
  );
}

function SoilHistory({ farms, soil, setSoil, token }) {
  const [form, setForm] = useState({ farm_id: farms[0]?.id || 1, ph: '', moisture: '', nitrogen: '', phosphorus: '', potassium: '', source: 'farmer_input' });
  const barData = { labels: soil.map((item) => shortDate(item.created_at)), datasets: [
    { label: 'Nitrogen', data: soil.map((item) => item.nitrogen || 0), backgroundColor: '#2563eb' },
    { label: 'Phosphorus', data: soil.map((item) => item.phosphorus || 0), backgroundColor: '#d97706' },
    { label: 'Potassium', data: soil.map((item) => item.potassium || 0), backgroundColor: '#059669' },
  ] };
  async function submit(event) {
    event.preventDefault();
    const payload = normalizeNumbers(form);
    const optimistic = { ...payload, id: Date.now(), created_at: new Date().toISOString() };
    setSoil([optimistic, ...soil]);
    if (token) {
      const result = await api('/soil-data', { method: 'POST', body: JSON.stringify(payload) }, token);
      setSoil((current) => current.map((item) => item.id === optimistic.id ? result.data : item));
    }
  }
  return (
    <section className="dashboard-grid">
      <form className="panel form-panel" onSubmit={submit}>
        <h2>Add Soil Record</h2>
        <select value={form.farm_id} onChange={(e) => setForm({ ...form, farm_id: Number(e.target.value) })}>{farms.map((farm) => <option value={farm.id} key={farm.id}>{farm.name}</option>)}</select>
        <div className="two-col"><input type="number" step="0.1" min="3" max="10" placeholder="pH" value={form.ph} onChange={(e) => setForm({ ...form, ph: e.target.value })} required /><input type="number" step="0.1" min="0" max="100" placeholder="Moisture" value={form.moisture} onChange={(e) => setForm({ ...form, moisture: e.target.value })} required /></div>
        <div className="three-col"><input type="number" placeholder="N" value={form.nitrogen} onChange={(e) => setForm({ ...form, nitrogen: e.target.value })} /><input type="number" placeholder="P" value={form.phosphorus} onChange={(e) => setForm({ ...form, phosphorus: e.target.value })} /><input type="number" placeholder="K" value={form.potassium} onChange={(e) => setForm({ ...form, potassium: e.target.value })} /></div>
        <button className="primary" type="submit">Record soil data</button>
      </form>
      <div className="panel chart-panel"><h2>NPK Trend</h2><Bar data={barData} options={{ responsive: true, maintainAspectRatio: false }} /></div>
      <div className="panel wide"><h2>Soil Records</h2><DataTable rows={soil} /></div>
    </section>
  );
}

function Recommendations({ latest, token, setPredictions }) {
  const [form, setForm] = useState({ soil_ph: latest.ph || 6.5, moisture: latest.moisture || 60, nitrogen: latest.nitrogen || 80, phosphorus: latest.phosphorus || 40, potassium: latest.potassium || 45, temperature: 28, humidity: 70, rainfall: 120 });
  const [result, setResult] = useState(null);
  async function submit(event) {
    event.preventDefault();
    const response = await api('/predict', { method: 'POST', body: JSON.stringify(normalizeNumbers(form)) }, token);
    setResult(response);
    setPredictions((current) => [...response.predictions.map((item) => ({ ...item, crop_name: item.crop, confidence_score: item.confidence })), ...current]);
  }
  return (
    <section className="split">
      <form className="panel form-panel" onSubmit={submit}>
        <h2>Recommendation Inputs</h2>
        <div className="two-col"><NumberInput label="pH" value={form.soil_ph} onChange={(value) => setForm({ ...form, soil_ph: value })} /><NumberInput label="Moisture" value={form.moisture} onChange={(value) => setForm({ ...form, moisture: value })} /></div>
        <div className="three-col"><NumberInput label="N" value={form.nitrogen} onChange={(value) => setForm({ ...form, nitrogen: value })} /><NumberInput label="P" value={form.phosphorus} onChange={(value) => setForm({ ...form, phosphorus: value })} /><NumberInput label="K" value={form.potassium} onChange={(value) => setForm({ ...form, potassium: value })} /></div>
        <div className="three-col"><NumberInput label="Temp" value={form.temperature} onChange={(value) => setForm({ ...form, temperature: value })} /><NumberInput label="Humidity" value={form.humidity} onChange={(value) => setForm({ ...form, humidity: value })} /><NumberInput label="Rainfall" value={form.rainfall} onChange={(value) => setForm({ ...form, rainfall: value })} /></div>
        <button className="primary" type="submit">Generate recommendation</button>
      </form>
      <div className="panel"><h2>Recommendation</h2>{result ? result.predictions.map((item) => <article className="recommendation" key={item.crop}><div><strong>{item.rank}. {item.crop}</strong><span>{Math.round(item.confidence * 100)}% confidence</span></div><ul>{item.reasons.map((reason) => <li key={reason}>{reason}</li>)}</ul></article>) : <p className="muted">Submit soil and weather data to get ranked crop options.</p>}</div>
    </section>
  );
}

function Predictions({ predictions }) {
  return <section className="panel"><h2>Prediction History</h2><div className="list">{predictions.length ? predictions.map((item, index) => <Row key={index} title={item.crop_name || item.crop} detail={`pH ${item.soil_ph || '-'} | moisture ${item.moisture || '-'} | ${Math.round((item.confidence_score || item.confidence || 0) * 100)}%`} />) : <p className="muted">No saved predictions yet.</p>}</div></section>;
}

function Profile({ user }) {
  return <section className="panel profile"><UserCircleIcon aria-hidden="true" /><div><h2>{user?.first_name ? `${user.first_name} ${user.last_name || ''}` : 'Demo Farmer'}</h2><p>{user?.email || 'Sign in to load your profile.'}</p><span>API: {API_BASE}</span></div></section>;
}

function FarmRow({ farm }) {
  return <Row title={farm.name} detail={`${farm.district || farm.location || 'Location pending'} | ${farm.size_hectares || 0} ha | ${farm.soil_type || 'soil n/a'}`} />;
}

function Row({ title, detail }) {
  return <div className="row"><strong>{title}</strong><span>{detail}</span></div>;
}

function DataTable({ rows }) {
  return <div className="table-wrap"><table><thead><tr><th>Date</th><th>Farm</th><th>pH</th><th>Moisture</th><th>N</th><th>P</th><th>K</th><th>Source</th></tr></thead><tbody>{rows.map((row) => <tr key={row.id}><td>{shortDate(row.created_at)}</td><td>{row.farm_id}</td><td>{row.ph}</td><td>{row.moisture}</td><td>{row.nitrogen || '-'}</td><td>{row.phosphorus || '-'}</td><td>{row.potassium || '-'}</td><td>{row.source || '-'}</td></tr>)}</tbody></table></div>;
}

function NumberInput({ label, value, onChange }) {
  return <input aria-label={label} type="number" step="0.1" placeholder={label} value={value} onChange={(event) => onChange(event.target.value)} />;
}

function normalizeNumbers(source) {
  return Object.fromEntries(Object.entries(source).map(([key, value]) => [key, value === '' ? undefined : Number(value) || value]));
}

function average(rows, key) {
  if (!rows.length) return 0;
  return Math.round((rows.reduce((sum, item) => sum + Number(item[key] || 0), 0) / rows.length) * 10) / 10;
}

function shortDate(value) {
  if (!value) return 'Today';
  return new Date(value).toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
}

createRoot(document.getElementById('root')).render(<App />);
