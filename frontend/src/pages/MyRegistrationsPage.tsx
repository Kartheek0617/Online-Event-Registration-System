import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';
import { Registration } from '../types';
import { Alert } from '../components/Alert';
import { Modal } from '../components/Modal';

export const MyRegistrationsPage: React.FC = () => {
  const [registrations, setRegistrations] = useState<Registration[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const [cancelTarget, setCancelTarget] = useState<Registration | null>(null);
  const [cancelling, setCancelling] = useState(false);

  const fetchRegistrations = async () => {
    setLoading(true);
    try {
      const data = await api.registrations.myRegistrations();
      setRegistrations(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch registrations');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRegistrations();
  }, []);

  const handleCancelRegistration = async () => {
    if (!cancelTarget) return;
    setCancelling(true);
    setError(null);
    try {
      const res = await api.registrations.cancel(cancelTarget.id);
      setSuccessMsg(res.message);
      setCancelTarget(null);
      await fetchRegistrations();
    } catch (err: any) {
      setError(err.message || 'Failed to cancel registration');
    } finally {
      setCancelling(false);
    }
  };

  return (
    <div className="container">
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', background: 'var(--bg-glass)', border: '1px solid var(--border-glass)', borderRadius: '999px', padding: '0.3rem 0.8rem', fontSize: '0.8rem', fontWeight: 600, color: 'var(--primary-400)', marginBottom: '0.75rem' }}>
          <span>📋 Student Registrations</span>
          <span>•</span>
          <span>Verified Event Passes</span>
        </div>
        <h1 style={{ fontSize: '2.25rem', fontWeight: 800, marginBottom: '0.5rem', color: 'var(--heading-color)', letterSpacing: '-0.02em' }}>
          My Event Registrations
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '1rem', maxWidth: '680px' }}>
          Manage your confirmed event registrations, view schedule logistics, and cancel reservations if your plans change.
        </p>
      </div>

      {error && <Alert type="danger" message={error} onClose={() => setError(null)} />}
      {successMsg && <Alert type="success" message={successMsg} onClose={() => setSuccessMsg(null)} />}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '4rem 0', color: 'var(--text-muted)' }}>
          <p>Loading your registrations...</p>
        </div>
      ) : registrations.length === 0 ? (
        <div className="glass-card empty-state">
          <h3>No Registrations Yet</h3>
          <p style={{ marginTop: '0.5rem', marginBottom: '1.5rem' }}>
            You have not registered for any events yet. Explore upcoming campus events!
          </p>
          <Link to="/events" className="btn btn-primary">Browse Events Now</Link>
        </div>
      ) : (
        <div className="table-container glass-card" style={{ padding: 0 }}>
          <table className="table">
            <thead>
              <tr>
                <th>Registration ID</th>
                <th>Event Title</th>
                <th>Date & Venue</th>
                <th>Registered At</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {registrations.map((reg) => {
                const isConfirmed = reg.status === 'CONFIRMED';
                return (
                  <tr key={reg.id}>
                    <td>
                      <code>#REG-{reg.id.toString().padStart(4, '0')}</code>
                    </td>
                    <td>
                      <strong>
                        <Link to={`/events/${reg.event_id}`} style={{ color: 'var(--text-main)', textDecoration: 'underline' }}>
                          {reg.event_title || `Event #${reg.event_id}`}
                        </Link>
                      </strong>
                    </td>
                    <td>
                      <div>📅 {reg.event_date}</div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>📍 {reg.venue}</div>
                    </td>
                    <td style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                      {new Date(reg.registered_at).toLocaleString()}
                    </td>
                    <td>
                      <span className={`badge badge-${isConfirmed ? 'confirmed' : 'cancelled'}`}>
                        {reg.status}
                      </span>
                    </td>
                    <td>
                      {isConfirmed ? (
                        <button
                          type="button"
                          className="btn btn-danger btn-sm"
                          onClick={() => setCancelTarget(reg)}
                        >
                          Cancel
                        </button>
                      ) : (
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-faint)' }}>Cancelled</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Cancellation Confirmation Modal */}
      <Modal
        isOpen={!!cancelTarget}
        onClose={() => setCancelTarget(null)}
        title="Confirm Registration Cancellation"
        footer={
          <>
            <button
              type="button"
              className="btn btn-outline btn-sm"
              onClick={() => setCancelTarget(null)}
              disabled={cancelling}
            >
              Keep Registration
            </button>
            <button
              type="button"
              className="btn btn-danger btn-sm"
              onClick={handleCancelRegistration}
              disabled={cancelling}
            >
              {cancelling ? 'Cancelling...' : 'Yes, Cancel Registration'}
            </button>
          </>
        }
      >
        <p style={{ marginBottom: '1rem' }}>
          Are you sure you want to cancel your registration for{' '}
          <strong>{cancelTarget?.event_title}</strong>?
        </p>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
          Your seat will be immediately released for other students to register.
        </p>
      </Modal>
    </div>
  );
};
