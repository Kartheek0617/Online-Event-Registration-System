import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../services/api';
import { Participant, EventDetail } from '../types';
import { Alert } from '../components/Alert';

export const EventParticipantsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [event, setEvent] = useState<EventDetail | null>(null);
  const [participants, setParticipants] = useState<Participant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchFilter, setSearchFilter] = useState('');

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

  const filteredParticipants = participants.filter((p) => {
    if (!searchFilter.trim()) return true;
    const term = searchFilter.toLowerCase();
    return (
      p.student_name.toLowerCase().includes(term) ||
      p.student_email.toLowerCase().includes(term) ||
      p.student_id.toString().includes(term) ||
      p.registration_id.toString().includes(term)
    );
  });

  useEffect(() => {
    if (!id) return;
    const loadData = async () => {
      setLoading(true);
      try {
        const evId = parseInt(id, 10);
        const [eventData, partsData] = await Promise.all([
          api.events.get(evId),
          api.registrations.participants(evId),
        ]);
        setEvent(eventData);
        setParticipants(partsData);
      } catch (err: any) {
        setError(err.message || 'Access denied or failed to load participant roster.');
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [id]);

  const handleExportCSV = () => {
    if (!event || participants.length === 0) return;
    const headers = ['Registration ID', 'Student ID', 'Student Name', 'Student Email', 'Registered At', 'Status'];
    const rows = participants.map((p) => [
      p.registration_id,
      p.student_id,
      `"${p.student_name}"`,
      p.student_email,
      `"${new Date(p.registered_at).toLocaleString()}"`,
      p.status,
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map((e) => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `participants_event_${event.id}_${event.title.replace(/\s+/g, '_')}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="container">
      <div style={{ marginBottom: '1.5rem' }}>
        <Link to="/manage-events" style={{ color: 'var(--primary-400)', fontSize: '0.9rem', display: 'inline-flex', alignItems: 'center', gap: '0.4rem' }}>
          ← Back to Managed Events
        </Link>
      </div>

      {error && <Alert type="danger" message={error} onClose={() => setError(null)} />}

      {event && (
        <div className="glass-card" style={{ marginBottom: '2rem', padding: '1.75rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <span className={`badge ${getCategoryBadgeClass(event.category)}`} style={{ marginBottom: '0.5rem' }}>
                {event.category}
              </span>
              <h1 style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--heading-color)', letterSpacing: '-0.02em' }}>
                {event.title}
              </h1>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.25rem' }}>
                📅 {event.event_date} | 📍 {event.venue} | 👤 Coordinator: {event.organizer_name}
              </p>
            </div>

            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--success)' }}>
                {participants.length} / {event.participant_limit}
              </div>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Confirmed Attendees</span>
            </div>
          </div>
        </div>
      )}

      {/* Security Data Protection Banner */}
      <div className="alert alert-info" style={{ marginBottom: '1.5rem' }}>
        🛡️ <strong>Participant Data Protection Active:</strong> In compliance with security policy, participant personal data is strictly isolated and accessible solely by the verified faculty organizer and system administrator.
      </div>

      {/* Roster Controls */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--heading-color)' }}>Registered Participants Roster</h2>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Showing {filteredParticipants.length} of {participants.length} registered students
          </span>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <input
            type="text"
            className="form-input"
            placeholder="Search attendee by name, ID, or email..."
            value={searchFilter}
            onChange={(e) => setSearchFilter(e.target.value)}
            style={{ padding: '0.4rem 0.85rem', fontSize: '0.85rem', minWidth: '260px' }}
          />
          {participants.length > 0 && (
            <button type="button" className="btn btn-secondary btn-sm" onClick={handleExportCSV}>
              📥 Export CSV
            </button>
          )}
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '4rem 0', color: 'var(--text-muted)' }}>
          <p>Verifying permissions and fetching participant data...</p>
        </div>
      ) : participants.length === 0 ? (
        <div className="glass-card empty-state">
          <h3>No students registered yet</h3>
          <p style={{ marginTop: '0.5rem' }}>When students register, their names and details will appear here.</p>
        </div>
      ) : filteredParticipants.length === 0 ? (
        <div className="glass-card empty-state">
          <h3>No matching participants found</h3>
          <p style={{ marginTop: '0.5rem' }}>No student matched "{searchFilter}".</p>
          <button type="button" className="btn btn-outline btn-sm" onClick={() => setSearchFilter('')} style={{ marginTop: '0.75rem' }}>
            Clear Search
          </button>
        </div>
      ) : (
        <div className="table-container glass-card" style={{ padding: 0 }}>
          <table className="table">
            <thead>
              <tr>
                <th>Registration ID</th>
                <th>Student ID</th>
                <th>Student Full Name</th>
                <th>Institutional Email</th>
                <th>Registered Timestamp</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {filteredParticipants.map((p) => (
                <tr key={p.registration_id}>
                  <td><code>#REG-{p.registration_id.toString().padStart(4, '0')}</code></td>
                  <td><code>STU-{p.student_id.toString().padStart(3, '0')}</code></td>
                  <td><strong>{p.student_name}</strong></td>
                  <td>{p.student_email}</td>
                  <td style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                    {new Date(p.registered_at).toLocaleString()}
                  </td>
                  <td>
                    <span className="badge badge-confirmed">Confirmed</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
