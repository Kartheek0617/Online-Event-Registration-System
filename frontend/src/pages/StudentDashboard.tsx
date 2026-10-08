import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import { Registration, Event } from '../types';

export const StudentDashboard: React.FC = () => {
  const { user } = useAuth();
  const [registrations, setRegistrations] = useState<Registration[]>([]);
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        const [regs, evs] = await Promise.all([
          api.registrations.myRegistrations(),
          api.events.list(),
        ]);
        setRegistrations(regs);
        setEvents(evs);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    loadDashboard();
  }, []);

  const activeRegistrations = registrations.filter((r) => r.status === 'CONFIRMED');
  const openEvents = events.filter((e) => e.status === 'OPEN' && e.available_seats > 0);

  return (
    <div className="container">
      {/* Welcome Banner */}
      <div className="hero-banner">
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', background: 'var(--bg-glass)', border: '1px solid var(--border-glass)', borderRadius: '999px', padding: '0.3rem 0.8rem', fontSize: '0.8rem', fontWeight: 600, color: 'var(--primary-400)', marginBottom: '0.75rem' }}>
          <span>🎓 Student Portal</span>
          <span>•</span>
          <span>Verified Enrollment</span>
        </div>
        <h1 style={{ fontSize: '2rem', fontWeight: 800, marginBottom: '0.5rem', color: 'var(--heading-color)', letterSpacing: '-0.02em' }}>
          Welcome back, {user?.name}!
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '1rem', maxWidth: '680px', lineHeight: '1.6' }}>
          Browse upcoming campus workshops, track your confirmed registrations, and download schedules.
        </p>
      </div>

      {/* Metrics Grid */}
      <div className="grid-stats">
        <div className="glass-card">
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Confirmed Registrations
          </span>
          <p style={{ fontSize: '2.25rem', fontWeight: 800, color: 'var(--success)', marginTop: '0.25rem' }}>
            {activeRegistrations.length}
          </p>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            Active Event Passes
          </div>
        </div>

        <div className="glass-card">
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Available Campus Events
          </span>
          <p style={{ fontSize: '2.25rem', fontWeight: 800, color: 'var(--info)', marginTop: '0.25rem' }}>
            {openEvents.length}
          </p>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            Open For Registration
          </div>
        </div>

        <div className="glass-card">
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Your Role Privileges
          </span>
          <div style={{ marginTop: '0.75rem' }}>
            <span className="badge badge-student" style={{ fontSize: '0.85rem' }}>
              ● STUDENT ACCESS
            </span>
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
            Verified College Participant
          </div>
        </div>
      </div>

      {/* Quick Actions & Recent Registrations */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
        <div className="glass-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--heading-color)' }}>Your Active Registrations</h2>
            <Link to="/my-registrations" style={{ fontSize: '0.85rem', color: 'var(--primary-400)', fontWeight: 600 }}>
              View All →
            </Link>
          </div>

          {activeRegistrations.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '1.5rem 0', color: 'var(--text-muted)' }}>
              <p style={{ fontSize: '0.9rem', marginBottom: '0.75rem' }}>No active registrations found.</p>
              <Link to="/events" className="btn btn-outline btn-sm">Explore Open Events</Link>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {activeRegistrations.slice(0, 3).map((reg) => (
                <div
                  key={reg.id}
                  style={{
                    background: 'var(--bg-card-inner)',
                    padding: '0.95rem',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--border-glass)',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '0.5rem' }}>
                    <Link to={`/events/${reg.event_id}`} style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--text-main)' }}>
                      {reg.event_title}
                    </Link>
                    <span className="badge badge-confirmed">Confirmed</span>
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
                    📅 {reg.event_date} | 📍 {reg.venue}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="glass-card">
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1rem' }}>Quick Actions</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <Link to="/events" className="btn btn-primary" style={{ justifyContent: 'flex-start' }}>
              🔍 Browse & Filter Campus Events
            </Link>
            <Link to="/my-registrations" className="btn btn-secondary" style={{ justifyContent: 'flex-start' }}>
              📋 Manage My Registrations & Cancellations
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
