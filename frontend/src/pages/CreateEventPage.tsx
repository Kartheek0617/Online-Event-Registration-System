import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../services/api';
import { Alert } from '../components/Alert';

export const CreateEventPage: React.FC = () => {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: 'Technology',
    venue: '',
    event_date: '',
    start_time: '10:00',
    end_time: '13:00',
    participant_limit: 30,
    registration_deadline: '',
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'participant_limit' ? parseInt(value, 10) || 0 : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Client-side validation checks
    if (!formData.title.trim()) {
      setError('Event title is required');
      return;
    }
    if (formData.participant_limit <= 0) {
      setError('Participant limit must be greater than zero');
      return;
    }
    if (!formData.event_date) {
      setError('Event date is required');
      return;
    }

    setLoading(true);
    try {
      const deadline = formData.registration_deadline || `${formData.event_date}T23:59:59`;
      await api.events.create({
        ...formData,
        registration_deadline: deadline,
      });
      navigate('/faculty');
    } catch (err: any) {
      setError(err.message || 'Failed to create event');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container" style={{ maxWidth: '780px' }}>
      <div style={{ marginBottom: '1.5rem' }}>
        <Link to="/faculty" style={{ color: 'var(--primary-400)', fontSize: '0.9rem', display: 'inline-flex', alignItems: 'center', gap: '0.4rem' }}>
          ← Back to Faculty Hub
        </Link>
      </div>

      <div className="glass-card" style={{ padding: '2.5rem' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', background: 'var(--bg-glass)', border: '1px solid var(--border-glass)', borderRadius: '999px', padding: '0.3rem 0.8rem', fontSize: '0.8rem', fontWeight: 600, color: 'var(--primary-400)', marginBottom: '0.75rem' }}>
          <span>🏛️ Faculty Publishing</span>
          <span>•</span>
          <span>Event Creation Form</span>
        </div>
        <h1 style={{ fontSize: '1.85rem', fontWeight: 800, marginBottom: '0.5rem', color: 'var(--heading-color)', letterSpacing: '-0.02em' }}>
          Create New College Event
        </h1>
        <p style={{ color: 'var(--text-muted)', marginBottom: '2rem', fontSize: '0.95rem' }}>
          Publish a new campus seminar, workshop, or competition with enforced participant capacity.
        </p>

        {error && <Alert type="danger" message={error} onClose={() => setError(null)} />}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="title">Event Title *</label>
            <input
              id="title"
              name="title"
              type="text"
              className="form-input"
              value={formData.title}
              onChange={handleChange}
              placeholder="e.g. Distributed Systems & Microservices Workshop"
              required
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label" htmlFor="category">Category *</label>
              <select
                id="category"
                name="category"
                className="form-select"
                value={formData.category}
                onChange={handleChange}
                required
              >
                <option value="Cybersecurity">Cybersecurity</option>
                <option value="Artificial Intelligence">Artificial Intelligence</option>
                <option value="Web Engineering">Web Engineering</option>
                <option value="Cloud & DevOps">Cloud & DevOps</option>
                <option value="Cultural">Cultural</option>
                <option value="Symposium">Symposium</option>
                <option value="Robotics">Robotics</option>
                <option value="General">General</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="participant_limit">Participant Limit (Max Seats) *</label>
              <input
                id="participant_limit"
                name="participant_limit"
                type="number"
                min="1"
                max="5000"
                className="form-input"
                value={formData.participant_limit}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="venue">Venue / Location *</label>
            <input
              id="venue"
              name="venue"
              type="text"
              className="form-input"
              value={formData.venue}
              onChange={handleChange}
              placeholder="e.g. CS Seminar Hall 3 / Virtual Zoom Link"
              required
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label" htmlFor="event_date">Event Date *</label>
              <input
                id="event_date"
                name="event_date"
                type="date"
                className="form-input"
                value={formData.event_date}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="start_time">Start Time *</label>
              <input
                id="start_time"
                name="start_time"
                type="time"
                className="form-input"
                value={formData.start_time}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="end_time">End Time *</label>
              <input
                id="end_time"
                name="end_time"
                type="time"
                className="form-input"
                value={formData.end_time}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="description">Event Description *</label>
            <textarea
              id="description"
              name="description"
              className="form-textarea"
              value={formData.description}
              onChange={handleChange}
              placeholder="Provide agenda, prerequisites, learning outcomes, and schedule..."
              rows={4}
              required
            />
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', marginTop: '1.5rem' }}>
            <Link to="/faculty" className="btn btn-outline">Cancel</Link>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Creating event...' : 'Publish Event'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
