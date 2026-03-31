import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Link, useNavigate } from 'react-router-dom';
import { Rocket, Mail, Lock, User, Loader2, ArrowRight } from 'lucide-react';

export default function Signup() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { signup } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await signup(username, password, email);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Signup failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={containerStyle}>
      <div style={glassCardStyle}>
        <div style={headerStyle}>
          <div style={logoContainerStyle}>
            <Rocket size={32} color="#3b82f6" />
          </div>
          <h1 style={titleStyle}>Join Job-Copilot</h1>
          <p style={subtitleStyle}>Command your career with AI-driven discovery</p>
        </div>

        <form onSubmit={handleSubmit} style={formStyle}>
          {error && <div style={errorStyle}>{error}</div>}
          
          <div style={inputGroupStyle}>
            <label style={labelStyle}>Username</label>
            <div style={inputWrapperStyle}>
              <User size={18} style={iconStyle} />
              <input 
                type="text" 
                value={username} 
                onChange={(e) => setUsername(e.target.value)} 
                placeholder="Choose a username"
                style={inputStyle}
                required
              />
            </div>
          </div>

          <div style={inputGroupStyle}>
            <label style={labelStyle}>Email Address</label>
            <div style={inputWrapperStyle}>
              <Mail size={18} style={iconStyle} />
              <input 
                type="email" 
                value={email} 
                onChange={(e) => setEmail(e.target.value)} 
                placeholder="your@email.com"
                style={inputStyle}
                required
              />
            </div>
          </div>

          <div style={inputGroupStyle}>
            <label style={labelStyle}>Password</label>
            <div style={inputWrapperStyle}>
              <Lock size={18} style={iconStyle} />
              <input 
                type="password" 
                value={password} 
                onChange={(e) => setPassword(e.target.value)} 
                placeholder="••••••••"
                style={inputStyle}
                required
              />
            </div>
          </div>

          <button type="submit" disabled={loading} style={buttonStyle}>
            {loading ? <Loader2 size={20} className="animate-spin" /> : (
              <>
                Create Account
                <ArrowRight size={18} style={{ marginLeft: 8 }} />
              </>
            )}
          </button>
        </form>

        <p style={footerTextStyle}>
          Already have an account? <Link to="/login" style={linkStyle}>Log in</Link>
        </p>
      </div>
    </div>
  );
}

// ── Styles ──────────────────────────────────────────────────────────────────

const containerStyle = {
  minHeight: '100vh',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  background: 'linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)',
  padding: '20px'
};

const glassCardStyle = {
  width: '100%',
  maxWidth: '440px',
  background: 'rgba(255, 255, 255, 0.03)',
  backdropFilter: 'blur(16px)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  borderRadius: '24px',
  padding: '40px',
  boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)'
};

const headerStyle = {
  textAlign: 'center',
  marginBottom: '32px'
};

const logoContainerStyle = {
  width: '64px',
  height: '64px',
  background: 'rgba(59, 130, 246, 0.1)',
  borderRadius: '16px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  margin: '0 auto 16px'
};

const titleStyle = {
  fontSize: '1.75rem',
  fontWeight: 800,
  color: '#fff',
  marginBottom: '8px'
};

const subtitleStyle = {
  color: '#94a3b8',
  fontSize: '0.9rem'
};

const formStyle = {
  display: 'flex',
  flexDirection: 'column',
  gap: '20px'
};

const inputGroupStyle = {
  display: 'flex',
  flexDirection: 'column',
  gap: '8px'
};

const labelStyle = {
  fontSize: '0.8rem',
  fontWeight: 600,
  color: '#cbd5e1',
  marginLeft: '4px'
};

const inputWrapperStyle = {
  position: 'relative',
  display: 'flex',
  alignItems: 'center'
};

const iconStyle = {
  position: 'absolute',
  left: '12px',
  color: '#64748b'
};

const inputStyle = {
  width: '100%',
  background: 'rgba(15, 23, 42, 0.5)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  borderRadius: '12px',
  padding: '12px 12px 12px 40px',
  color: '#fff',
  fontSize: '0.95rem',
  outline: 'none',
  transition: 'border-color 0.2s'
};

const buttonStyle = {
  background: '#3b82f6',
  color: '#fff',
  border: 'none',
  borderRadius: '12px',
  padding: '14px',
  fontSize: '1rem',
  fontWeight: 600,
  cursor: 'pointer',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  marginTop: '12px',
  transition: 'transform 0.1s, background 0.2s'
};

const errorStyle = {
  background: 'rgba(239, 68, 68, 0.1)',
  border: '1px solid rgba(239, 68, 68, 0.2)',
  color: '#f87171',
  padding: '12px',
  borderRadius: '10px',
  fontSize: '0.85rem',
  textAlign: 'center'
};

const footerTextStyle = {
  textAlign: 'center',
  marginTop: '24px',
  color: '#94a3b8',
  fontSize: '0.9rem'
};

const linkStyle = {
  color: '#3b82f6',
  textDecoration: 'none',
  fontWeight: 600
};
