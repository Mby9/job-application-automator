import React, { useState, useEffect, useCallback, useRef } from 'react';
import api from '../api/api';
import { useAuth } from '../context/AuthContext';
import { Plus, ToggleRight, ToggleLeft, Settings, X, Loader2, Check, Upload, Globe, Building2, Star, Trash2, Zap, ExternalLink, Briefcase, MapPin, Calendar, DollarSign, Ban, ChevronRight, Search, AlertCircle, Rocket } from 'lucide-react';

// ── Helpers ──────────────────────────────────────────────────────────────────

const s = (light, dark, isDark) => isDark ? dark : light;

// ── ATS Badge ────────────────────────────────────────────────────────────────
const ATS_CFG = {
  greenhouse: { bg: 'rgba(16,185,129,0.1)',  color: '#059669', label: 'Greenhouse' },
  lever:      { bg: 'rgba(245,158,11,0.1)',  color: '#d97706', label: 'Lever' },
  ashby:      { bg: 'rgba(139,92,246,0.1)',  color: '#7c3aed', label: 'Ashby' },
  workday:    { bg: 'rgba(239,68,68,0.1)',   color: '#dc2626', label: 'Workday' },
};
function AtsBadge({ type }) {
  const c = ATS_CFG[type] || { bg: 'rgba(100,116,139,0.1)', color: '#64748b', label: type };
  return (
    <span style={{ background: c.bg, color: c.color, padding: '2px 8px', borderRadius: 6, fontSize: '0.7rem', fontWeight: 700 }}>
      {c.label}
    </span>
  );
}

// ── Status Badge ─────────────────────────────────────────────────────────────
function StatusBadge({ status }) {
  if (status === 'applied') return (
    <span style={{ background: 'rgba(16,185,129,0.12)', color: '#059669', padding: '2px 10px', borderRadius: 99, fontSize: '0.72rem', fontWeight: 700 }}>
      ✓ Applied
    </span>
  );
  return null;
}

// ── Chip Input ───────────────────────────────────────────────────────────────
function ChipInput({ label, values, onChange, placeholder, isDark }) {
  const [input, setInput] = useState('');
  const add = () => {
    const v = input.trim();
    if (v && !values.includes(v)) onChange([...values, v]);
    setInput('');
  };
  const border = `1px solid var(--border)`;
  return (
    <div style={{ marginBottom: 20 }}>
      <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', display: 'block', marginBottom: 8 }}>
        {label}
      </label>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 8 }}>
        {values.map(v => (
          <span key={v} style={{ background: 'rgba(59,130,246,0.1)', border: '1px solid rgba(59,130,246,0.2)', color: 'var(--accent-blue)', borderRadius: 99, padding: '3px 10px', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: 5 }}>
            {v}
            <button onClick={() => onChange(values.filter(x => x !== v))} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit', lineHeight: 1 }}>×</button>
          </span>
        ))}
      </div>
      <div style={{ display: 'flex', gap: 8 }}>
        <input 
          value={input} 
          onChange={e => setInput(e.target.value)} 
          onKeyDown={e => e.key === 'Enter' && add()} 
          placeholder={placeholder}
          list={label === "Preferred Locations" ? "location-suggestions" : undefined}
          style={{ flex: 1, background: 'var(--surface)', border, borderRadius: 8, padding: '8px 12px', color: 'var(--text-primary)', fontSize: '0.875rem', outline: 'none' }} 
        />
        {label === "Preferred Locations" && (
          <datalist id="location-suggestions">
            <option value="Toronto, ON" />
            <option value="Vancouver, BC" />
            <option value="Montreal, QC" />
            <option value="Ottawa, ON" />
            <option value="Calgary, AB" />
            <option value="Remote" />
            <option value="USA" />
            <option value="New York, NY" />
            <option value="San Francisco, CA" />
            <option value="Austin, TX" />
            <option value="London, UK" />
            <option value="Berlin, Germany" />
          </datalist>
        )}
        <button onClick={add} style={{ background: 'var(--accent-blue)', border: 'none', borderRadius: 8, padding: '8px 14px', cursor: 'pointer', color: '#fff' }}>
          <Plus size={15} />
        </button>
      </div>
    </div>
  );
}

// ── Toggle Row ────────────────────────────────────────────────────────────────
function ToggleRow({ label, desc, value, onChange }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 10, padding: '12px 16px', marginBottom: 16 }}>
      <div>
        <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-primary)' }}>{label}</div>
        {desc && <div style={{ color: 'var(--text-secondary)', fontSize: '0.78rem', marginTop: 2 }}>{desc}</div>}
      </div>
      <button onClick={() => onChange(!value)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: value ? 'var(--accent-blue)' : 'var(--text-muted)', padding: 4 }}>
        {value ? <ToggleRight size={30} /> : <ToggleLeft size={30} />}
      </button>
    </div>
  );
}

// ── Settings Drawer ───────────────────────────────────────────────────────────
function SettingsDrawer({ open, onClose, isDark }) {
  const [prefs, setPrefs] = useState({ 
    preferred_locations: [], 
    preferred_keywords: [], 
    remote_only: false, 
    dark_mode: false, 
    seniority_level: 'Any', 
    legal_work_country: 'Any',
    resume_text: '' 
  });
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [uploadingResume, setUploadingResume] = useState(false);
  const [showPaste, setShowPaste] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const resumeFileRef = useRef(null);

  useEffect(() => {
    if (!open) return;
    api.get('/api/preferences').then(r => setPrefs(p => ({ ...p, ...r.data }))).catch(() => {});
    api.get('/api/profile/resume').then(r => setPrefs(p => ({ ...p, resume_text: r.data.resume_text }))).catch(() => {});
  }, [open]);

  const handleResumeUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadingResume(true);
    const fd = new FormData();
    fd.append('file', file);
    try {
      const { data } = await api.post('/api/utils/parse-resume', fd);
      setPrefs(p => ({ ...p, resume_text: data.text }));
      setUploadSuccess(true);
      setShowPaste(false);
    } catch (err) {
      alert("Failed to parse resume: " + (err.response?.data?.detail || err.message));
    }
    setUploadingResume(false);
    if (resumeFileRef.current) resumeFileRef.current.value = '';
  };

  const save = async () => {
    setSaving(true);
    try {
      await api.put('/api/preferences', prefs);
      await api.put('/api/profile/resume', { resume_text: prefs.resume_text || '' });
      // Apply dark mode immediately
      document.documentElement.setAttribute('data-theme', prefs.dark_mode ? 'dark' : '');
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch {}
    setSaving(false);
  };

  if (!open) return null;
  return (
    <>
      <div onClick={onClose} style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.25)', backdropFilter: 'blur(3px)', zIndex: 100 }} />
      <div style={{ position: 'fixed', top: 0, right: 0, bottom: 0, width: 420, background: 'var(--surface-raised)', borderLeft: '1px solid var(--border)', zIndex: 101, display: 'flex', flexDirection: 'column', boxShadow: 'var(--shadow-drawer)', animation: 'slideIn 0.2s ease' }}>
        <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <Settings size={18} color="var(--accent-blue)" />
            <span style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--text-primary)' }}>Preferences</span>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-secondary)', padding: 4 }}><X size={18} /></button>
        </div>

        <div style={{ flex: 1, overflowY: 'auto', padding: 24 }}>
          <ChipInput label="Preferred Locations" values={prefs.preferred_locations} onChange={v => setPrefs(p => ({ ...p, preferred_locations: v }))} placeholder="e.g. Toronto, Remote" isDark={isDark} />
          <ChipInput label="Job Title Keywords" values={prefs.preferred_keywords} onChange={v => setPrefs(p => ({ ...p, preferred_keywords: v }))} placeholder="e.g. AI Engineer, Python" isDark={isDark} />
          
          <div style={{ marginBottom: 20 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', display: 'block' }}>
                Resume
              </label>
              
              <div style={{ display: 'flex', gap: 8 }}>
                <button onClick={() => setShowPaste(!showPaste)} style={{ background: 'transparent', border: '1px dashed var(--border)', borderRadius: 6, padding: '4px 10px', color: 'var(--text-secondary)', fontSize: '0.75rem', fontWeight: 600, cursor: 'pointer' }}>
                  {showPaste ? 'Hide Text' : 'Paste Text Instead'}
                </button>
                <input type="file" accept=".pdf,.doc,.docx,.txt" ref={resumeFileRef} style={{ display: 'none' }} onChange={handleResumeUpload} />
                <button onClick={() => resumeFileRef.current?.click()} disabled={uploadingResume} style={{ background: 'var(--accent-blue)', color: '#fff', border: 'none', borderRadius: 6, padding: '4px 10px', fontSize: '0.75rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 6, cursor: uploadingResume ? 'wait' : 'pointer' }}>
                  {uploadingResume ? <Loader2 size={12} style={{ animation: 'spin 1s linear infinite' }} /> : <Upload size={12} />}
                  Upload File
                </button>
              </div>
            </div>
            
            {uploadSuccess && !showPaste && (
              <div style={{ fontSize: '0.8rem', color: 'var(--accent-green)', padding: '8px 12px', background: 'rgba(34, 197, 94, 0.1)', borderRadius: 6, border: '1px solid rgba(34, 197, 94, 0.2)' }}>
                Resume file parsed and loaded! Click Save to apply.
              </div>
            )}
            
            {(!uploadSuccess && !showPaste && prefs.resume_text) && (
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', padding: '8px 12px', background: 'var(--bg)', borderRadius: 6, border: '1px dashed var(--border)' }}>
                Resume is currently saved ({prefs.resume_text.length} characters). Upload a new file or paste text to update.
              </div>
            )}

            {showPaste && (
              <textarea 
                value={prefs.resume_text} 
                onChange={e => {
                  setPrefs(p => ({ ...p, resume_text: e.target.value }));
                  setUploadSuccess(false);
                }}
                placeholder="Paste your resume text here (used for AI matching)..."
                style={{ width: '100%', height: 120, padding: '10px 12px', borderRadius: 8, border: '1px solid var(--border)', background: 'var(--surface)', color: 'var(--text-primary)', fontSize: '0.85rem', outline: 'none', resize: 'vertical' }}
              />
            )}
          </div>
          
          <div style={{ marginBottom: 20 }}>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', display: 'block', marginBottom: 8 }}>
              Seniority Target
            </label>
            <select 
              value={prefs.seniority_level || 'Any'} 
              onChange={e => setPrefs(p => ({ ...p, seniority_level: e.target.value }))}
              style={{ width: '100%', padding: '10px 12px', borderRadius: 8, border: '1px solid var(--border)', background: 'var(--surface)', color: 'var(--text-primary)', fontSize: '0.9rem', outline: 'none' }}
            >
              <option value="Any">Any</option>
              <option value="Junior">Junior / Internship</option>
              <option value="Mid">Mid-Level</option>
              <option value="Senior">Senior / Principal / Lead</option>
            </select>
          </div>

          <ToggleRow label="Remote Only" desc="Filter out non-remote positions" value={prefs.remote_only} onChange={v => setPrefs(p => ({ ...p, remote_only: v }))} />
          <div style={{ marginBottom: 20 }}>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', display: 'block', marginBottom: 8 }}>
              Work Authorization Country
            </label>
            <select 
              value={prefs.legal_work_country || 'Any'} 
              onChange={e => setPrefs(p => ({ ...p, legal_work_country: e.target.value }))}
              style={{ width: '100%', padding: '10px 12px', borderRadius: 8, border: '1px solid var(--border)', background: 'var(--surface)', color: 'var(--text-primary)', fontSize: '0.9rem', outline: 'none' }}
            >
              <option value="Any">Any (Global)</option>
              <option value="Canada">Canada 🇨🇦</option>
              <option value="USA">United States 🇺🇸</option>
              <option value="UK">United Kingdom 🇬🇧</option>
              <option value="India">India 🇮🇳</option>
              <option value="Germany">Germany 🇩🇪</option>
            </select>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 6 }}>
              Filters out remote jobs restricted to other countries (e.g. Remote-USA jobs won't show if set to Canada).
            </p>
          </div>
          <ToggleRow label="Dark Mode" desc="Switch to a dark interface" value={prefs.dark_mode} onChange={v => setPrefs(p => ({ ...p, dark_mode: v }))} />
        </div>

        <div style={{ padding: '16px 24px', borderTop: '1px solid var(--border)' }}>
          <button onClick={save} disabled={saving} style={{ width: '100%', padding: '11px', background: saved ? 'var(--accent-green)' : 'var(--accent-blue)', border: 'none', borderRadius: 10, color: '#fff', fontWeight: 700, cursor: 'pointer', fontSize: '0.9rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, transition: 'background 0.2s' }}>
            {saving ? <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} /> : <Check size={16} />}
            {saving ? 'Saving…' : saved ? 'Saved!' : 'Save Preferences'}
          </button>
        </div>
      </div>
    </>
  );
}

// ── Companies View ────────────────────────────────────────────────────────────
function CompaniesView() {
  const [companies, setCompanies] = useState([]);
  const [tab, setTab] = useState('approved');
  const [search, setSearch] = useState('');
  const [discovering, setDiscovering] = useState(false);
  const [discoverMsg, setDiscoverMsg] = useState('');
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);

  const load = useCallback(async () => {
    const r = await api.get('/api/companies');
    setCompanies(r.data);
  }, []);

  useEffect(() => { load(); }, [load]);

  const checkDiscoveryStatus = async () => {
    try {
      const { data } = await api.get('/api/companies/discover/status');
      return data.is_discovering;
    } catch {
      return false;
    }
  };

  const runDiscovery = async () => {
    setDiscovering(true); setDiscoverMsg('Starting discovery in background...');
    try {
      await api.post('/api/companies/discover');
      
      const pollInterval = setInterval(async () => {
        const isRunning = await checkDiscoveryStatus();
        if (!isRunning) {
          clearInterval(pollInterval);
          const r = await api.get('/api/companies');
          const newCompanies = r.data;
          setCompanies(newCompanies);
          setDiscovering(false);
          
          // UI Polish: If currently on approved and it's empty but suggested has items, switch to suggested
          if (tab === 'approved') {
            const hasApproved = newCompanies.some(c => c.status === 'approved');
            const hasSuggested = newCompanies.some(c => c.status === 'suggested');
            if (!hasApproved && hasSuggested) {
              setTab('suggested');
            }
          }
          
          setDiscoverMsg('Discovery complete. UI updated.');
          setTimeout(() => setDiscoverMsg(''), 5000);
        } else {
          setDiscoverMsg('Searching across the web... This may take up to 20 seconds.');
        }
      }, 2000);
    } catch { 
      setDiscoverMsg('Discovery failed to start'); 
      setDiscovering(false);
    }
  };

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    setUploading(true);
    setDiscoverMsg('');
    const fd = new FormData();
    fd.append('file', file);

    try {
      const r = await api.post('/api/companies/upload', fd);
      setDiscoverMsg(`Uploaded ${r.data.added} companies (skipped ${r.data.skipped_due_to_duplicate} duplicates)`);
      // Reload the companies list
      load();
    } catch (err) {
      setDiscoverMsg(err.response?.data?.detail || 'Upload failed');
    }
    setUploading(false);
    if (fileInputRef.current) fileInputRef.current.value = ''; // reset
  };

  const updateStatus = async (id, status) => {
    await api.put(`/api/companies/${id}`, { status });
    setCompanies(prev => prev.map(c => c.id === id ? { ...c, status } : c));
  };
  const togglePriority = async (id, cur) => {
    await api.put(`/api/companies/${id}`, { is_priority: !cur });
    setCompanies(prev => prev.map(c => c.id === id ? { ...c, is_priority: !cur } : c));
  };
  const remove = async (id) => {
    await api.delete(`/api/companies/${id}`);
    setCompanies(prev => prev.filter(c => c.id !== id));
  };

  const tabs = ['approved', 'suggested', 'rejected'];
  const filtered = companies
    .filter(c => c.status === tab)
    .filter(c => !search || c.name.toLowerCase().includes(search.toLowerCase()));

  return (
    <div>
      {/* Top bar */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20, flexWrap: 'wrap' }}>
        <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search companies…"
          style={{ flex: '1 1 240px', background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 8, padding: '9px 14px', color: 'var(--text-primary)', fontSize: '0.875rem', outline: 'none', boxShadow: 'var(--shadow-sm)' }} />
        
        <input type="file" accept=".csv" ref={fileInputRef} style={{ display: 'none' }} onChange={handleUpload} />
        <button onClick={() => fileInputRef.current?.click()} disabled={uploading || discovering} style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 8, padding: '9px 18px', color: 'var(--text-primary)', fontWeight: 600, cursor: (uploading || discovering) ? 'wait' : 'pointer', display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.875rem', whiteSpace: 'nowrap', boxShadow: 'var(--shadow-sm)' }}>
          {uploading ? <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} /> : <Upload size={16} />}
          Upload CSV
        </button>
        
        <button onClick={runDiscovery} disabled={uploading || discovering} style={{ background: 'var(--accent-blue)', border: 'none', borderRadius: 8, padding: '9px 18px', color: '#fff', fontWeight: 600, cursor: (uploading || discovering) ? 'wait' : 'pointer', display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.875rem', whiteSpace: 'nowrap', boxShadow: 'var(--shadow-sm)' }}>
          {discovering ? <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} /> : <Globe size={16} />}
          {discovering ? 'Searching…' : 'Run Discovery'}
        </button>
      </div>
      {discoverMsg && <p style={{ color: 'var(--accent-blue)', marginBottom: 12, fontSize: '0.85rem', fontWeight: 500 }}>{discoverMsg}</p>}

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 4, marginBottom: 16, background: 'var(--surface)', padding: 4, borderRadius: 10, border: '1px solid var(--border)', width: 'fit-content', boxShadow: 'var(--shadow-sm)' }}>
        {tabs.map(t => (
          <button key={t} onClick={() => setTab(t)} style={{ padding: '6px 16px', borderRadius: 8, border: 'none', cursor: 'pointer', fontSize: '0.85rem', fontWeight: 600, textTransform: 'capitalize', background: tab === t ? 'var(--accent-blue)' : 'transparent', color: tab === t ? '#fff' : 'var(--text-secondary)', transition: 'all 0.15s' }}>
            {t} ({companies.filter(c => c.status === t).length})
          </button>
        ))}
      </div>

      {/* Companies table */}
      {filtered.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-secondary)' }}>
          <Building2 size={36} style={{ marginBottom: 12, opacity: 0.3 }} />
          <p>{tab === 'suggested' ? 'Run Discovery to find companies' : `No ${tab} companies`}</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 16, alignItems: 'stretch' }}>
          {filtered.map(c => (
            <div key={c.id} style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 12, padding: '16px', display: 'flex', flexDirection: 'column', gap: 12, boxShadow: 'var(--shadow-sm)', transition: 'box-shadow 0.2s', height: '100%' }}
                 onMouseOver={e => { e.currentTarget.style.boxShadow = 'var(--shadow-md)'; }}
                 onMouseOut={e => { e.currentTarget.style.boxShadow = 'var(--shadow-sm)'; }}>
              
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
                <div style={{ width: 48, height: 48, background: 'var(--bg)', borderRadius: '12px', border: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden', flexShrink: 0 }}>
                  {c.logo_url ? (
                    <img src={c.logo_url} alt={c.name} style={{ width: '100%', height: '100%', objectFit: 'contain', padding: c.logo_url.includes('google.com/s2/favicons') ? 8 : 0 }} onError={(e) => { e.currentTarget.style.display = 'none'; e.currentTarget.nextSibling.style.display = 'flex'; }} />
                  ) : null}
                  <Building2 size={24} color="var(--accent-blue)" style={{ display: c.logo_url ? 'none' : 'flex' }} />
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                    <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{c.name}</span>
                    {c.is_priority && <Star size={14} fill="var(--accent-gold)" color="var(--accent-gold)" style={{ flexShrink: 0 }} />}
                  </div>
                  <div style={{ marginTop: 6 }}><AtsBadge type={c.ats_type} /></div>
                </div>
              </div>

              <div style={{ display: 'flex', gap: 8, marginTop: 'auto', paddingTop: 16, borderTop: '1px solid var(--border)', justifyContent: 'flex-end' }}>
                {tab === 'suggested' && (
                  <>
                    <button onClick={() => updateStatus(c.id, 'approved')} title="Approve" style={{ display: 'flex', alignItems: 'center', gap: 6, background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.2)', borderRadius: 8, padding: '6px 12px', cursor: 'pointer', color: 'var(--accent-green)', fontWeight: 600, fontSize: '0.8rem', flex: 1, justifyContent: 'center' }}>
                      <Check size={14} /> Approve
                    </button>
                    <button onClick={() => updateStatus(c.id, 'rejected')} title="Reject" style={{ display: 'flex', alignItems: 'center', gap: 6, background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.15)', borderRadius: 8, padding: '6px 12px', cursor: 'pointer', color: 'var(--accent-red)', fontWeight: 600, fontSize: '0.8rem', flex: 1, justifyContent: 'center' }}>
                      <X size={14} /> Reject
                    </button>
                  </>
                )}
                {tab === 'rejected' && (
                  <button onClick={() => updateStatus(c.id, 'approved')} title="Restore" style={{ display: 'flex', alignItems: 'center', gap: 6, background: 'rgba(59,130,246,0.1)', border: '1px solid rgba(59,130,246,0.2)', borderRadius: 8, padding: '6px 12px', cursor: 'pointer', color: 'var(--accent-blue)', fontWeight: 600, fontSize: '0.8rem', flex: 1, justifyContent: 'center' }}>
                    <Check size={14} /> Restore
                  </button>
                )}
                {tab === 'approved' && (
                  <button onClick={() => togglePriority(c.id, c.is_priority)} title={c.is_priority ? "Remove priority" : "Mark as priority"} style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 6, justifyContent: 'center', background: c.is_priority ? 'rgba(245,158,11,0.12)' : 'var(--surface)', border: `1px solid ${c.is_priority ? 'rgba(245,158,11,0.3)' : 'var(--border)'}`, borderRadius: 8, padding: '6px 12px', cursor: 'pointer', fontWeight: 600, fontSize: '0.8rem', color: c.is_priority ? 'var(--accent-gold)' : 'var(--text-secondary)' }}>
                    <Star size={14} fill={c.is_priority ? 'currentColor' : 'none'} /> {c.is_priority ? 'Priority' : 'Prioritize'}
                  </button>
                )}
                <button onClick={() => remove(c.id)} title="Delete" style={{ background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: 8, cursor: 'pointer', color: 'var(--text-muted)', padding: '6px 10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Trash2 size={15} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Job Card ──────────────────────────────────────────────────────────────────
function JobCard({ job, onSkip, onApply }) {
  const [loading, setLoading] = useState(null);

  const handleSkip = async () => {
    setLoading('skip');
    await onSkip(job.id);
  };
  const handleApply = async () => {
    setLoading('apply');
    await onApply(job.id);
  };

  return (
    <div style={{
      background: 'var(--surface)', border: `1px solid ${job.is_priority ? 'rgba(245,158,11,0.3)' : 'var(--border)'}`,
      borderRadius: 16, padding: 22, display: 'flex', flexDirection: 'column', gap: 14,
      height: '100%',  // fill grid cell so all cards in a row are equal height
      boxShadow: job.is_priority ? '0 0 0 1px rgba(245,158,11,0.1), var(--shadow-md)' : 'var(--shadow-sm)',
      transition: 'transform 0.2s, box-shadow 0.2s', animation: 'fadeIn 0.3s ease', cursor: 'pointer'
    }}
    onMouseOver={e => { e.currentTarget.style.transform = 'translateY(-3px)'; e.currentTarget.style.boxShadow = 'var(--shadow-lg)'; }}
    onMouseOut={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = job.is_priority ? '0 0 0 1px rgba(245,158,11,0.1), var(--shadow-md)' : 'var(--shadow-sm)'; }}>

      {/* Top row: badges */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 8 }}>
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
          {job.is_priority && (
            <span style={{ background: 'rgba(245,158,11,0.1)', color: 'var(--accent-gold)', borderRadius: 99, padding: '3px 10px', fontSize: '0.72rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 4 }}>
              <Star size={10} fill="currentColor" /> Priority
            </span>
          )}
          <span style={{ background: 'rgba(59,130,246,0.1)', color: 'var(--accent-blue)', borderRadius: 99, padding: '3px 10px', fontSize: '0.72rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 4 }}>
            <Zap size={10} fill="currentColor" /> {job.match_score ?? '—'}%
          </span>
          {job.ats_source && <AtsBadge type={job.ats_source} />}
          <StatusBadge status={job.status} />
        </div>
        <button onClick={e => { e.stopPropagation(); window.open(job.url, '_blank'); }} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', padding: 2, flexShrink: 0 }}>
          <ExternalLink size={15} />
        </button>
      </div>

      {/* Title & Company */}
      <div onClick={() => window.open(job.url, '_blank')}>
        <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: 4, color: 'var(--text-primary)', lineHeight: 1.3 }}>{job.title}</h3>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--text-secondary)', fontSize: '0.85rem', flexWrap: 'wrap' }}>
          <Briefcase size={13} /><span>{job.company}</span>
          {job.location && <><span style={{ opacity: 0.4 }}>·</span><MapPin size={13} /><span>{job.location}</span></>}
          {job.posted_at && <><span style={{ opacity: 0.4 }}>·</span><Calendar size={13} /><span>{new Date(job.posted_at).toLocaleDateString()}</span></>}
          {job.salary_range && <><span style={{ opacity: 0.4 }}>·</span><DollarSign size={13} /><span>{job.salary_range}</span></>}
        </div>
      </div>

      {/* Description snippet */}
      <p style={{ color: 'var(--text-secondary)', fontSize: '0.84rem', lineHeight: 1.65, display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden', flex: 1 }}>
        {job.description || 'Click to view full job description →'}
      </p>

      {/* Actions */}
      <div style={{ display: 'flex', gap: 8, marginTop: 'auto', paddingTop: 12, borderTop: '1px solid var(--border)' }}>
        <button onClick={handleSkip} disabled={loading === 'skip'} style={{ flex: 1, padding: '8px', background: 'rgba(239,68,68,0.07)', border: '1px solid rgba(239,68,68,0.15)', borderRadius: 8, cursor: 'pointer', color: 'var(--accent-red)', fontWeight: 600, fontSize: '0.8rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, transition: 'background 0.15s' }}
          onMouseOver={e => e.currentTarget.style.background = 'rgba(239,68,68,0.13)'}
          onMouseOut={e => e.currentTarget.style.background = 'rgba(239,68,68,0.07)'}>
          {loading === 'skip' ? <Loader2 size={13} style={{ animation: 'spin 1s linear infinite' }} /> : <Ban size={13} />} Skip
        </button>
        <button onClick={handleApply} disabled={loading === 'apply' || job.status === 'applied'} style={{ flex: 2, padding: '8px', background: job.status === 'applied' ? 'rgba(16,185,129,0.1)' : 'var(--accent-blue)', border: job.status === 'applied' ? '1px solid rgba(16,185,129,0.3)' : 'none', borderRadius: 8, cursor: job.status === 'applied' ? 'default' : 'pointer', color: job.status === 'applied' ? 'var(--accent-green)' : '#fff', fontWeight: 600, fontSize: '0.8rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, transition: 'opacity 0.15s' }}>
          {loading === 'apply' ? <Loader2 size={13} style={{ animation: 'spin 1s linear infinite' }} /> : <Check size={13} />}
          {job.status === 'applied' ? 'Applied' : 'Mark Applied'}
        </button>
        <button onClick={e => { e.stopPropagation(); window.open(job.url, '_blank'); }} style={{ padding: '8px 12px', background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 8, cursor: 'pointer', color: 'var(--text-secondary)', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: 5 }}>
          View <ChevronRight size={13} />
        </button>
      </div>
    </div>
  );
}

// ── Jobs View ─────────────────────────────────────────────────────────────────
function JobsView() {
  const [jobs, setJobs] = useState([]);
  const [initialLoading, setInitialLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState(null);
  const [scanResult, setScanResult] = useState(null);
  const [filter, setFilter] = useState('new'); // 'all' | 'new' | 'applied'
  const [stats, setStats] = useState({ new: 0, applied: 0, all: 0 });
  const [skip, setSkip] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const LIMIT = 20;

  const fetchStats = async () => {
    try {
      const r = await api.get('/api/jobs/stats');
      setStats(r.data);
    } catch {}
  };

  const loadJobs = useCallback(async (reset = false, currentFilter = filter) => {
    if (reset) {
      setInitialLoading(true);
      setSkip(0);
    } else {
      setLoadingMore(true);
    }
    const offset = reset ? 0 : skip;
    try {
      const r = await api.get('/api/jobs', {
        params: { status: currentFilter, skip: offset, limit: LIMIT }
      });
      if (reset) {
        setJobs(r.data);
      } else {
        setJobs(prev => [...prev, ...r.data]);
      }
      setHasMore(r.data.length >= LIMIT);
      setSkip(offset + LIMIT);
      fetchStats();
    } catch {
      setError('Could not load jobs.');
    } finally {
      setInitialLoading(false);
      setLoadingMore(false);
    }
  }, [filter, skip]);

  // Reload when filter tab changes
  useEffect(() => {
    loadJobs(true, filter);
  }, [filter]);

  const checkScanStatus = async () => {
    try {
      const { data } = await api.get('/api/jobs/scan/status');
      return data;
    } catch {
      return { is_scanning: false, progress: '' };
    }
  };

  // Scan for new jobs (triggers scraping pipeline)
  const scanJobs = async () => {
    setScanning(true); setError(null); setScanResult('Starting job scan...');
    try {
      await api.post('/api/jobs/scan');
      
      const pollInterval = setInterval(async () => {
        const status = await checkScanStatus();
        if (!status.is_scanning) {
          clearInterval(pollInterval);
          await loadJobs(true, filter);
          setScanning(false);
          setScanResult(`Scan complete: ${status.discovered_count || 0} new job${status.discovered_count === 1 ? '' : 's'} found.`);
          setTimeout(() => setScanResult(null), 5000);
        } else {
          setScanResult(status.progress || 'Scanning...');
        }
      }, 2000);
    } catch {
      setError('Scan failed. Is the backend running?');
      setScanning(false);
      setScanResult(null);
    }
  };

  const skipJob = async (id) => {
    await api.put(`/api/jobs/${id}/status`, { status: 'hidden' });
    setJobs(prev => prev.filter(j => j.id !== id));
    fetchStats();
  };

  const applyJob = async (id) => {
    await api.put(`/api/jobs/${id}/status`, { status: 'applied' });
    setJobs(prev => prev.map(j => j.id === id ? { ...j, status: 'applied' } : j));
    fetchStats();
  };

  // jobs array is already filtered by backend
  const visibleJobs = jobs;

  return (
    <>
      {/* Controls row */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20, flexWrap: 'wrap' }}>
        {/* Filter pills */}
        <div style={{ display: 'flex', gap: 4, background: 'var(--surface)', padding: 4, borderRadius: 10, border: '1px solid var(--border)', boxShadow: 'var(--shadow-sm)', height: 40 }}>
          {[['new', `New (${stats.new})`], ['applied', `Applied (${stats.applied})`], ['all', `All (${stats.all})`]].map(([val, label]) => (
            <button key={val} onClick={() => setFilter(val)} style={{ padding: '0 14px', height: 32, borderRadius: 8, border: 'none', cursor: 'pointer', fontSize: '0.82rem', fontWeight: 600, background: filter === val ? 'var(--accent-blue)' : 'transparent', color: filter === val ? '#fff' : 'var(--text-secondary)', transition: 'all 0.15s' }}>
              {label}
            </button>
          ))}
        </div>

        <div style={{ flex: 1 }} />

        <button onClick={scanJobs} disabled={scanning} style={{ background: 'var(--accent-blue)', color: '#fff', padding: '0 20px', height: 40, borderRadius: 10, border: 'none', fontWeight: 600, cursor: scanning ? 'wait' : 'pointer', display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.875rem', boxShadow: '0 2px 8px rgba(59,130,246,0.25)', transition: 'transform 0.15s, opacity 0.15s', opacity: scanning ? 0.8 : 1 }}
          onMouseOver={e => { if (!scanning) e.currentTarget.style.transform = 'translateY(-1px)'; }}
          onMouseOut={e => { e.currentTarget.style.transform = 'translateY(0)'; }}>
          {scanning ? <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} /> : <Search size={16} />}
          {scanning ? 'Scanning for new jobs…' : 'Scan for New Jobs'}
        </button>
      </div>
      

      {error && (
        <div style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)', padding: '14px 18px', borderRadius: 12, display: 'flex', alignItems: 'center', gap: 12, color: 'var(--accent-red)', marginBottom: 20 }}>
          <AlertCircle size={18} /><span style={{ fontSize: '0.875rem' }}>{error}</span>
        </div>
      )}
      
      {scanResult && (
        <div style={{ position: 'fixed', bottom: 30, left: '50%', transform: 'translateX(-50%)', background: 'var(--surface)', border: '1px solid var(--border)', padding: '12px 24px', borderRadius: 99, display: 'flex', alignItems: 'center', gap: 10, color: 'var(--text-primary)', boxShadow: 'var(--shadow-lg)', zIndex: 100, animation: 'fadeInUp 0.3s ease' }}>
          <Check size={18} color="var(--accent-green)" />
          <span style={{ fontSize: '0.9rem', fontWeight: 500 }}>{scanResult}</span>
          <button onClick={() => setScanResult(null)} style={{ background: 'transparent', border: 'none', cursor: 'pointer', display: 'flex', color: 'var(--text-muted)', marginLeft: 8 }}><X size={16} /></button>
        </div>
      )}

      {initialLoading ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: 24, alignItems: 'start' }}>
          {[1,2,3,4,5,6].map(i => <div key={i} style={{ height: 260, background: 'var(--surface)', borderRadius: 16, border: '1px solid var(--border)', animation: 'pulse 1.5s infinite' }} />)}
        </div>
      ) : visibleJobs.length > 0 ? (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: 24, alignItems: 'stretch' }}>
            {visibleJobs.map((job, i) => <JobCard key={job.id ?? i} job={job} onSkip={skipJob} onApply={applyJob} />)}
          </div>
          
          {hasMore && (
            <div style={{ display: 'flex', justifyContent: 'center', marginTop: 40, marginBottom: 20 }}>
              <button onClick={() => loadJobs(false)} disabled={loadingMore} style={{ background: 'var(--surface)', border: '1px solid var(--border)', color: 'var(--text-primary)', padding: '12px 32px', borderRadius: 99, fontWeight: 600, cursor: loadingMore ? 'wait' : 'pointer', display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.9rem', boxShadow: 'var(--shadow-sm)', transition: 'all 0.15s' }}>
                {loadingMore && <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} />}
                {loadingMore ? 'Loading...' : 'Load More Jobs'}
              </button>
            </div>
          )}
        </>
      ) : (
        <div style={{ textAlign: 'center', padding: '80px 20px', background: 'var(--surface)', borderRadius: 20, border: '1px dashed var(--border)' }}>
          <Rocket size={44} color="var(--text-muted)" style={{ marginBottom: 16, opacity: 0.5 }} />
          <h2 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: 8, color: 'var(--text-primary)' }}>
            {filter === 'applied' ? 'No applied jobs yet' : stats[filter] === 0 ? 'No saved jobs yet' : 'All caught up!'}
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: 24 }}>
            {filter === 'applied'
              ? 'Jobs you mark as applied will appear here.'
              : 'Click Scan for New Jobs to discover job postings from your approved companies.'}
          </p>
          {stats[filter] === 0 && (
            <button onClick={scanJobs} disabled={scanning} style={{ background: 'var(--accent-blue)', color: '#fff', padding: '11px 28px', borderRadius: 10, border: 'none', fontWeight: 600, cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: 8, fontSize: '0.9rem', boxShadow: '0 2px 8px rgba(59,130,246,0.25)' }}>
              {scanning ? <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} /> : <Search size={16} />}
              {scanning ? 'Scanning…' : 'Scan for New Jobs'}
            </button>
          )}
        </div>
      )}
    </>
  );
}

// ── Mappings View ─────────────────────────────────────────────────────────────
function MappingsView() {
  const [mappings, setMappings] = useState([]);
  const [tab, setTab] = useState('pending'); // 'pending' | 'active'
  const [newLabel, setNewLabel] = useState('');
  const [newValue, setNewValue] = useState('');

  const loadMappings = useCallback(async () => {
    try {
      const { data } = await api.get('/api/mappings');
      setMappings(data);
    } catch (e) { console.error(e); }
  }, []);

  useEffect(() => { loadMappings(); }, [loadMappings]);

  const updateStatus = async (id, status) => {
    try {
      await api.put(`/api/mappings/${id}/status`, { status });
      loadMappings();
    } catch (e) { console.error(e); }
  };

  const deleteMapping = async (id) => {
    try {
      await api.delete(`/api/mappings/${id}`);
      loadMappings();
    } catch (e) { console.error(e); }
  };

  const handleAdd = async (e) => {
    e.preventDefault();
    if (!newLabel.trim() || !newValue.trim()) return;
    try {
      await api.post('/api/mappings', {
        label_text: newLabel,
        field_value: newValue,
        status: 'active'
      });
      setNewLabel('');
      setNewValue('');
      setTab('active');
      loadMappings();
    } catch (e) { console.error(e); }
  };

  const filtered = mappings.filter(m => m.status === tab);
  const counts = {
    pending: mappings.filter(m => m.status === 'pending').length,
    active: mappings.filter(m => m.status === 'active').length,
  };

  return (
    <div style={{ animation: 'fadeIn 0.4s ease-out' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
            <Zap size={24} color="var(--accent-blue)" /> Autofill Rules
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>Review unverified form fields caught by the extension or insert your own semantic rules.</p>
        </div>
      </div>

      <div style={{ display: 'flex', gap: 8, marginBottom: 24 }}>
        {['pending', 'active'].map(t => (
          <button
            key={t}
            onClick={() => setTab(t)}
            style={{
              padding: '8px 16px', borderRadius: 999, border: '1px solid',
              background: tab === t ? 'var(--accent-blue)' : 'transparent',
              color: tab === t ? '#fff' : 'var(--text-secondary)',
              borderColor: tab === t ? 'var(--accent-blue)' : 'var(--border)',
              fontWeight: 600, fontSize: '0.85rem', cursor: 'pointer', transition: 'all 0.15s'
            }}
          >
            {t.charAt(0).toUpperCase() + t.slice(1)} <span style={{ opacity: 0.7, marginLeft: 6 }}>{counts[t]}</span>
          </button>
        ))}
      </div>

      {tab === 'active' && (
        <form onSubmit={handleAdd} style={{ background: 'var(--surface)', padding: 16, borderRadius: 12, border: '1px solid var(--border)', display: 'flex', gap: 12, marginBottom: 24, alignItems: 'center' }}>
          <div style={{ flex: 1 }}>
            <input placeholder="Form field label (e.g. 'Desired Salary')" value={newLabel} onChange={e => setNewLabel(e.target.value)} style={{ width: '100%', padding: '10px 14px', borderRadius: 8, border: '1px solid var(--border)', background: 'var(--bg)', color: 'var(--text-primary)', fontSize: '0.9rem' }} required />
          </div>
          <div style={{ flex: 1 }}>
            <input placeholder="Auto-fill value (e.g. '120,000')" value={newValue} onChange={e => setNewValue(e.target.value)} style={{ width: '100%', padding: '10px 14px', borderRadius: 8, border: '1px solid var(--border)', background: 'var(--bg)', color: 'var(--text-primary)', fontSize: '0.9rem' }} required />
          </div>
          <button type="submit" style={{ background: 'var(--text-primary)', color: 'var(--bg)', border: 'none', padding: '10px 20px', borderRadius: 8, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
            <Plus size={16} /> Add Rule
          </button>
        </form>
      )}

      {filtered.length === 0 ? (
        <div style={{ padding: 48, textAlign: 'center', background: 'var(--surface)', borderRadius: 16, border: '1px dashed var(--border)' }}>
          <p style={{ color: 'var(--text-secondary)' }}>No {tab} mapping rules found.</p>
        </div>
      ) : (
        <div style={{ background: 'var(--surface)', borderRadius: 16, border: '1px solid var(--border)', overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
            <thead>
              <tr style={{ background: 'var(--bg)', borderBottom: '1px solid var(--border)', color: 'var(--text-secondary)' }}>
                <th style={{ padding: '16px 24px', fontWeight: 600 }}>Form Label Encountered</th>
                <th style={{ padding: '16px 24px', fontWeight: 600 }}>Auto-fill Value</th>
                <th style={{ padding: '16px 24px', fontWeight: 600, textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(m => (
                <tr key={m.id} style={{ borderBottom: '1px solid var(--border)' }}>
                  <td style={{ padding: '16px 24px', fontWeight: 500, color: 'var(--text-primary)' }}>{m.label_text}</td>
                  <td style={{ padding: '16px 24px', color: 'var(--text-secondary)' }}>{m.field_value || <em style={{ opacity: 0.5 }}>none</em>}</td>
                  <td style={{ padding: '16px 24px', textAlign: 'right' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 8 }}>
                      {tab === 'pending' && (
                        <button onClick={() => updateStatus(m.id, 'active')} title="Approve" style={{ background: 'rgba(16,185,129,0.1)', color: '#10b981', border: 'none', width: 32, height: 32, borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
                          <Check size={16} strokeWidth={3} />
                        </button>
                      )}
                      <button onClick={() => deleteMapping(m.id)} title="Delete" style={{ background: 'rgba(239,68,68,0.1)', color: '#ef4444', border: 'none', width: 32, height: 32, borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
                        <X size={16} strokeWidth={3} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

// ── App ───────────────────────────────────────────────────────────────────────
export default function Dashboard() {
  const [page, setPage] = useState('jobs'); // 'jobs' | 'companies'
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [isDark, setIsDark] = useState(false);
  const { user, logout } = useAuth();

  // Load dark mode preference on mount
  useEffect(() => {
    api.get('/api/preferences').then(r => {
      if (r.data.dark_mode) {
        document.documentElement.setAttribute('data-theme', 'dark');
        setIsDark(true);
      }
    }).catch(() => {});
  }, []);

  return (
    <div style={{ minHeight: '100vh', paddingBottom: 60 }}>
      {/* ── Header ── */}
      <header style={{ background: 'var(--surface)', borderBottom: '1px solid var(--border)', boxShadow: 'var(--shadow-sm)', position: 'sticky', top: 0, zIndex: 50 }}>
        <div className="page-wrapper" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: 60 }}>
          {/* Logo */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))', padding: 8, borderRadius: 10, boxShadow: '0 2px 8px rgba(59,130,246,0.3)' }}>
              <Rocket color="#fff" size={18} />
            </div>
            <span style={{ fontWeight: 800, fontSize: '1.1rem', letterSpacing: '-0.4px', color: 'var(--text-primary)' }}>Job-Copilot</span>
          </div>

          {/* Nav tabs */}
          <div style={{ display: 'flex', gap: 4, background: 'var(--bg)', padding: 4, borderRadius: 10, border: '1px solid var(--border)' }}>
            {[['jobs', 'Jobs'], ['companies', 'Companies'], ['autofill', 'Autofill']].map(([id, label]) => (
              <button key={id} onClick={() => setPage(id)} style={{ padding: '6px 18px', borderRadius: 8, border: 'none', cursor: 'pointer', fontSize: '0.875rem', fontWeight: 600, background: page === id ? 'var(--surface)' : 'transparent', color: page === id ? 'var(--accent-blue)' : 'var(--text-secondary)', boxShadow: page === id ? 'var(--shadow-sm)' : 'none', transition: 'all 0.15s' }}>
                {label}
              </button>
            ))}
          </div>

          {/* User & Settings */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{ background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: 9, padding: '4px 12px', display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Welcome, </span>
              <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-primary)' }}>{user?.username}</span>
            </div>
            
            <button onClick={() => setSettingsOpen(true)} style={{ background: 'var(--bg)', border: '1px solid var(--border)', color: 'var(--text-secondary)', padding: '8px 12px', borderRadius: 9, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 7, fontSize: '0.85rem', fontWeight: 600, transition: 'all 0.15s', boxShadow: 'var(--shadow-sm)' }}
              onMouseOver={e => { e.currentTarget.style.borderColor = 'var(--accent-blue)'; e.currentTarget.style.color = 'var(--accent-blue)'; }}
              onMouseOut={e => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.color = 'var(--text-secondary)'; }}>
              <Settings size={16} /> Preferences
            </button>

            <button onClick={logout} style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)', color: 'var(--accent-red)', padding: '8px 16px', borderRadius: 9, cursor: 'pointer', fontSize: '0.85rem', fontWeight: 700, transition: 'all 0.15s' }}>
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* ── Main content ── */}
      <main className="page-wrapper" style={{ paddingTop: 32 }}>
        {page === 'jobs' && <JobsView />}
        {page === 'companies' && <CompaniesView />}
        {page === 'autofill' && <MappingsView />}
      </main>

      <SettingsDrawer open={settingsOpen} onClose={() => setSettingsOpen(false)} isDark={isDark} />
    </div>
  );
}
