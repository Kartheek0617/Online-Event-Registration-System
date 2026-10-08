import React, { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Alert } from '../components/Alert';

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const from = (location.state as any)?.from?.pathname || '/events';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const user = await login(email, password);
      if (user.role === 'STUDENT') navigate('/student');
      else if (user.role === 'FACULTY') navigate('/faculty');
      else if (user.role === 'ADMIN') navigate('/admin');
      else navigate(from);
    } catch (err: any) {
      setError(err.message || 'Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  const fillCredentials = (demEmail: string, demPass: string) => {
    setEmail(demEmail);
    setPassword(demPass);
    setError(null);
  };

  return (
    <div className="container" style={{ maxWidth: '480px', marginTop: '3rem' }}>
      <div className="glass-card" style={{ padding: '2rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{
            display: 'inline-flex',
            padding: '0.75rem',
            borderRadius: '50%',
            background: 'rgba(99, 102, 241, 0.1)',
            color: '#6366f1',
            marginBottom: '0.75rem'
          }}>
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2a5 5 0 0 0-5 5v3H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8a2 2 0 0 0-2-2h-1V7a5 5 0 0 0-5-5zM9 7a3 3 0 0 1 6 0v3H9V7z"/>
            </svg>
          </div>
          <h1 style={{ fontSize: '1.65rem', fontWeight: 800, color: 'var(--heading-color)', letterSpacing: '-0.02em' }}>
            Sign In to EventHub
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.35rem' }}>
            Secure college event registration with enterprise RBAC
          </p>
        </div>

        {error && <Alert type="danger" message={error} onClose={() => setError(null)} />}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="email-input">College Email Address</label>
            <input
              id="email-input"
              type="email"
              className="form-input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="e.g. student.aarav@college.edu"
              required
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="password-input">Password</label>
            <input
              id="password-input"
              type="password"
              className="form-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••••••"
              required
              autoComplete="current-password"
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', marginTop: '0.75rem', padding: '0.75rem 1.25rem', fontSize: '0.95rem' }}
            disabled={loading}
          >
            {loading ? 'Authenticating securely...' : 'Sign In to EventHub →'}
          </button>
        </form>

        {/* 1-Click Academic Demo Credentials Panel */}
        <div style={{ marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px solid var(--border-glass)' }}>
          <p style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.75rem', textAlign: 'center' }}>
            Academic Lab Demo Presets (1-Click Fill)
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.5rem' }}>
            <button
              type="button"
              className="btn btn-outline btn-sm"
              onClick={() => fillCredentials('student.aarav@college.edu', 'Student@Secure123')}
              title="Student preset"
              style={{ fontSize: '0.8rem' }}
            >
              👨‍🎓 Student
            </button>
            <button
              type="button"
              className="btn btn-outline btn-sm"
              onClick={() => fillCredentials('faculty.sharma@college.edu', 'Faculty@Secure123')}
              title="Faculty preset"
              style={{ fontSize: '0.8rem' }}
            >
              👨‍🏫 Faculty
            </button>
            <button
              type="button"
              className="btn btn-outline btn-sm"
              onClick={() => fillCredentials('admin@college.edu', 'Admin@Secure123')}
              title="Admin preset"
              style={{ fontSize: '0.8rem' }}
            >
              🛡️ Admin
            </button>
          </div>
        </div>

        <div style={{ textAlign: 'center', marginTop: '1.5rem' }}>
          <Link to="/events" style={{ fontSize: '0.85rem', color: 'var(--primary-400)', textDecoration: 'underline' }}>
            Browse Public Events as Guest
          </Link>
        </div>
      </div>
    </div>
  );
};
