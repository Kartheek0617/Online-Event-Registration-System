import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import { Event } from '../types';
import { Alert } from '../components/Alert';
import { Modal } from '../components/Modal';

export const ManageEventsPage: React.FC = () => {
  const { user } = useAuth();
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const [editEvent, setEditEvent] = useState<Event | null>(null);
  const [editVenue, setEditVenue] = useState('');
  const [editLimit, setEditLimit] = useState<number>(0);
  const [savingEdit, setSavingEdit] = useState(false);

  const [closeTarget, setCloseTarget] = useState<Event | null>(null);
  const [closing, setClosing] = useState(false);

  const fetchEvents = async () => {
    setLoading(true);
    try {
      const allEvents = await api.events.list();
      const myEvents = allEvents.filter((e) => e.organizer_id === user?.id || user?.role === 'ADMIN');
      setEvents(myEvents);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch events');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, [user]);

  const handleOpenEdit = (ev: Event) => {
    setEditEvent(ev);
    setEditVenue(ev.venue);
    setEditLimit(ev.participant_limit);
  };

  const handleSaveEdit = async () => {
    if (!editEvent) return;
    setSavingEdit(true);
    setError(null);
    try {
      await api.events.update(editEvent.id, {
        venue: editVenue,
        participant_limit: editLimit,
      });
      setSuccessMsg(`Event "${editEvent.title}" updated successfully.`);
      setEditEvent(null);
      await fetchEvents();
    } catch (err: any) {
      setError(err.message || 'Failed to update event');
    } finally {
      setSavingEdit(false);
    }
  };

  const handleCloseRegistration = async () => {
    if (!closeTarget) return;
    setClosing(true);
    setError(null);
    try {
      await api.events.close(closeTarget.id);
      setSuccessMsg(`Registration closed for "${closeTarget.title}".`);
      setCloseTarget(null);
      await fetchEvents();
    } catch (err: any) {
      setError(err.message || 'Failed to close registration');
    } finally {
      setClosing(false);
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

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '2rem' }}>
        <div>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', background: 'var(--bg-glass)', border: '1px solid var(--border-glass)', borderRadius: '999px', padding: '0.3rem 0.8rem', fontSize: '0.8rem', fontWeight: 600, color: 'var(--primary-400)', marginBottom: '0.75rem' }}>
            <span>⚙️ Management Console</span>
            <span>•</span>
            <span>Logistics & Quota Controls</span>
          </div>
          <h1 style={{ fontSize: '2.25rem', fontWeight: 800, marginBottom: '0.5rem', color: 'var(--heading-color)', letterSpacing: '-0.02em' }}>
            Manage Your Events
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '1rem', maxWidth: '680px' }}>
            Edit event logistics, close active registrations, and inspect confirmed rosters.
          </p>
        </div>
        <Link to="/create-event" className="btn btn-primary">
          + Create New Event
        </Link>
      </div>

      {error && <Alert type="danger" message={error} onClose={() => setError(null)} />}
      {successMsg && <Alert type="success" message={successMsg} onClose={() => setSuccessMsg(null)} />}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '4rem 0', color: 'var(--text-muted)' }}>
          <p>Loading events...</p>
        </div>
      ) : events.length === 0 ? (
        <div className="glass-card empty-state">
          <h3>No events found</h3>
          <p style={{ margin: '1rem 0' }}>You haven't created any events yet.</p>
          <Link to="/create-event" className="btn btn-primary">Create Event</Link>
        </div>
      ) : (
        <div className="table-container glass-card" style={{ padding: 0 }}>
          <table className="table">
            <thead>
              <tr>
                <th>Event Title</th>
                <th>Category</th>
                <th>Venue</th>
                <th>Date</th>
                <th>Capacity</th>
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
                  </td>
                  <td>
                    <span className={`badge ${getCategoryBadgeClass(ev.category)}`}>
                      {ev.category}
                    </span>
                  </td>
                  <td>📍 {ev.venue}</td>
                  <td>📅 {ev.event_date}</td>
                  <td>
                    <strong>{ev.registered_count}</strong> / {ev.participant_limit} seats
                  </td>
                  <td>
                    <span className={`badge badge-${ev.status === 'OPEN' ? 'open' : 'closed'}`}>
                      {ev.status}
                    </span>
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                      <Link to={`/events/${ev.id}/participants`} className="btn btn-secondary btn-sm">
                        Participants ({ev.registered_count})
                      </Link>
                      <button
                        type="button"
                        className="btn btn-outline btn-sm"
                        onClick={() => handleOpenEdit(ev)}
                      >
                        Edit
                      </button>
                      {ev.status === 'OPEN' && (
                        <button
                          type="button"
                          className="btn btn-danger btn-sm"
                          onClick={() => setCloseTarget(ev)}
                        >
                          Close
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

      {/* Edit Modal */}
      <Modal
        isOpen={!!editEvent}
        onClose={() => setEditEvent(null)}
        title={`Edit Event: ${editEvent?.title}`}
        footer={
          <>
            <button
              type="button"
              className="btn btn-outline btn-sm"
              onClick={() => setEditEvent(null)}
              disabled={savingEdit}
            >
              Cancel
            </button>
            <button
              type="button"
              className="btn btn-primary btn-sm"
              onClick={handleSaveEdit}
              disabled={savingEdit}
            >
              {savingEdit ? 'Saving...' : 'Save Changes'}
            </button>
          </>
        }
      >
        <div className="form-group">
          <label className="form-label" htmlFor="edit-venue">Venue</label>
          <input
            id="edit-venue"
            type="text"
            className="form-input"
            value={editVenue}
            onChange={(e) => setEditVenue(e.target.value)}
          />
        </div>
        <div className="form-group">
          <label className="form-label" htmlFor="edit-limit">Participant Limit</label>
          <input
            id="edit-limit"
            type="number"
            min="1"
            className="form-input"
            value={editLimit}
            onChange={(e) => setEditLimit(parseInt(e.target.value, 10) || 0)}
          />
          <small style={{ color: 'var(--text-muted)' }}>
            Must be greater than or equal to current confirmed attendance ({editEvent?.registered_count}).
          </small>
        </div>
      </Modal>

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
              {closing ? 'Closing...' : 'Close Event'}
            </button>
          </>
        }
      >
        <p>Are you sure you want to close registration for <strong>{closeTarget?.title}</strong>?</p>
      </Modal>
    </div>
  );
};
