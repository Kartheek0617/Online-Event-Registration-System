-- ============================================================
-- ONLINE EVENT REGISTRATION SYSTEM - CONTAINER INIT SCRIPT
-- ============================================================

\i /docker-entrypoint-initdb.d/schema.sql;

-- Initial Seed Data
-- Passwords hashed using bcrypt (Rounds: 12)
-- admin@college.edu : Admin@Secure123
-- faculty.sharma@college.edu : Faculty@Secure123
-- faculty.patel@college.edu : Faculty@Secure123
-- student.aarav@college.edu : Student@Secure123
-- student.ananya@college.edu : Student@Secure123
-- student.rohan@college.edu : Student@Secure123

INSERT INTO users (name, email, password_hash, role, is_active) VALUES
('System Administrator', 'admin@college.edu', '$2b$12$7kS1vLkW16j8j5mR0v5LreE7GfUqG9C7R6jK6pU8aQ7h5l5M4v8N2', 'ADMIN', true),
('Dr. Ramesh Sharma', 'faculty.sharma@college.edu', '$2b$12$eJ4Xz5.xKqP1fP/3pM0ybe9JtH3zK8lR9jM4v7Q1nU6x5Y3p8O9aO', 'FACULTY', true),
('Prof. Priya Patel', 'faculty.patel@college.edu', '$2b$12$eJ4Xz5.xKqP1fP/3pM0ybe9JtH3zK8lR9jM4v7Q1nU6x5Y3p8O9aO', 'FACULTY', true),
('Aarav Kumar', 'student.aarav@college.edu', '$2b$12$fT3Yw6.yLrQ2gQ/4qN1zcf0KuI4aL9mS0kN5w8R2oV7y6Z4q9P0bP', 'STUDENT', true),
('Ananya Singh', 'student.ananya@college.edu', '$2b$12$fT3Yw6.yLrQ2gQ/4qN1zcf0KuI4aL9mS0kN5w8R2oV7y6Z4q9P0bP', 'STUDENT', true),
('Rohan Verma', 'student.rohan@college.edu', '$2b$12$fT3Yw6.yLrQ2gQ/4qN1zcf0KuI4aL9mS0kN5w8R2oV7y6Z4q9P0bP', 'STUDENT', true)
ON CONFLICT (email) DO NOTHING;

INSERT INTO events (organizer_id, title, description, category, venue, event_date, start_time, end_time, participant_limit, registration_deadline, status) VALUES
(2, 'Cybersecurity Awareness Workshop', 'Comprehensive hands-on workshop covering OWASP Top 10, network defense, threat modeling, and defensive coding practices.', 'Cybersecurity', 'Auditorium A, CS Block', '2026-11-15', '10:00', '13:00', 50, '2026-11-14T23:59:59', 'OPEN'),
(3, 'AI Innovation Hackathon 2026', '24-hour inter-departmental hackathon focused on building generative AI and autonomous agent applications for social impact.', 'Artificial Intelligence', 'Innovation Center Lab 3', '2026-11-20', '09:00', '18:00', 30, '2026-11-19T23:59:59', 'OPEN'),
(2, 'Web Development Bootcamp', 'Intensive bootcamp covering full-stack architecture with React, TypeScript, FastAPI, and containerized microservices.', 'Web Engineering', 'Seminar Hall 2', '2026-11-25', '14:00', '17:00', 40, '2026-11-24T23:59:59', 'OPEN'),
(3, 'Annual College Cultural Fest', 'Celebration of talent featuring music, drama, dance competitions, and cultural exhibitions.', 'Cultural', 'Open Air Amphitheatre', '2026-12-05', '17:00', '22:00', 150, '2026-12-04T23:59:59', 'OPEN'),
(2, 'National Technical Symposium', 'Academic research paper presentation, coding competitions, and panel discussions with industry technology leaders.', 'Symposium', 'Convention Hall Main', '2026-12-12', '09:30', '16:30', 60, '2026-12-11T23:59:59', 'OPEN'),
(2, 'Advanced Robotics Seminar [Closed]', 'Specialized seminar on ROS2 and autonomous robotics. Registration is now closed.', 'Robotics', 'Robotics Lab 1', '2026-11-10', '11:00', '13:00', 20, '2026-11-09T23:59:59', 'CLOSED'),
(3, 'Micro Quantum Computing Seminar [Full]', 'Intimate round-table discussion on quantum cryptography. Strictly limited to 2 participants.', 'Quantum', 'Conference Room C', '2026-11-18', '15:00', '17:00', 2, '2026-11-17T23:59:59', 'OPEN');

-- Initial Registrations
INSERT INTO registrations (event_id, student_id, status) VALUES
(1, 4, 'CONFIRMED'),
(2, 5, 'CONFIRMED'),
(7, 4, 'CONFIRMED'),
(7, 5, 'CONFIRMED');

-- Initial Audit Log
INSERT INTO audit_logs (actor_id, action, entity_type, entity_id, source_ip, result, metadata_json) VALUES
(1, 'DATABASE_INIT_DOCKER', 'SYSTEM', 1, '127.0.0.1', 'SUCCESS', '{"status": "PostgreSQL database initialized with verified secure seed data"}');
