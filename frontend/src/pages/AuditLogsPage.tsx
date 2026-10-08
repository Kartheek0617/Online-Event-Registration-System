import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';
import { AuditLog } from '../types';
import { Alert } from '../components/Alert';

export const AuditLogsPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState('');

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const data = await api.admin.auditLogs(200);
      setLogs(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch audit logs');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  const filteredLogs = logs.filter((log) => {
    if (!filter) return true;
    const term = filter.toLowerCase();
    return (
      log.action.toLowerCase().includes(term) ||
      (log.actor_name && log.actor_name.toLowerCase().includes(term)) ||
      (log.source_ip && log.source_ip.toLowerCase().includes(term)) ||
      log.result.toLowerCase().includes(term)
    );
  });

  return (
    <div className="container">
      <div style={{ marginBottom: '1.5rem' }}>
        <Link to="/admin" style={{ color: 'var(--primary-400)', fontSize: '0.9rem', display: 'inline-flex', alignItems: 'center', gap: '0.4rem', fontWeight: 600 }}>
          ← Back to Admin Console
        </Link>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.5rem' }}>
        <div>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', background: 'var(--bg-glass)', border: '1px solid var(--border-glass)', borderRadius: '999px', padding: '0.3rem 0.8rem', fontSize: '0.8rem', fontWeight: 600, color: 'var(--primary-400)', marginBottom: '0.75rem' }}>
            <span>📜 Tamper-Evident Ledger</span>
            <span>•</span>
            <span>Non-Repudiation Audit Logs</span>
          </div>
          <h1 style={{ fontSize: '2.25rem', fontWeight: 800, marginBottom: '0.5rem', color: 'var(--heading-color)', letterSpacing: '-0.02em' }}>
            Security Audit Logs
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '1rem', maxWidth: '680px' }}>
            Cryptographically trace actions, authorization attempts, security evaluations, and role escalations.
          </p>
        </div>
        <button type="button" className="btn btn-secondary btn-sm" onClick={fetchLogs}>
          🔄 Refresh Logs
        </button>
      </div>

      {error && <Alert type="danger" message={error} onClose={() => setError(null)} />}

      {/* Filter Bar */}
      <div className="glass-card" style={{ marginBottom: '1.5rem', padding: '1rem' }}>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap' }}>
          <div style={{ flex: '1 1 300px', position: 'relative' }}>
            <span style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }}>
              🔍
            </span>
            <input
              type="text"
              className="form-input"
              placeholder="Filter logs by Action, Actor Name, IP, or Result..."
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              style={{ width: '100%', paddingLeft: '2.5rem' }}
            />
          </div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Showing <strong>{filteredLogs.length}</strong> of <strong>{logs.length}</strong> events
          </div>
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '4rem 0', color: 'var(--text-muted)' }}>
          <p>Loading security audit logs...</p>
        </div>
      ) : filteredLogs.length === 0 ? (
        <div className="glass-card empty-state">
          <h3>No audit logs found</h3>
          <p style={{ marginTop: '0.5rem' }}>No records match your query.</p>
        </div>
      ) : (
        <div className="table-container glass-card" style={{ padding: 0 }}>
          <table className="table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Action</th>
                <th>Result</th>
                <th>Actor</th>
                <th>Entity Target</th>
                <th>IP Address</th>
                <th>Metadata</th>
              </tr>
            </thead>
            <tbody>
              {filteredLogs.map((log) => {
                const isSuccess = log.result === 'SUCCESS';
                const isDenied = log.result === 'DENIED';

                return (
                  <tr key={log.id}>
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td>
                      <code style={{ color: isDenied ? 'var(--warning)' : isSuccess ? 'var(--primary-400)' : 'var(--danger)', fontWeight: 600 }}>
                        {log.action}
                      </code>
                    </td>
                    <td>
                      <span className={`badge badge-${isSuccess ? 'success' : isDenied ? 'warning' : 'danger'}`}>
                        {log.result}
                      </span>
                    </td>
                    <td>
                      {log.actor_name ? (
                        <div>
                          <strong>{log.actor_name}</strong>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{log.actor_email}</div>
                        </div>
                      ) : (
                        <span style={{ color: 'var(--text-faint)' }}>Anonymous / Guest</span>
                      )}
                    </td>
                    <td>
                      <code>{log.entity_type}{log.entity_id ? `:#${log.entity_id}` : ''}</code>
                    </td>
                    <td style={{ fontSize: '0.85rem' }}>{log.source_ip || 'Internal'}</td>
                    <td style={{ fontSize: '0.75rem', maxWidth: '250px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {log.metadata_json || '-'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
