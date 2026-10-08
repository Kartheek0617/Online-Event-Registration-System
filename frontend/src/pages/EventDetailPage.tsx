import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { EventDetail } from '../types';
import { Alert } from '../components/Alert';
import { Modal } from '../components/Modal';

export const EventDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { user, isStudent, isFaculty, isAdmin } = useAuth();

  const [event, setEvent] = useState<EventDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [isRegistering, setIsRegistering] = useState(false);
  const [showConfirmModal, setShowConfirmModal] = useState(false);

  const fetchDetail = async () => {
    if (!id) return;
    setLoading(true);
    try {
      const data = await api.events.get(parseInt(id, 10));
      setEvent(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load event details');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetail();
  }, [id]);

  const handleRegister = async () => {
    if (!event) return;
    setIsRegistering(true);
    setError(null);
    try {
      const res = await api.registrations.register(event.id);
      setSuccessMsg(res.message);
      setShowConfirmModal(false);
      // Refresh event details to update capacity and registration status
      await fetchDetail();
    } catch (err: any) {
      setError(err.message || 'Registration failed');
      setShowConfirmModal(false);
    } finally {
      setIsRegistering(false);
    }
  };

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

  if (loading) {
    return (
      <div className="container" style={{ textAlign: 'center', padding: '5rem 0', color: 'var(--text-muted)' }}>
        <div style={{ display: 'inline-block', width: '32px', height: '32px', border: '3px solid var(--border-glass)', borderTopColor: 'var(--primary-500)', borderRadius: '50%', animation: 'spin 0.8s linear infinite', marginBottom: '1rem' }} />
        <p>Loading event information...</p>
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  if (!event) {
    return (
      <div className="container" style={{ maxWidth: '600px', margin: '4rem auto', textAlign: 'center' }}>
        <div className="glass-card">
          <h2 style={{ color: 'var(--heading-color)' }}>Event Not Found</h2>
          <p style={{ color: 'var(--text-muted)', margin: '1rem 0' }}>The requested event does not exist or has been removed.</p>
          <Link to="/events" className="btn btn-primary">Back to Events</Link>
        </div>
      </div>
    );
  }

  const isFull = event.available_seats <= 0;
  const isClosed = event.status === 'CLOSED';
  const percentFilled = Math.min(100, Math.round((event.registered_count / event.participant_limit) * 100));

  return (
    <div className="container" style={{ maxWidth: '940px' }}>
      <div style={{ marginBottom: '1.5rem' }}>
        <Link to="/events" style={{ color: 'var(--primary-400)', fontSize: '0.9rem', display: 'inline-flex', alignItems: 'center', gap: '0.4rem', fontWeight: 600 }}>
          ← Back to All Events
        </Link>
      </div>

      {error && <Alert type="danger" message={error} onClose={() => setError(null)} />}
      {successMsg && <Alert type="success" message={successMsg} onClose={() => setSuccessMsg(null)} />}

      <div className="glass-card" style={{ padding: '2.5rem' }}>
        {/* Header Tags */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem' }}>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            <span className={`badge ${getCategoryBadgeClass(event.category)}`}>{event.category}</span>
            {isClosed ? (
              <span className="badge badge-closed">Registration Closed</span>
            ) : isFull ? (
              <span className="badge badge-warning">Capacity Full</span>
            ) : (
              <span className="badge badge-open">Registration Open</span>
            )}
          </div>

          {event.is_registered_by_user && (
            <span className="badge badge-confirmed" style={{ fontSize: '0.85rem' }}>
              ✓ You are Registered
            </span>
          )}
        </div>

        {/* Title */}
        <h1 style={{ fontSize: '2.35rem', fontWeight: 800, marginBottom: '1rem', color: 'var(--heading-color)', letterSpacing: '-0.02em', lineHeight: '1.3' }}>
          {event.title}
        </h1>

        {/* Description */}
        <p style={{ color: 'var(--text-muted)', fontSize: '1.05rem', lineHeight: '1.75', marginBottom: '2.25rem', whiteSpace: 'pre-line' }}>
          {event.description}
        </p>

        {/* Event Logistics Grid Box */}
        <div className="glass-card" style={{ background: 'var(--bg-card-inner)', marginBottom: '2.25rem', border: '1px solid var(--border-glass)' }}>
          <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--primary-400)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '1.25rem' }}>
            Event Logistics & Schedule
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.25rem', fontSize: '0.9rem' }}>
            <div>
              <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.78rem', textTransform: 'uppercase', marginBottom: '0.2rem' }}>EVENT DATE</span>
              <strong style={{ color: 'var(--text-main)' }}>📅 {event.event_date}</strong>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.78rem', textTransform: 'uppercase', marginBottom: '0.2rem' }}>SCHEDULE TIME</span>
              <strong style={{ color: 'var(--text-main)' }}>⏰ {event.start_time} - {event.end_time}</strong>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.78rem', textTransform: 'uppercase', marginBottom: '0.2rem' }}>CAMPUS VENUE</span>
              <strong style={{ color: 'var(--text-main)' }}>📍 {event.venue}</strong>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.78rem', textTransform: 'uppercase', marginBottom: '0.2rem' }}>ORGANIZER</span>
              <strong style={{ color: 'var(--text-main)' }}>👤 {event.organizer_name || 'Faculty Coordinator'}</strong>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.78rem', textTransform: 'uppercase', marginBottom: '0.2rem' }}>REGISTRATION DEADLINE</span>
              <strong style={{ color: 'var(--text-main)' }}>⏳ {event.registration_deadline.replace('T', ' ')}</strong>
            </div>
          </div>
        </div>

        {/* Capacity Progress Bar */}
        <div style={{ marginBottom: '2.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem', marginBottom: '0.5rem' }}>
            <span style={{ color: 'var(--text-muted)' }}>Registered Attendance Capacity</span>
            <strong style={{ color: 'var(--text-main)' }}>
              {event.registered_count} / {event.participant_limit} seats filled ({event.available_seats} remaining)
            </strong>
          </div>
          <div style={{ height: '10px', background: 'var(--border-glass)', borderRadius: '999px', overflow: 'hidden' }}>
            <div
              style={{
                height: '100%',
                width: `${percentFilled}%`,
                background: isFull
                  ? 'var(--danger)'
                  : percentFilled > 80
                  ? 'var(--warning)'
                  : 'linear-gradient(90deg, #6366f1, #10b981)',
                transition: 'width 0.4s ease',
              }}
            />
          </div>
        </div>

        {/* Action Controls */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', alignItems: 'center' }}>
          {isStudent && (
            <>
              {event.is_registered_by_user ? (
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                  <Link to="/my-registrations" className="btn btn-secondary">
                    View in My Registrations
                  </Link>
                  <span style={{ color: 'var(--success)', fontSize: '0.9rem', fontWeight: 600 }}>
                    ✓ You are registered for this event.
                  </span>
                </div>
              ) : isClosed ? (
                <button className="btn btn-secondary" disabled>
                  Registration Closed
                </button>
              ) : isFull ? (
                <button className="btn btn-secondary" disabled>
                  Event Full (Capacity Reached)
                </button>
              ) : (
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={() => setShowConfirmModal(true)}
                  disabled={isRegistering}
                >
                  Register Now for this Event
                </button>
              )}
            </>
          )}

          {!user && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
              <Link to="/login" className="btn btn-primary">
                Sign In as Student to Register
              </Link>
              <span style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                Authentication required for registration
              </span>
            </div>
          )}

          {(isFaculty || isAdmin) && user && (event.organizer_id === user.id || isAdmin) && (
            <Link to={`/events/${event.id}/participants`} className="btn btn-secondary">
              View Registered Participants ({event.registered_count}) →
            </Link>
          )}
        </div>
      </div>

      {/* Confirmation Modal */}
      <Modal
        isOpen={showConfirmModal}
        onClose={() => setShowConfirmModal(false)}
        title="Confirm Event Registration"
        footer={
          <>
            <button
              type="button"
              className="btn btn-outline btn-sm"
              onClick={() => setShowConfirmModal(false)}
              disabled={isRegistering}
            >
              Cancel
            </button>
            <button
              type="button"
              className="btn btn-primary btn-sm"
              onClick={handleRegister}
              disabled={isRegistering}
            >
              {isRegistering ? 'Registering...' : 'Confirm Registration'}
            </button>
          </>
        }
      >
        <p style={{ marginBottom: '1rem', color: 'var(--text-main)' }}>
          Are you sure you want to register for <strong>{event.title}</strong>?
        </p>
        <div style={{ background: 'var(--bg-card-inner)', padding: '0.95rem', borderRadius: '8px', fontSize: '0.875rem', border: '1px solid var(--border-glass)' }}>
          <p style={{ marginBottom: '0.35rem' }}>📅 <strong>Date:</strong> {event.event_date}</p>
          <p style={{ marginBottom: '0.35rem' }}>⏰ <strong>Time:</strong> {event.start_time} - {event.end_time}</p>
          <p>📍 <strong>Venue:</strong> {event.venue}</p>
        </div>
      </Modal>
    </div>
  );
};
