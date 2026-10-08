import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';

export const Navbar: React.FC = () => {
  const { user, logout, isStudent, isFaculty, isAdmin } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="navbar" aria-label="Main Navigation">
      <div className="nav-container">
        <Link to="/" className="nav-brand" aria-label="EventHub Home">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{ color: '#6366f1' }}>
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="16" y1="2" x2="16" y2="6"></line>
            <line x1="8" y1="2" x2="8" y2="6"></line>
            <line x1="3" y1="10" x2="21" y2="10"></line>
          </svg>
          <span>EventHub</span>
        </Link>

        <ul className="nav-links">
          {/* Public / Common Links */}
          <li>
            <Link to="/events" className={`nav-link ${isActive('/events') ? 'active' : ''}`}>
              Browse Events
            </Link>
          </li>

          {/* Student Navigation */}
          {isStudent && (
            <>
              <li>
                <Link to="/student" className={`nav-link ${isActive('/student') ? 'active' : ''}`}>
                  Student Dashboard
                </Link>
              </li>
              <li>
                <Link to="/my-registrations" className={`nav-link ${isActive('/my-registrations') ? 'active' : ''}`}>
                  My Registrations
                </Link>
              </li>
            </>
          )}

          {/* Faculty Navigation */}
          {isFaculty && (
            <>
              <li>
                <Link to="/faculty" className={`nav-link ${isActive('/faculty') ? 'active' : ''}`}>
                  Faculty Hub
                </Link>
              </li>
              <li>
                <Link to="/create-event" className={`nav-link ${isActive('/create-event') ? 'active' : ''}`}>
                  + Create Event
                </Link>
              </li>
              <li>
                <Link to="/manage-events" className={`nav-link ${isActive('/manage-events') ? 'active' : ''}`}>
                  Manage Events
                </Link>
              </li>
            </>
          )}

          {/* Admin Navigation */}
          {isAdmin && (
            <>
              <li>
                <Link to="/admin" className={`nav-link ${isActive('/admin') ? 'active' : ''}`}>
                  Admin Console
                </Link>
              </li>
              <li>
                <Link to="/admin/audit-logs" className={`nav-link ${isActive('/admin/audit-logs') ? 'active' : ''}`}>
                  Audit Logs
                </Link>
              </li>
            </>
          )}

          {/* Theme Toggle Button */}
          <li>
            <button
              onClick={toggleTheme}
              className="theme-toggle-btn"
              title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
              aria-label={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
              type="button"
            >
              {theme === 'dark' ? '☀️' : '🌙'}
            </button>
          </li>

          {/* Authentication State Controls */}
          {user ? (
            <li style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <span className={`badge badge-${user.role.toLowerCase()}`}>
                {user.role} : {user.name.split(' ')[0]}
              </span>
              <button onClick={handleLogout} className="btn btn-secondary btn-sm" aria-label="Sign out">
                Sign Out
              </button>
            </li>
          ) : (
            <li>
              <Link to="/login" className="btn btn-primary btn-sm">
                Sign In
              </Link>
            </li>
          )}
        </ul>
      </div>
    </nav>
  );
};
