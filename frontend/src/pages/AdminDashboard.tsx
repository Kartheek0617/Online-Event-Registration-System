import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';
import { User, SystemStats, Event } from '../types';
import { Alert } from '../components/Alert';
import { Modal } from '../components/Modal';

export const AdminDashboard: React.FC = () => {
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const [roleChangeTarget, setRoleChangeTarget] = useState<{ user: User; newRole: string } | null>(null);
  const [updatingRole, setUpdatingRole] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [statsData, usersData, eventsData] = await Promise.all([
        api.admin.stats(),
        api.admin.users(),
        api.admin.events(),
      ]);
      setStats(statsData);
      setUsers(usersData);
      setEvents(eventsData);
    } catch (err: any) {
      setError(err.message || 'Failed to load administration data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const confirmRoleChange = async () => {
    if (!roleChangeTarget) return;
    setUpdatingRole(true);
    setError(null);
    try {
      await api.admin.updateRole(roleChangeTarget.user.id, roleChangeTarget.newRole);
      setSuccessMsg(`Role for ${roleChangeTarget.user.name} updated to ${roleChangeTarget.newRole}.`);
      setRoleChangeTarget(null);
      await loadData();
    } catch (err: any) {
      setError(err.message || 'Failed to update user role');
    } finally {
      setUpdatingRole(false);
    }
  };

  return (
    <div className="container">
      {/* Admin Title */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '2rem' }}>
        <div>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', background: 'var(--bg-glass)', border: '1px solid var(--border-glass)', borderRadius: '999px', padding: '0.3rem 0.8rem', fontSize: '0.8rem', fontWeight: 600, color: 'var(--primary-400)', marginBottom: '0.75rem' }}>
            <span>🛡️ System Administration</span>
            <span>•</span>
            <span>Institutional Governance</span>
          </div>
          <h1 style={{ fontSize: '2.25rem', fontWeight: 800, marginBottom: '0.5rem', color: 'var(--heading-color)', letterSpacing: '-0.02em' }}>
            System Administration Console
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '1rem', maxWidth: '680px' }}>
            Supervisory oversight of accounts, role assignments, event records, capacity metrics, and security audit logs.
          </p>
        </div>
        <Link to="/admin/audit-logs" className="btn btn-secondary">
          📜 View Security Audit Logs →
        </Link>
      </div>

      {error && <Alert type="danger" message={error} onClose={() => setError(null)} />}
      {successMsg && <Alert type="success" message={successMsg} onClose={() => setSuccessMsg(null)} />}

      {/* System Statistics Cards */}
      {stats && (
        <div className="grid-stats">
          <div className="glass-card">
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Total Users
            </span>
            <p style={{ fontSize: '2.25rem', fontWeight: 800, color: 'var(--primary-400)', marginTop: '0.25rem' }}>
              {stats.total_users}
            </p>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
              👨‍🎓 {stats.total_students} Students | 👨‍🏫 {stats.total_faculty} Faculty
            </div>
          </div>

          <div className="glass-card">
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Total Events
            </span>
            <p style={{ fontSize: '2.25rem', fontWeight: 800, color: 'var(--info)', marginTop: '0.25rem' }}>
              {stats.total_events}
            </p>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
              ⚡ {stats.active_events} Currently Active
            </div>
          </div>

          <div className="glass-card">
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Confirmed Registrations
            </span>
            <p style={{ fontSize: '2.25rem', fontWeight: 800, color: 'var(--success)', marginTop: '0.25rem' }}>
              {stats.confirmed_registrations}
            </p>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
              Total Records: {stats.total_registrations}
            </div>
          </div>

          <div className="glass-card">
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Security Audit Events
            </span>
            <p style={{ fontSize: '2.25rem', fontWeight: 800, color: 'var(--warning)', marginTop: '0.25rem' }}>
              {stats.total_audit_logs}
            </p>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
              Non-Repudiation Logs Captured
            </div>
          </div>
        </div>
      )}

      {/* User Management Section */}
      <div className="glass-card" style={{ marginBottom: '2.5rem', padding: 0, overflow: 'hidden' }}>
        <div style={{ padding: '1.25rem 1.5rem', borderBottom: '1px solid var(--border-glass)' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700 }}>User Management & RBAC Roles</h2>
        </div>

        <div className="table-container" style={{ border: 'none' }}>
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Full Name</th>
                <th>Institutional Email</th>
                <th>Current Role</th>
                <th>Status</th>
                <th>Assign Role</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td><code>USR-{u.id.toString().padStart(3, '0')}</code></td>
                  <td><strong>{u.name}</strong></td>
                  <td>{u.email}</td>
                  <td>
                    <span className={`badge badge-${u.role.toLowerCase()}`}>
                      {u.role}
                    </span>
                  </td>
                  <td>
                    <span style={{ color: u.is_active ? 'var(--success)' : 'var(--danger)', fontSize: '0.85rem' }}>
                      {u.is_active ? '● Active' : '○ Inactive'}
                    </span>
                  </td>
                  <td>
                    <select
                      className="form-select"
                      style={{ padding: '0.3rem 0.6rem', fontSize: '0.85rem' }}
                      value={u.role}
                      onChange={(e) => setRoleChangeTarget({ user: u, newRole: e.target.value })}
                    >
                      <option value="STUDENT">STUDENT</option>
                      <option value="FACULTY">FACULTY</option>
                      <option value="ADMIN">ADMIN</option>
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Role Change Confirmation Modal */}
      <Modal
        isOpen={!!roleChangeTarget}
        onClose={() => setRoleChangeTarget(null)}
        title="Confirm User Role Elevation / Change"
        footer={
          <>
            <button
              type="button"
              className="btn btn-outline btn-sm"
              onClick={() => setRoleChangeTarget(null)}
              disabled={updatingRole}
            >
              Cancel
            </button>
            <button
              type="button"
              className="btn btn-primary btn-sm"
              onClick={confirmRoleChange}
              disabled={updatingRole}
            >
              {updatingRole ? 'Updating...' : 'Confirm Role Change'}
            </button>
          </>
        }
      >
        <p style={{ marginBottom: '1rem' }}>
          Are you sure you want to change the role of <strong>{roleChangeTarget?.user.name}</strong> from{' '}
          <code>{roleChangeTarget?.user.role}</code> to <code>{roleChangeTarget?.newRole}</code>?
        </p>
        <p style={{ fontSize: '0.85rem', color: 'var(--warning)' }}>
          ⚠️ This action will immediately adjust the user's system privileges and generate a security audit log.
        </p>
      </Modal>
    </div>
  );
};
