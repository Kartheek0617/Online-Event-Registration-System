# Product Backlog & Jira-Ready User Stories

The human team will create and manage Jira manually. This document provides the complete, Jira-ready specification for all 20 implementation user stories, including Epics, story points, acceptance criteria, dependencies, sprint assignments, and suggested ownership.

---

## 1. Epic Definitions

* **EPIC-01: Identity, Authentication & Role-Based Access (IAM)**
  Covers credential management, Bcrypt hashing, secure HttpOnly sessions, rate limiting, and RBAC authorization guards.
* **EPIC-02: Campus Event Lifecycle & Capacity Management (EVT)**
  Covers public event discovery, category search, faculty event creation, capacity specification, and registration closure.
* **EPIC-03: Secure & Atomic Registration Engine (REG)**
  Covers atomic student registration, duplicate prevention, overbooking elimination, IDOR-protected cancellation, and participant isolation.
* **EPIC-04: System Oversight & Forensic Auditability (ADM)**
  Covers admin dashboards, user role elevation, operational metrics, and immutable audit trails.
* **EPIC-05: DevSecOps, Containerization & Automated Quality Assurance (OPS)**
  Covers Docker, Kubernetes Minikube manifests, CI/CD security pipelines, and automated test suites.

---

## 2. Product Backlog Items (US-01 through US-20)

### US-01: Secure Login & Credential Verification
* **Story ID:** US-01
* **Epic:** EPIC-01 (IAM)
* **User Story:** *As a registered student, faculty member, or administrator, I want to securely log in using my college email and password, so that I can access my authorized role features without risking credential theft.*
* **Priority:** Critical (Must Have)
* **Story Points:** 5
* **Suggested Sprint:** Sprint 1
* **Suggested Owner:** Backend Security Lead
* **Dependencies:** None
* **Acceptance Criteria:**
  1. Passwords verified using constant-time comparison against Bcrypt salted hashes (rounds $\ge 12$).
  2. Issues cryptographically signed JWT in an HttpOnly, SameSite=Lax cookie.
  3. Returns user profile excluding `password_hash`.
  4. Returns HTTP 401 on bad credentials with generic error message.

---

### US-02: Role-Based Access Control (RBAC) Enforcement
* **Story ID:** US-02
* **Epic:** EPIC-01 (IAM)
* **User Story:** *As a system security architect, I want role-based access control enforced on every protected API endpoint, so that students and faculty cannot access administrative or cross-role functions.*
* **Priority:** Critical (Must Have)
* **Story Points:** 3
* **Suggested Sprint:** Sprint 1
* **Suggested Owner:** Backend Security Lead
* **Dependencies:** US-01
* **Acceptance Criteria:**
  1. FastAPI dependency `require_roles([UserRole])` intercepts unprivileged requests with HTTP 403 Forbidden.
  2. Student accounts cannot call `/api/events` (POST), `/api/admin/*`, or `/api/events/{id}/participants`.
  3. Denied access attempts generate an audit log record with actor ID, IP, and requested path.

---

### US-03: Public Event Browsing & Search
* **Story ID:** US-03
* **Epic:** EPIC-02 (EVT)
* **User Story:** *As a student or guest visitor, I want to browse upcoming campus events and search by title, category, or venue, so that I can discover activities relevant to my interests.*
* **Priority:** High (Must Have)
* **Story Points:** 3
* **Suggested Sprint:** Sprint 1
* **Suggested Owner:** Frontend Developer
* **Dependencies:** None
* **Acceptance Criteria:**
  1. `GET /api/events` returns list of events accessible to unauthenticated guests.
  2. Supports `?search=`, `?category=`, and `?status=` query parameters.
  3. All queries parameterized via SQLAlchemy ORM to prevent SQL Injection.
  4. UI renders responsive cards with status badges and live seat counter.

---

### US-04: Comprehensive Event Details Inspection
* **Story ID:** US-04
* **Epic:** EPIC-02 (EVT)
* **User Story:** *As a student or guest, I want to view detailed logistics, capacity progress, and schedules for an event, so that I can decide whether to attend.*
* **Priority:** High (Must Have)
* **Story Points:** 2
* **Suggested Sprint:** Sprint 1
* **Suggested Owner:** Frontend Developer
* **Dependencies:** US-03
* **Acceptance Criteria:**
  1. `GET /api/events/{id}` returns complete description, venue, date, times, and coordinator name.
  2. For authenticated students, returns `is_registered_by_user` flag and registration ID.
  3. Invalid event IDs return HTTP 404 without leaking stack traces.

---

### US-05: Faculty Event Creation
* **Story ID:** US-05
* **Epic:** EPIC-02 (EVT)
* **User Story:** *As a faculty coordinator, I want to create new campus events with complete schedule details, so that students can register for department programs.*
* **Priority:** High (Must Have)
* **Story Points:** 5
* **Suggested Sprint:** Sprint 1
* **Suggested Owner:** Full-Stack Developer
* **Dependencies:** US-01, US-02
* **Acceptance Criteria:**
  1. `POST /api/events` accepts validated payload and sets `organizer_id = current_user.id`.
  2. Student and Guest requests are rejected with HTTP 403 / 401.
  3. Records audit event `EVENT_CREATED`.

---

### US-06: Participant Limit Specification & Input Validation
* **Story ID:** US-06
* **Epic:** EPIC-02 (EVT)
* **User Story:** *As a faculty coordinator, I want to enforce strict participant seat limits on my events, so that venues do not exceed fire and physical seating capacities.*
* **Priority:** High (Must Have)
* **Story Points:** 3
* **Suggested Sprint:** Sprint 1
* **Suggested Owner:** Backend Developer
* **Dependencies:** US-05
* **Acceptance Criteria:**
  1. `participant_limit` validated to be integer $> 0$ and $\le 10,000$.
  2. Database schema enforces `CHECK (participant_limit > 0)`.
  3. Negative or zero limits return HTTP 422 Unprocessable Entity.

---

### US-07: Student Event Registration
* **Story ID:** US-07
* **Epic:** EPIC-03 (REG)
* **User Story:** *As an authenticated student, I want to register for an open campus event, so that I can reserve my seat and participate.*
* **Priority:** Critical (Must Have)
* **Story Points:** 5
* **Suggested Sprint:** Sprint 1
* **Suggested Owner:** Full-Stack Developer
* **Dependencies:** US-01, US-04
* **Acceptance Criteria:**
  1. `POST /api/events/{id}/register` creates confirmed registration.
  2. Student ID resolved from verified JWT cookie, never request body.
  3. Returns HTTP 201 Created with registration ID.
  4. Immediate audit log recorded for `EVENT_REGISTRATION_SUCCESS`.

---

### US-08: Prevent Duplicate Registrations
* **Story ID:** US-08
* **Epic:** EPIC-03 (REG)
* **User Story:** *As a system security engineer, I want to strictly prevent a student from registering multiple times for the same event, so that seat reservations cannot be hoarded.*
* **Priority:** Critical (Must Have)
* **Story Points:** 5
* **Suggested Sprint:** Sprint 2
* **Suggested Owner:** Database / Backend Engineer
* **Dependencies:** US-07
* **Acceptance Criteria:**
  1. Service query checks for existing active registration (`status == 'CONFIRMED'`).
  2. Database partial unique index `uq_event_student_active` rejects duplicate inserts at persistence level.
  3. Re-registration attempt returns HTTP 409 Conflict.

---

### US-09: Concurrency-Safe Overbooking Elimination
* **Story ID:** US-09
* **Epic:** EPIC-03 (REG)
* **User Story:** *As a software architect, I want atomic capacity checks and row locking during registration, so that concurrent requests at capacity limit do not cause overbooking.*
* **Priority:** Critical (Must Have)
* **Story Points:** 8
* **Suggested Sprint:** Sprint 2
* **Suggested Owner:** Backend Lead
* **Dependencies:** US-07, US-08
* **Acceptance Criteria:**
  1. Acquires exclusive row lock (`SELECT ... FOR UPDATE` / mutex) during capacity evaluation.
  2. Concurrent requests for final seat result in exactly one HTTP 201 and all others receiving HTTP 400.
  3. Passes multi-threaded concurrency automated test suite (`test_16`).

---

### US-10: IDOR-Protected Registration Cancellation
* **Story ID:** US-10
* **Epic:** EPIC-03 (REG)
* **User Story:** *As an authenticated student, I want to cancel my own registration if my schedule changes, so that my seat is released for other students without allowing others to cancel it.*
* **Priority:** High (Must Have)
* **Story Points:** 5
* **Suggested Sprint:** Sprint 2
* **Suggested Owner:** Full-Stack Developer
* **Dependencies:** US-07
* **Acceptance Criteria:**
  1. `DELETE /api/registrations/{id}` verifies `reg.student_id == current_user.id`.
  2. Student A attempting to cancel Student B's registration is rejected with HTTP 403 Forbidden.
  3. Status updated to `CANCELLED` and available capacity restored immediately.

---

### US-11: Personal Registrations Inspection
* **Story ID:** US-11
* **Epic:** EPIC-03 (REG)
* **User Story:** *As an authenticated student, I want to view my confirmed and cancelled registrations in a private table, so that I can manage my event participation.*
* **Priority:** Medium (Must Have)
* **Story Points:** 3
* **Suggested Sprint:** Sprint 2
* **Suggested Owner:** Frontend Developer
* **Dependencies:** US-07, US-10
* **Acceptance Criteria:**
  1. `GET /api/registrations/me` returns exclusively registrations owned by the caller.
  2. Student cannot inspect another student's registration records.
  3. Includes event title, date, venue, and status badges.

---

### US-12: Faculty Participant Roster Protection
* **Story ID:** US-12
* **Epic:** EPIC-03 (REG)
* **User Story:** *As a faculty organizer, I want to view confirmed participants for my events while preventing unauthorized faculty or students from seeing them, so that student privacy is preserved.*
* **Priority:** High (Must Have)
* **Story Points:** 5
* **Suggested Sprint:** Sprint 2
* **Suggested Owner:** Backend Security Lead
* **Dependencies:** US-05, US-07
* **Acceptance Criteria:**
  1. `GET /api/events/{id}/participants` restricted to `event.organizer_id == current_user.id` or Admin.
  2. Faculty A cannot view Faculty B's participants (HTTP 403).
  3. Students cannot view any participant rosters (HTTP 403).
  4. Passwords and tokens never exposed in participant payloads.

---

### US-13: Event Registration Closure
* **Story ID:** US-13
* **Epic:** EPIC-02 (EVT)
* **User Story:** *As a faculty coordinator, I want to close registration for my event when the deadline arrives, so that no further registrations are accepted.*
* **Priority:** High (Must Have)
* **Story Points:** 3
* **Suggested Sprint:** Sprint 2
* **Suggested Owner:** Full-Stack Developer
* **Dependencies:** US-05
* **Acceptance Criteria:**
  1. `POST /api/events/{id}/close` verifies ownership and sets `status = CLOSED`.
  2. Subsequent registration attempts rejected with HTTP 400 Bad Request.
  3. Unauthorized closure attempts rejected with HTTP 403.

---

### US-14: Admin User & System Oversight
* **Story ID:** US-14
* **Epic:** EPIC-04 (ADM)
* **User Story:** *As a system administrator, I want to monitor system statistics and manage user roles, so that I can govern campus operations safely.*
* **Priority:** High (Must Have)
* **Story Points:** 5
* **Suggested Sprint:** Sprint 2
* **Suggested Owner:** Full-Stack Developer
* **Dependencies:** US-01, US-02
* **Acceptance Criteria:**
  1. `GET /api/admin/stats` returns aggregated counts for users, events, registrations, and audits.
  2. `PUT /api/admin/users/{id}/role` updates user role with audit logging.
  3. Students and Faculty are barred from all `/api/admin/*` endpoints with HTTP 403.

---

### US-15: Security Audit Logging & Non-Repudiation
* **Story ID:** US-15
* **Epic:** EPIC-04 (ADM)
* **User Story:** *As a security officer or administrator, I want immutable audit logs of all logins, role changes, registrations, and authorization denials, so that all security events are traceable.*
* **Priority:** High (Must Have)
* **Story Points:** 5
* **Suggested Sprint:** Sprint 2
* **Suggested Owner:** Backend Security Lead
* **Dependencies:** US-01, US-02
* **Acceptance Criteria:**
  1. Captures `action`, `actor_id`, `entity_type`, `entity_id`, `timestamp`, `source_ip`, and `result`.
  2. Automatically scrubs any keys containing `password`, `token`, or `secret` from metadata.
  3. `GET /api/admin/audit-logs` accessible only to Administrators.

---

### US-16: Application Security Hardening
* **Story ID:** US-16
* **Epic:** EPIC-01 (IAM)
* **User Story:** *As a DevSecOps engineer, I want OWASP security headers, CORS origin whitelisting, and brute-force rate limiting enforced, so that client-side attacks are mitigated.*
* **Priority:** High (Must Have)
* **Story Points:** 5
* **Suggested Sprint:** Sprint 2
* **Suggested Owner:** DevSecOps Engineer
* **Dependencies:** US-01
* **Acceptance Criteria:**
  1. Injects HSTS, CSP, X-Frame-Options: DENY, and X-Content-Type-Options: nosniff.
  2. Rate limiter blocks IPs making $> 5$ failed login attempts per minute with HTTP 429.
  3. Stack traces hidden from client responses on unhandled 500 exceptions.

---

### US-17: Automated Quality Assurance & Security Test Suite
* **Story ID:** US-17
* **Epic:** EPIC-05 (OPS)
* **User Story:** *As a QA engineer, I want automated unit, integration, and security test suites, so that regressions are caught before deployment.*
* **Priority:** High (Must Have)
* **Story Points:** 5
* **Suggested Sprint:** Sprint 2
* **Suggested Owner:** QA Lead
* **Dependencies:** All implementation stories
* **Acceptance Criteria:**
  1. 33 automated tests passing in pytest with zero failures.
  2. All 20 mandatory security test cases explicitly verified green.
  3. Input boundary and fuzzing test cases verified green.

---

### US-18: Docker Containerization & Multi-Service Compose
* **Story ID:** US-18
* **Epic:** EPIC-05 (OPS)
* **User Story:** *As a DevOps engineer, I want containerized Dockerfiles and a multi-service docker-compose setup, so that the application runs reliably across environments.*
* **Priority:** High (Must Have)
* **Story Points:** 5
* **Suggested Sprint:** Sprint 2
* **Suggested Owner:** DevOps Engineer
* **Dependencies:** US-01 through US-15
* **Acceptance Criteria:**
  1. Multi-stage Dockerfiles for backend (Python non-root `uid 10001`) and frontend (Nginx alpine).
  2. `docker-compose.yml` orchestrates PostgreSQL 16, Backend API, and Frontend Web with healthchecks.
  3. Healthcheck on `/health` returns status UP.

---

### US-19: Kubernetes Manifests & Security Contexts
* **Story ID:** US-19
* **Epic:** EPIC-05 (OPS)
* **User Story:** *As a cloud engineer, I want Minikube-compatible Kubernetes manifests with non-root security contexts, so that the application can be orchestrated securely on K8s.*
* **Priority:** Medium (Should Have)
* **Story Points:** 5
* **Suggested Sprint:** Sprint 2
* **Suggested Owner:** Cloud / DevSecOps Engineer
* **Dependencies:** US-18
* **Acceptance Criteria:**
  1. Complete manifests: `namespace.yaml`, `configmap.yaml`, `secret.example.yaml`, `postgres-statefulset.yaml`, `backend-deployment.yaml`, `frontend-deployment.yaml`.
  2. Applies `runAsNonRoot: true`, resource requests/limits, and dropped capabilities.
  3. Syntactically valid YAML tested against schemas.

---

### US-20: GitHub Actions CI/CD Security Pipeline
* **Story ID:** US-20
* **Epic:** EPIC-05 (OPS)
* **User Story:** *As a DevSecOps engineer, I want a GitHub Actions CI pipeline executing SAST scans, tests, and build checks, so that bad code is rejected before merging.*
* **Priority:** Medium (Should Have)
* **Story Points:** 3
* **Suggested Sprint:** Sprint 2
* **Suggested Owner:** DevSecOps Lead
* **Dependencies:** US-17, US-18
* **Acceptance Criteria:**
  1. Workflow runs on `push` and `pull_request` for `main` and `develop`.
  2. Executes Bandit SAST, Ruff lint, pip-audit, and pytest test suite.
  3. Compiles frontend TypeScript and validates Docker builds.
