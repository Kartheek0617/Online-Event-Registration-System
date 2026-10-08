import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';
import { Event } from '../types';
import { Alert } from '../components/Alert';

const CATEGORIES = ['All', 'Cybersecurity', 'Artificial Intelligence', 'Web Engineering', 'Cultural', 'Symposium', 'Robotics'];

export const EventsListPage: React.FC = () => {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');

  const fetchEvents = async () => {
    setLoading(true);
    try {
      const data = await api.events.list({
        search: search.trim() || undefined,
        category: selectedCategory !== 'All' ? selectedCategory : undefined,
      });
      setEvents(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load events');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchEvents();
    }, 250);
    return () => clearTimeout(timer);
  }, [search, selectedCategory]);

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
      {/* Hero Header Section */}
      <div style={{ marginBottom: '2.5rem' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', background: 'var(--bg-glass)', border: '1px solid var(--border-glass)', borderRadius: '999px', padding: '0.35rem 0.9rem', fontSize: '0.8rem', fontWeight: 600, color: 'var(--primary-400)', marginBottom: '0.75rem' }}>
          <span>🏛️ Campus Event Portal</span>
          <span>•</span>
          <span>Verified Student & Faculty Events</span>
        </div>
        <h1 style={{ fontSize: '2.25rem', fontWeight: 800, marginBottom: '0.5rem', color: 'var(--heading-color)', letterSpacing: '-0.02em' }}>
          Explore Upcoming College Events
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '1.05rem', maxWidth: '750px', lineHeight: '1.6' }}>
          Discover and register for university hackathons, technical symposiums, research workshops, and cultural fests with live seat quota tracking.
        </p>
      </div>

      {error && <Alert type="danger" message={error} onClose={() => setError(null)} />}

      {/* Filter and Search Panel */}
      <div className="glass-card" style={{ marginBottom: '2rem', padding: '1.25rem' }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
          {/* Search Bar */}
          <div style={{ flex: '1 1 320px', position: 'relative' }}>
            <span style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)', fontSize: '1rem' }}>
              🔍
            </span>
            <input
              type="text"
              className="form-input"
              placeholder="Search by event title, keyword, or venue..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ width: '100%', paddingLeft: '2.5rem' }}
              aria-label="Search events"
            />
            {search && (
              <button
                type="button"
                onClick={() => setSearch('')}
                style={{ position: 'absolute', right: '0.75rem', top: '50%', transform: 'translateY(-50%)', background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '1rem' }}
                aria-label="Clear search"
              >
                ✕
              </button>
            )}
          </div>

          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Showing <strong>{events.length}</strong> {events.length === 1 ? 'event' : 'events'}
          </div>
        </div>

        {/* Category Filter Pills (Preserves All Categories) */}
        <div>
          <div style={{ fontSize: '0.78rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-faint)', marginBottom: '0.6rem' }}>
            Filter by Category / Department:
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }} role="group" aria-label="Filter events by category">
            {CATEGORIES.map((cat) => (
              <button
                key={cat}
                type="button"
                className={`category-pill ${selectedCategory === cat ? 'active' : ''}`}
                onClick={() => setSelectedCategory(cat)}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Loading & Event Grid */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '5rem 0', color: 'var(--text-muted)' }}>
          <div style={{ display: 'inline-block', width: '32px', height: '32px', border: '3px solid var(--border-glass)', borderTopColor: 'var(--primary-500)', borderRadius: '50%', animation: 'spin 0.8s linear infinite', marginBottom: '1rem' }} />
          <p>Loading campus events...</p>
          <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
        </div>
      ) : events.length === 0 ? (
        <div className="glass-card empty-state">
          <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>📅</div>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--heading-color)' }}>No matching events found</h3>
          <p style={{ marginTop: '0.5rem', color: 'var(--text-muted)' }}>
            No events match your current search terms or category selection. Try clearing filters or searching another keyword.
          </p>
          {(search || selectedCategory !== 'All') && (
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => { setSearch(''); setSelectedCategory('All'); }}
              style={{ marginTop: '1.25rem' }}
            >
              Reset Filters
            </button>
          )}
        </div>
      ) : (
        <div className="grid-cards">
          {events.map((ev) => {
            const isFull = ev.available_seats <= 0;
            const isClosed = ev.status === 'CLOSED';
            const percentFilled = Math.min(100, Math.round(((ev.participant_limit - ev.available_seats) / ev.participant_limit) * 100));

            return (
              <div
                key={ev.id}
                className="glass-card interactive-card"
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  padding: '1.5rem',
                }}
              >
                <div>
                  {/* Top Header Tags */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.85rem' }}>
                    <span className={`badge ${getCategoryBadgeClass(ev.category)}`}>
                      {ev.category}
                    </span>
                    {isClosed ? (
                      <span className="badge badge-closed">Closed</span>
                    ) : isFull ? (
                      <span className="badge badge-warning">Full ({ev.participant_limit}/{ev.participant_limit})</span>
                    ) : (
                      <span className="badge badge-open">Open</span>
                    )}
                  </div>

                  {/* Title */}
                  <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.65rem', color: 'var(--heading-color)', lineHeight: '1.35' }}>
                    {ev.title}
                  </h3>

                  {/* Description */}
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.885rem', marginBottom: '1.25rem', lineHeight: '1.55' }}>
                    {ev.description.length > 120 ? `${ev.description.substring(0, 120)}...` : ev.description}
                  </p>
                </div>

                {/* Logistics & Footer Section */}
                <div style={{ borderTop: '1px solid var(--border-glass)', paddingTop: '1.15rem', marginTop: '0.5rem' }}>
                  {/* Event Metadata Grid */}
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.65rem', fontSize: '0.825rem', color: 'var(--text-muted)', marginBottom: '1.15rem' }}>
                    <div>
                      📅 <strong style={{ color: 'var(--text-main)' }}>{ev.event_date}</strong>
                    </div>
                    <div>
                      ⏰ <strong style={{ color: 'var(--text-main)' }}>{ev.start_time} - {ev.end_time}</strong>
                    </div>
                    <div>
                      📍 <strong style={{ color: 'var(--text-main)' }}>{ev.venue}</strong>
                    </div>
                    <div>
                      👤 <strong style={{ color: 'var(--text-main)' }}>{ev.organizer_name || 'Coordinator'}</strong>
                    </div>
                  </div>

                  {/* Seat Quota & Progress Bar */}
                  <div style={{ marginBottom: '1.15rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: '0.35rem' }}>
                      <span style={{ color: 'var(--text-muted)' }}>Seat Capacity:</span>
                      <strong style={{ color: isFull ? 'var(--danger)' : isClosed ? 'var(--text-muted)' : 'var(--success)' }}>
                        {isFull ? '0 Seats Left' : `${ev.available_seats} of ${ev.participant_limit} seats left`}
                      </strong>
                    </div>
                    <div style={{ height: '6px', background: 'var(--border-glass)', borderRadius: '999px', overflow: 'hidden' }}>
                      <div
                        style={{
                          height: '100%',
                          width: `${percentFilled}%`,
                          background: isFull
                            ? 'var(--danger)'
                            : percentFilled > 80
                            ? 'var(--warning)'
                            : 'linear-gradient(90deg, #6366f1, #10b981)',
                          transition: 'width 0.3s ease',
                        }}
                      />
                    </div>
                  </div>

                  {/* Primary Link Button */}
                  <Link
                    to={`/events/${ev.id}`}
                    className="btn btn-primary"
                    style={{ width: '100%' }}
                  >
                    View Details & Register →
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
