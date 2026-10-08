# Phase 2: Software Requirements Specification (SRS)

## 1. Introduction & Domain Purpose

### 1.1 Purpose
The **Online Event Registration System (EventHub)** is an enterprise-grade web application engineered for college campus event coordination. The system provides role-based workflows for prospective attendees (Students and Guests), event creators (Faculty coordinators), and administrative overseers (System Administrators). Security is treated as an architectural foundation to prevent unauthorized registrations, overbooking race conditions, object privilege escalation, and participant data harvesting.

### 1.2 Scope
The system encompasses student registration workflows, faculty event lifecycle management, administrative oversight, and a comprehensive security audit subsystem. It operates as a modern distributed web application consisting of a React single-page application frontend, a FastAPI REST backend, and a PostgreSQL relational database.

---

## 2. System Stakeholders & User Roles

| Role Identifier | Role Name | System Access Rights & Boundaries |
| :--- | :--- | :--- |
| **ACT-01** | **GUEST** | Unauthenticated public visitor. Can browse published events, search keywords, and inspect event descriptions/venues. Cannot register or view participant rosters. |
| **ACT-02** | **STUDENT** | Authenticated campus participant. Can browse events, register for open events, cancel their own registrations, and inspect personal registration history. Strictly prohibited from creating events or viewing other students' registrations. |
| **ACT-03** | **FACULTY** | Authenticated event coordinator. Can create campus events, specify participant caps, view confirmed participant rosters *only for events they organized*, and close registration. Cannot alter other faculty members' events. |
| **ACT-04** | **ADMIN** | System administrator. Holds supervisory authority to oversee all campus events, update user roles, inspect audit logs, and monitor system metrics. Administrative privileges are strictly barred from student/faculty roles. |
| **SYS-01** | **DATABASE** | Relational data persistence engine (PostgreSQL 16) enforcing ACID transactions, row-level locks, and unique constraints. |
| **SYS-02** | **AUDIT SUBSYSTEM** | Tamper-evident recording engine capturing security events, authorization denials, and lifecycle operations for non-repudiation. |

---

## 3. Assumptions, Constraints & Dependencies

### 3.1 Assumptions
1. All students and faculty possess institutional credentials and access the system via modern web browsers supporting ES6+ and secure cookies.
2. The server host maintains accurate network time synchronization (NTP) for deterministic JWT expiration and audit timestamp validity.

### 3.2 Constraints
1. **Zero-Token Storage:** Authentication tokens must not be persisted in browser `localStorage` or `sessionStorage` due to XSS vulnerability exposure.
2. **Deterministic Concurrency:** Event capacity caps must never be breached, even under concurrent registration attempts.
3. **Execution Runtime:** Backend must execute under non-root unprivileged service accounts (`uid: 10001`).

### 3.3 Dependencies
- PostgreSQL 16 (Relational storage with row locking and partial unique indexes)
- Python 3.11 with FastAPI, Pydantic v2, and SQLAlchemy 2.0
- React 18 with Vite, React Router v6, and TypeScript

---

## 4. Functional Requirements (FR)

| Req ID | Requirement Description | Actor | Priority |
| :--- | :--- | :--- | :--- |
| **FR-01** | **View Available Events:** The system shall permit all users (including unauthenticated Guests) to browse and filter open events. | Guest, Student, Faculty, Admin | Must Have |
| **FR-02** | **View Event Details:** The system shall display comprehensive event metadata including title, description, venue, schedule, and available seat quotas. | Guest, Student, Faculty, Admin | Must Have |
| **FR-03** | **Register for Event:** The system shall allow authenticated Students to register for events that are open, within deadline, and have available seats. | Student | Must Have |
| **FR-04** | **Cancel Registration:** The system shall permit authenticated Students to cancel only their own active registrations and immediately restore seat capacity. | Student | Must Have |
| **FR-05** | **View Personal Registrations:** The system shall allow Students to view only their own active and historical registrations. | Student | Must Have |
| **FR-06** | **Create Event:** The system shall allow authenticated Faculty to create campus events with title, description, venue, schedule, category, and participant limit. | Faculty, Admin | Must Have |
| **FR-07** | **Set Participant Limit:** The system shall require event organizers to establish positive integer participant limits and registration deadlines. | Faculty, Admin | Must Have |
| **FR-08** | **View Registered Participants:** The system shall allow Faculty members to view registered participant lists *strictly for events they created*. | Faculty, Admin | Must Have |
| **FR-09** | **Close Registration:** The system shall allow event organizers to close registration for their events prior to the event date. | Faculty, Admin | Must Have |
| **FR-10** | **Authentication & Session:** The system shall provide secure login, identity retrieval (`/api/auth/me`), and logout endpoints. | Student, Faculty, Admin | Must Have |
| **FR-11** | **Admin Oversight:** The system shall provide an administrative dashboard displaying all registered users, campus events, and aggregate system metrics. | Admin | Must Have |
| **FR-12** | **Health Reporting:** The system shall expose a `/health` endpoint reporting database and application readiness for container orchestrators. | System | Must Have |

---

## 5. Non-Functional Requirements (NFR)

| NFR ID | Category | Requirement Specification | Priority |
| :--- | :--- | :--- | :--- |
| **NFR-01** | **Performance** | API endpoint latency under normal load shall be $< 150\text{ ms}$ for $95\text{th}$ percentile requests; database queries must leverage indexes on foreign keys. | Must Have |
| **NFR-02** | **Availability** | The system shall maintain $\ge 99.9\%$ operational uptime backed by container health probes and automated restart policies. | Must Have |
| **NFR-03** | **Reliability** | Database connection pooling with auto-reconnect and graceful error handling ensuring zero implementation stack traces are leaked to clients. | Must Have |
| **NFR-04** | **Usability** | The web interface shall feature a responsive, high-contrast, accessible UI compliant with WCAG 2.1 AA standards and keyboard navigation. | Must Have |
| **NFR-05** | **Maintainability** | The backend shall adhere to a clean layered architecture (API $\rightarrow$ Security $\rightarrow$ Service $\rightarrow$ ORM $\rightarrow$ PostgreSQL) with $> 85\%$ test coverage. | Must Have |
| **NFR-06** | **Scalability** | Registration processing must remain concurrency-safe under high-volume bursts using row-level transactional locking. | Must Have |

---

## 6. Security Requirements Specification (SR)

| Security ID | Domain | Requirement Specification | Priority |
| :--- | :--- | :--- | :--- |
| **SR-01** | **Secure Authentication** | Passwords must be hashed using Bcrypt with salt cost factor 12 (cost factor 4 for test environments). Login must enforce rate limiting (5 attempts/min). | Must Have |
| **SR-02** | **Role-Based Authorization** | Strict RBAC enforced at the API layer using dependency injection (`require_roles`). Students/Faculty cannot execute administrative actions. | Must Have |
| **SR-03** | **Object-Level Authorization** | Server-side validation must ensure actors only operate on records they own (`event.organizer_id == user.id` or `reg.student_id == user.id`). Mitigates IDOR/BOLA. | Must Have |
| **SR-04** | **Unauthorized Registration Prevention** | Guests and Faculty are strictly barred from registering for events; only authenticated users with the `STUDENT` role may register. | Must Have |
| **SR-05** | **Duplicate Registration Prevention** | The database and service layer must guarantee zero duplicate active registrations via a partial unique index (`uq_event_student_active`). | Must Have |
| **SR-06** | **Participant Data Protection** | Student participant rosters are isolated to event creators and system admins; participant emails and identities must not be exposed to unauthorized users. | Must Have |
| **SR-07** | **Secure Session/Token Handling** | JWT tokens are issued exclusively into `HttpOnly`, `SameSite=Lax`, `Secure` cookies. JavaScript cannot access tokens; logout invalidates the cookie immediately. | Must Have |
| **SR-08** | **Input Validation** | All client inputs must be validated via strict Pydantic v2 schemas; negative participant limits, invalid dates, and malformed strings are rejected with HTTP 422. | Must Have |
| **SR-09** | **Audit Logging** | An immutable audit log records all security-relevant actions (`LOGIN_SUCCESS`, `LOGIN_FAILURE`, `EVENT_REGISTER`, `REGISTRATION_CANCEL`, `UNAUTHORIZED_ACCESS`). | Must Have |
| **SR-10** | **Secure Error Handling** | Error responses must adhere to standardized formats without exposing internal stack traces, database schema details, or underlying library versions. | Must Have |
| **SR-11** | **Secrets Protection** | Application secrets (e.g., `SECRET_KEY`, database credentials) must be injected solely via environment variables, never hard-coded or committed to VCS. | Must Have |
| **SR-12** | **Security Testing** | The system must pass automated test verification for all 20 critical security test cases (IDOR, race conditions, brute force, SQL injection, privilege escalation). | Must Have |

---

## 7. External Interfaces & Data Requirements

### 7.1 User Interfaces
- Modern responsive web interface built with React 18 and Vite.
- Midnight Indigo theme with high contrast, semantic badges, and clear error banners.

### 7.2 Software Interfaces
- **PostgreSQL 16:** Relational database accessed via SQLAlchemy 2.0 ORM with connection pooling.
- **RESTful JSON API:** OpenAPI 3.0-compliant interface served by FastAPI.

### 7.3 Data Entities
- **Users:** `id`, `email` (unique), `password_hash`, `name`, `role`, `is_active`, `created_at`, `updated_at`.
- **Events:** `id`, `title`, `description`, `venue`, `event_date`, `start_time`, `end_time`, `participant_limit`, `registration_deadline`, `status`, `organizer_id` (FK), `created_at`, `updated_at`.
- **Registrations:** `id`, `event_id` (FK), `student_id` (FK), `registered_at`, `status`, `cancelled_at`. Partial unique index on `(event_id, student_id)` where `status = 'CONFIRMED'`.
- **Audit Logs:** `id`, `actor_id` (FK nullable), `action`, `entity_type`, `entity_id`, `timestamp`, `source_ip`, `result`, `metadata`.

---

## 8. Requirements Traceability Matrix

| Req ID | Use Case | Design Component | DB Entity / API Route | Security Control | User Story | Test Case |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **FR-01** | UC-01 | `EventService` | `GET /api/events` | SR-08, SR-10 | US-03 | TC-18 |
| **FR-02** | UC-02 | `EventService` | `GET /api/events/{id}` | SR-08, SR-10 | US-04 | TC-11 |
| **FR-03** | UC-04 | `RegistrationService` | `POST /api/events/{id}/register` | SR-02, SR-04, SR-05, SR-07 | US-07 | TC-08, TC-12 |
| **FR-04** | UC-05 | `RegistrationService` | `DELETE /api/registrations/{id}` | SR-03, SR-09 | US-10 | TC-02 |
| **FR-05** | UC-06 | `RegistrationService` | `GET /api/registrations/me` | SR-03, SR-06, SR-07 | US-11 | TC-01 |
| **FR-06** | UC-07 | `EventService` | `POST /api/events` | SR-02, SR-08, SR-09 | US-05 | TC-03, TC-13 |
| **FR-07** | UC-08 | `EventService` | `events.participant_limit` | SR-08 | US-06 | TC-09, TC-13 |
| **FR-08** | UC-09 | `RegistrationService` | `GET /api/events/{id}/participants`| SR-03, SR-06, SR-09 | US-12 | TC-05 |
| **FR-09** | UC-10 | `EventService` | `POST /api/events/{id}/close` | SR-02, SR-03, SR-09 | US-13 | TC-04, TC-10 |
| **FR-10** | UC-03 | `AuthService` | `POST /api/auth/login` | SR-01, SR-07, SR-09 | US-01 | TC-14, TC-17 |
| **FR-11** | UC-11 | `AdminService` | `GET /api/admin/system-stats` | SR-02, SR-03 | US-14 | TC-07 |
| **FR-12** | N/A | `HealthRouter` | `GET /health` | N/A | US-20 | TC-11 |
