import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import { AuthProvider } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { ProtectedRoute } from './components/ProtectedRoute';

// Pages
import { LoginPage } from './pages/LoginPage';
import { EventsListPage } from './pages/EventsListPage';
import { EventDetailPage } from './pages/EventDetailPage';
import { StudentDashboard } from './pages/StudentDashboard';
import { MyRegistrationsPage } from './pages/MyRegistrationsPage';
import { FacultyDashboard } from './pages/FacultyDashboard';
import { CreateEventPage } from './pages/CreateEventPage';
import { ManageEventsPage } from './pages/ManageEventsPage';
import { EventParticipantsPage } from './pages/EventParticipantsPage';
import { AdminDashboard } from './pages/AdminDashboard';
import { AuditLogsPage } from './pages/AuditLogsPage';

export const App: React.FC = () => {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
            <Navbar />
            <main style={{ flex: 1, paddingBottom: '3rem' }}>
              <Routes>
                {/* Public Routes */}
                <Route path="/" element={<Navigate to="/events" replace />} />
                <Route path="/events" element={<EventsListPage />} />
                <Route path="/events/:id" element={<EventDetailPage />} />
                <Route path="/login" element={<LoginPage />} />

                {/* Student Routes */}
                <Route
                  path="/student"
                  element={
                    <ProtectedRoute allowedRoles={['STUDENT', 'ADMIN']}>
                      <StudentDashboard />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/my-registrations"
                  element={
                    <ProtectedRoute allowedRoles={['STUDENT', 'ADMIN']}>
                      <MyRegistrationsPage />
                    </ProtectedRoute>
                  }
                />

                {/* Faculty Routes */}
                <Route
                  path="/faculty"
                  element={
                    <ProtectedRoute allowedRoles={['FACULTY', 'ADMIN']}>
                      <FacultyDashboard />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/create-event"
                  element={
                    <ProtectedRoute allowedRoles={['FACULTY', 'ADMIN']}>
                      <CreateEventPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/manage-events"
                  element={
                    <ProtectedRoute allowedRoles={['FACULTY', 'ADMIN']}>
                      <ManageEventsPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/events/:id/participants"
                  element={
                    <ProtectedRoute allowedRoles={['FACULTY', 'ADMIN']}>
                      <EventParticipantsPage />
                    </ProtectedRoute>
                  }
                />

                {/* Admin Routes */}
                <Route
                  path="/admin"
                  element={
                    <ProtectedRoute allowedRoles={['ADMIN']}>
                      <AdminDashboard />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/admin/audit-logs"
                  element={
                    <ProtectedRoute allowedRoles={['ADMIN']}>
                      <AuditLogsPage />
                    </ProtectedRoute>
                  }
                />

                {/* Fallback */}
                <Route
                  path="*"
                  element={
                    <div className="container" style={{ textAlign: 'center', padding: '5rem 0' }}>
                      <h2>404 - Page Not Found</h2>
                      <p style={{ color: 'var(--text-muted)', margin: '1rem 0' }}>The requested page does not exist.</p>
                      <a href="/events" className="btn btn-primary">Return to Events</a>
                    </div>
                  }
                />
              </Routes>
            </main>

            <footer style={{ borderTop: '1px solid var(--border-glass)', padding: '1.5rem', textAlign: 'center', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              <p>
                🔒 Secure Software Engineering Laboratory Project — Online Event Registration System | RBAC & Data Protection
              </p>
            </footer>
          </div>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
};
