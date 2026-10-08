import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import { Event } from '../types';
import { Alert } from '../components/Alert';
import { Modal } from '../components/Modal';

export const FacultyDashboard: React.FC = () => {
  const { user } = useAuth();
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const [closeTarget, setCloseTarget] = useState<Event | null>(null);
  const [closing, setClosing] = useState(false);

  const fetchFacultyEvents = async () => {
    setLoading(true);
    try {
      const allEvents = await api.events.list();
      // Filter events where organizer_id matches current faculty user
      const myEvents = allEvents.filter((e) => e.organizer_id === user?.id);
      setEvents(myEvents);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch events');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFacultyEvents();
  }, [user]);

  const handleCloseRegistration = async () => {
    if (!closeTarget) return;
    setClosing(true);
    setError(null);
    try {
      await api.events.close(closeTarget.id);
      setSuccessMsg(`Registration for "${closeTarget.title}" has been closed.`);
      setCloseTarget(null);
      await fetchFacultyEvents();
    } catch (err: any) {
      setError(err.message || 'Failed to close registration');
    } finally {
      setClosing(false);
    }
  };

  const totalAttendees = events.reduce((acc, curr) => acc + curr.registered_count, 0);
  const activeEvents = events.filter((e) => e.status === 'OPEN').length;

  const getCategoryBadgeClass = (category: string) => {
    switch (category) {
      case 'Cybersecurity': return 'badge-cat-cybersecurity';
      case 'Artificial Intelligence': return 'badge-cat-ai';
      case 'Web Engineering': return 'badge-cat-web';
      case 'Cultural': return 'badge-cat-cultural';
      case 'Symposium': return 'badge-cat-symposium';
      case 'Robotics': return 'badge-cat-robotics';
      default: return 'badge-info';
    }
  };

  return (
    <div className="container">
      {/* Header section */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '2rem' }}>
        <div>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', background: 'var(--bg-glass)', border: '1px solid var(--border-glass)', borderRadius: '999px', padding: '0.3rem 0.8rem', fontSize: '0.8rem', fontWeight: 600, color: 'var(--primary-400)', marginBottom: '0.75rem' }}>
            <span>🏛️ Faculty Coordinator Hub</span>
            <span>•</span>
            <span>Event Management & Rosters</span>
          </div>
          <h1 style={{ fontSize: '2.25rem', fontWeight: 800, marginBottom: '0.5rem', color: 'var(--heading-color)', letterSpacing: '-0.02em' }}>
            Faculty Organizer Hub
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '1rem', maxWidth: '680px' }}>
            Welcome, {user?.name}. Manage your department events, inspect participant rosters, and adjust seating limits.
          </p>
        </div>
        <Link to="/create-event" className="btn btn-primary">
          + Create New Event
        </Link>
      </div>

      {error && <Alert type="danger" message={error} onClose={() => setError(null)} />}
      {successMsg && <Alert type="success" message={successMsg} onClose={() => setSuccessMsg(null)} />}

      {/* Metrics Row */}
      <div className="grid-stats">
        <div className="glass-card">
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Events Organized by You
          </span>
          <p style={{ fontSize: '2.25rem', fontWeight: 800, color: 'var(--primary-400)', marginTop: '0.25rem' }}>
            {events.length}
          </p>
        </div>

        <div className="glass-card">
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Total Registered Attendees
          </span>
          <p style={{ fontSize: '2.25rem', fontWeight: 800, color: 'var(--success)', marginTop: '0.25rem' }}>
            {totalAttendees}
          </p>
        </div>

        <div className="glass-card">
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Active Open Events
          </span>
          <p style={{ fontSize: '2.25rem', fontWeight: 800, color: 'var(--info)', marginTop: '0.25rem' }}>
            {activeEvents}
          </p>
        </div>
      </div>

      {/* Events Table */}
      <div className="glass-card" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ padding: '1.25rem 1.5rem', borderBottom: '1px solid var(--border-glass)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700 }}>Your Created Events</h2>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Object-Level Authorization: Only you can manage these events
          </span>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem 0', color: 'var(--text-muted)' }}>
            <p>Loading your events...</p>
          </div>
        ) : events.length === 0 ? (
          <div className="empty-state">
            <h3>No events created yet</h3>
            <p style={{ marginTop: '0.5rem', marginBottom: '1.5rem' }}>
              Create your first campus workshop, seminar, or competition.
            </p>
            <Link to="/create-event" className="btn btn-primary">+ Create Event</Link>
          </div>
        ) : (
          <div className="table-container" style={{ border: 'none' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Event Title</th>
                  <th>Category</th>
                  <th>Date & Time</th>
                  <th>Attendance / Capacity</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {events.map((ev) => (
                  <tr key={ev.id}>
                    <td>
                      <strong>
                        <Link to={`/events/${ev.id}`} style={{ color: 'var(--text-main)', textDecoration: 'underline' }}>
                          {ev.title}
                        </Link>
                      </strong>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>📍 {ev.venue}</div>
                    </td>
                    <td>
                      <span className={`badge ${getCategoryBadgeClass(ev.category)}`}>{ev.category}</span>
                    </td>
                    <td>
                      <div>📅 {ev.event_date}</div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>⏰ {ev.start_time} - {ev.end_time}</div>
                    </td>
                    <td style={{ minWidth: '160px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.825rem', marginBottom: '0.35rem' }}>
                        <span><strong>{ev.registered_count}</strong> / {ev.participant_limit}</span>
                        <span style={{ color: ev.available_seats === 0 ? 'var(--danger)' : 'var(--success)', fontWeight: 600 }}>
                          {ev.available_seats} left
                        </span>
                      </div>
                      <div className="progress-bar-container">
                        <div
                          className="progress-bar-fill"
                          style={{
                            width: `${Math.min(100, Math.round(((ev.participant_limit - ev.available_seats) / ev.participant_limit) * 100))}%`,
                            background: ev.available_seats <= 0 ? 'var(--danger)' : ev.available_seats <= 5 ? 'var(--warning)' : 'var(--primary-500)',
                          }}
                        />
                      </div>
                    </td>
                    <td>
                      <span className={`badge badge-${ev.status === 'OPEN' ? 'open' : 'closed'}`}>
                        {ev.status}
                      </span>
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                        <Link to={`/events/${ev.id}/participants`} className="btn btn-secondary btn-sm">
                          👥 Attendees ({ev.registered_count})
                        </Link>
                        {ev.status === 'OPEN' && (
                          <button
                            type="button"
                            className="btn btn-danger btn-sm"
                            onClick={() => setCloseTarget(ev)}
                          >
                            Close Registration
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Close Registration Confirmation Modal */}
      <Modal
        isOpen={!!closeTarget}
        onClose={() => setCloseTarget(null)}
        title="Confirm Event Closure"
        footer={
          <>
            <button
              type="button"
              className="btn btn-outline btn-sm"
              onClick={() => setCloseTarget(null)}
              disabled={closing}
            >
              Cancel
            </button>
            <button
              type="button"
              className="btn btn-danger btn-sm"
              onClick={handleCloseRegistration}
              disabled={closing}
            >
              {closing ? 'Closing...' : 'Close Event Registration'}
            </button>
          </>
        }
      >
        <p style={{ marginBottom: '1rem' }}>
          Are you sure you want to close registration for <strong>{closeTarget?.title}</strong>?
        </p>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
          Once closed, students will no longer be able to register for this event.
        </p>
      </Modal>
    </div>
  );
};
