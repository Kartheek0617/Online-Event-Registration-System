# Online Event Registration System (EventHub)
### Secure Software Engineering End-Semester Laboratory Project

[![CI Pipeline](https://github.com/academic-sse/online-event-registration/actions/workflows/ci.yml/badge.svg)](.github/workflows/ci.yml)
[![Tests Passing](https://img.shields.io/badge/pytest-33%2F33%20passed-brightgreen)](backend/tests/)
[![Security SAST](https://img.shields.io/badge/bandit-0%20high%2Fmed%20issues-brightgreen)](docs/test-report.md)
[![License](https://img.shields.io/badge/license-Academic-blue.svg)](LICENSE)

---

## 1. Project Overview
The **Online Event Registration System (EventHub)** is a secure, full-stack enterprise web application designed for college campus event coordination. Engineered using a traceable Secure Software Development Lifecycle (SSDLC), the system adheres to strict defense-in-depth principles across 16 formal academic engineering phases. It prevents unauthorized registrations, race-condition overbooking, horizontal privilege escalation (IDOR), and participant data leakage under high-concurrency campus demands.

---

## 2. Problem Statement
College campuses host numerous academic workshops, hackathons, and symposiums. Managing attendee registration demands a resilient system ensuring:
- **Students:** Can browse published events, view real-time capacities, register atomically, cancel their own bookings, and inspect personal registration histories.
- **Faculty:** Can organize events, specify participant caps, view attendee rosters *strictly for their own events*, and close registration.
- **Administrators:** Supervise campus events, maintain user roles, and inspect immutable security audit logs.
- **Security Focus:** Prevent unauthorized registrations, duplicate bookings, broken object-level access control (IDOR), and unauthorized participant data harvesting.

---

## 3. Core Functional Features

### Student Capabilities
- Browse and filter campus events by keyword, category, and date.
- Real-time seat availability indicator (`Seats Left / Total Capacity`).
- One-click atomic registration with instant seat reservation.
- Self-cancellation with immediate capacity restoration.
- Private "My Registrations" dashboard displaying registration statuses.

### Faculty Capabilities
- Event creator wizard with date, time, venue, category, and capacity limit validation.
- Organizer dashboard listing all events created by the logged-in faculty member.
- Protected participant roster viewer with CSV export and privacy disclaimer.
- One-click event closure preventing further registrations.

### Administrative Capabilities
- System oversight dashboard aggregating total users, events, and registrations.
- Role management portal with non-repudiation audit logging.
- Searchable, filterable security audit log viewer (`audit_logs`).

---

## 4. Layered System Architecture

```
[Presentation Tier]        React 18 SPA (Vite + TypeScript + Midnight Indigo Glassmorphic UI)
                                 │
                                 ▼ (HTTPS + HttpOnly SameSite=Lax Secure Cookies)
[API & Security Tier]      FastAPI 0.115 + Security Middleware (CSP, HSTS, CORS)
                                 │
                                 ▼ (In-Memory Sliding-Window Rate Limiting)
[Authorization Layer]      RBAC Engine (require_roles) + Object-Level Ownership Validator
                                 │
                                 ▼ (Pydantic v2 Schemas / DTOs)
[Service Layer]            AuthService, EventService, RegistrationService, AuditService
                                 │
                                 ▼ (Pessimistic Row-Level Lock: SELECT ... FOR UPDATE)
[Persistence Layer]        SQLAlchemy 2.0 ORM + PostgreSQL 16 Relational Engine
                                 │
                                 ▼ (Partial Unique Index: uq_event_student_active)
[Database Storage]         Encrypted PostgreSQL Storage (users, events, registrations, audit_logs)
```

Detailed architectural diagrams are cataloged in [docs/diagrams/](file:///d:/Kartheek/WAS/SSE/docs/diagrams/):
- [docs/diagrams/system-architecture.png](file:///d:/Kartheek/WAS/SSE/docs/diagrams/system-architecture.png)
- [docs/diagrams/component-diagram.png](file:///d:/Kartheek/WAS/SSE/docs/diagrams/component-diagram.png)
- [docs/diagrams/deployment-diagram.png](file:///d:/Kartheek/WAS/SSE/docs/diagrams/deployment-diagram.png)

---

## 5. Technology Stack

| Domain | Technology / Library | Version | Purpose |
| :--- | :--- | :---: | :--- |
| **Frontend** | React + Vite + TypeScript | 18.3 / 6.4 | Responsive, accessible Single Page Application |
| **Styling** | Vanilla CSS (Midnight Indigo) | Custom | Modern glassmorphism, responsive cards, zero Tailwind bloat |
| **Backend** | Python + FastAPI | 3.11 / 0.115 | High-performance asynchronous RESTful API framework |
| **Validation**| Pydantic v2 | 2.10 | Strict schema validation, boundary enforcement, DTO mapping |
| **ORM** | SQLAlchemy 2.0 | 2.0.38 | Parameterized queries, transactional row locking, migrations |
| **Database** | PostgreSQL | 16-alpine | Relational persistence with ACID transactions & partial unique index |
| **Cryptography**| Passlib (Bcrypt) + PyJWT | 1.7 / 2.10 | Password hashing (`cost=12`) and signed JWT session tokens |
| **Containers**| Docker & Docker Compose | 29.6 / v2 | Non-root container packaging and multi-service orchestration |
| **Cluster** | Kubernetes / Minikube | 1.28+ | Namespace-isolated pods with `securityContext` and resource limits |
| **CI/CD** | GitHub Actions | v4 | Automated linting, SAST scanning (Bandit), testing, and container build |

---

## 6. Key Security Controls & Invariants

1. **Zero Token in LocalStorage:** JWT tokens are issued strictly into `HttpOnly`, `SameSite=Lax`, and `Secure` cookies. Browser JavaScript cannot access or exfiltrate tokens via XSS.
2. **Bcrypt Password Hashing:** Salt cost factor 12 in development/production (cost factor 4 in test mode for instant test suite execution).
3. **Pessimistic Row-Level Locking:** Prevents TOCTOU race-condition overbooking using `with_for_update()` during registration seat allocation.
4. **Database Partial Unique Index:** `uq_event_student_active` physically prevents duplicate active bookings for the same student on the same event.
5. **Object-Level Authorization (IDOR Defense):** Server-side verification ensures students can cancel only their own registrations and faculty can view participants only for their own events.
6. **Sliding-Window Rate Limiting:** In-memory rate limiter restricts login attempts to 5 per minute per IP, thwarting brute-force credential stuffing.
7. **OWASP Security Headers:** Automated middleware applies `Content-Security-Policy`, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, and `Strict-Transport-Security`.
8. **Immutable Security Audit Log:** Structured recording of all security events (`LOGIN_SUCCESS`, `LOGIN_FAILURE`, `EVENT_REGISTER`, `UNAUTHORIZED_ACCESS`).
9. **Zero Leakage Policy:** Passwords and sensitive tokens are strictly excluded from API response schemas (`UserOut`) and sanitized from audit logs.
10. **Non-Root Runtime:** Backend container runs under dedicated unprivileged user `appuser:10001`.

---

## 7. Database Design & Relational Schema

Implemented in [database/schema.sql](file:///d:/Kartheek/WAS/SSE/database/schema.sql) and [backend/app/models/](file:///d:/Kartheek/WAS/SSE/backend/app/models/):

- **`users`:** `id (PK)`, `email (UQ)`, `password_hash`, `name`, `role`, `is_active`, `created_at`, `updated_at`.
- **`events`:** `id (PK)`, `organizer_id (FK -> users)`, `title`, `description`, `category`, `venue`, `event_date`, `start_time`, `end_time`, `participant_limit`, `registration_deadline`, `status`, `created_at`, `updated_at`.
- **`registrations`:** `id (PK)`, `event_id (FK -> events)`, `student_id (FK -> users)`, `registered_at`, `status`, `cancelled_at`.  
  *Partial Unique Index:* `CREATE UNIQUE INDEX uq_event_student_active ON registrations (event_id, student_id) WHERE status = 'CONFIRMED';`
- **`audit_logs`:** `id (PK)`, `actor_id (FK -> users NULL)`, `action`, `entity_type`, `entity_id`, `timestamp`, `source_ip`, `result`, `metadata (JSONB)`.

---

## 8. Local Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+ (Node 20 / 22 recommended)
- PostgreSQL 16 (Optional: SQLite fallback runs automatically if PostgreSQL is unreachable)

```bash
# Clone the repository
git clone https://github.com/academic-sse/online-event-registration.git
cd online-event-registration

# Copy environment configuration
cp .env.example .env
```

---

## 9. Environment Configuration ([.env.example](file:///d:/Kartheek/WAS/SSE/.env.example))

```env
APP_NAME="Online Event Registration System"
ENVIRONMENT="development"
DEBUG="false"
SECRET_KEY="generate-a-secure-random-secret-key-min-32-chars"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES="120"
COOKIE_SECURE="false"
COOKIE_SAMESITE="lax"
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/event_registration_db"
ALLOWED_ORIGINS="http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
RATE_LIMIT_LOGIN_MAX_ATTEMPTS="5"
RATE_LIMIT_LOGIN_WINDOW_SECONDS="60"
```

---

## 10. Database Initialization & Seeding

```bash
# Initialize and seed database with academic demo accounts & events
python -m backend.app.seed
```

---

## 11. Running the Backend Service

```bash
cd backend
python -m pip install -r requirements.txt
python run.py

# API available at: http://localhost:8000
# OpenAPI Docs at: http://localhost:8000/docs
# Health Check at: http://localhost:8000/health
```

---

## 12. Running the Frontend Client

```bash
cd frontend
npm install
npm run dev

# Frontend accessible at: http://localhost:5173
```

---

## 13. Running Automated Tests & Security Verification

The automated test suite verifies all functional requirements, security invariants, fuzzing boundaries, and end-to-end multi-role workflows.

```bash
# Run the complete test suite (33 tests in 1.18 seconds)
python -m pytest backend/tests -v

# Run Bandit Static Application Security Testing (SAST)
python -m bandit -r backend/app -ll
```

---

## 14. Docker & Multi-Service Execution

Launch the complete application stack (PostgreSQL 16, FastAPI Backend, Nginx Frontend) in isolated Docker containers:

```bash
# Build and run containers in detached mode
docker compose up -d --build

# Verify container health
docker compose ps

# Access Web Application
# Open browser to: http://localhost:3000
```

---

## 15. Kubernetes & Minikube Deployment

```bash
# 1. Start Minikube
minikube start --driver=docker

# 2. Deploy isolated namespace
kubectl apply -f k8s/namespace.yaml

# 3. Create secrets & apply manifests
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/postgres-statefulset.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml

# 4. Access Frontend via Minikube tunnel
minikube service frontend-service -n event-reg-system
```

---

## 16. CI/CD Security Pipeline ([.github/workflows/ci.yml](file:///d:/Kartheek/WAS/SSE/.github/workflows/ci.yml))
The automated pipeline executes on every commit:
1. Python 3.11 environment initialization & dependency audit.
2. Bandit SAST scanner checking 1,908 lines of backend Python code.
3. Automated pytest suite running all 33 unit, integration, and security tests.
4. Node 20 environment initialization & `npm run build` verification.
5. Docker multi-stage container build validation.
6. Kubernetes manifest schema linting.

---

## 17. Academic Demo Credentials

The database seeder automatically initializes the following accounts:

| Role | Email Address | Password | Intended Test Workflow |
| :--- | :--- | :--- | :--- |
| **Student** | `student@college.edu` | `Student@123` | Browse, register, cancel own booking, view registrations |
| **Faculty 1** | `faculty@college.edu` | `Faculty@123` | Create event, set capacity limit, view participants, close event |
| **Faculty 2** | `faculty2@college.edu` | `Faculty@123` | Cross-faculty IDOR verification (isolated from Faculty 1) |
| **Admin** | `admin@college.edu` | `Admin@123` | System oversight, role management, security audit log review |
| **Guest** | *Unauthenticated* | *N/A* | Browse public events listing only |

*(Note: The login screen also features 1-click credential auto-fill buttons for rapid live examination demonstrations.)*

---

## 18. The 20 Mandatory Security Test Scenarios

The system passes 100% of the 20 mandatory security test cases ([docs/security-test-cases.md](file:///d:/Kartheek/WAS/SSE/docs/security-test-cases.md)):

| Test | Security Invariant Verified | Outcome |
| :---: | :--- | :---: |
| **1** | Student A cannot view Student B's registration | **PASSED** |
| **2** | Student A cannot cancel Student B's registration (IDOR) | **PASSED** |
| **3** | Student cannot create an event (RBAC) | **PASSED** |
| **4** | Student cannot close an event (RBAC) | **PASSED** |
| **5** | Faculty A cannot view Faculty B's participant list | **PASSED** |
| **6** | Faculty A cannot modify Faculty B's event | **PASSED** |
| **7** | Admin-only endpoint rejects Student | **PASSED** |
| **8** | Student cannot register twice for same event | **PASSED** |
| **9** | Registration cannot exceed participant limit | **PASSED** |
| **10** | Closed event rejects registration | **PASSED** |
| **11** | Invalid event ID handled safely without stack trace | **PASSED** |
| **12** | Unauthenticated registration rejected | **PASSED** |
| **13** | Malformed input rejected safely (Pydantic bounds) | **PASSED** |
| **14** | Passwords never returned by APIs | **PASSED** |
| **15** | Sensitive tokens/secrets not logged | **PASSED** |
| **16** | Concurrent registrations cannot cause capacity overflow | **PASSED** |
| **17** | Authentication brute-force attempts are controlled | **PASSED** |
| **18** | SQL injection payloads do not alter database behavior | **PASSED** |
| **19** | Unauthorized API calls generate audit records | **PASSED** |
| **20** | Logout invalidates authenticated session | **PASSED** |

---

## 19. Project Documentation Map

Comprehensive documentation across all 16 academic phases:

```
docs/
├── phase1-agile.md                      # Phase 1: Scrum + XP, 6 manifesto mappings, refactoring
├── phase2-srs.md                        # Phase 2: IEEE-830 SRS, FR-01..12, SR-01..12, Traceability
├── phase3-uml.md                        # Phase 3: UML Use Case, Class, Sequence, Activity models
├── phase4-data-flow.md                  # Phase 4: ER schema, Level-0/1 DFD, 4 Trust boundaries
├── phase5-architecture.md               # Phase 5: Layered architecture, 5 design patterns
├── phase6-ui.md                         # Phase 6: Screen specs, UI wireframes, accessibility
├── phase7-threat-model.md               # Phase 7: 10 Assets, 14 STRIDE threats, 6 Vulnerabilities
├── phase8-attack-tree.md                # Phase 8: Root goal attack tree, control triage
├── product-backlog.md                   # Phase 9: 20 User Stories, Epics, Points, Acceptance Criteria
├── sprints.md                           # Phase 10: Sprint 1 & 2 Plans, Tasks, DoD, Scrum ceremonies
├── scrum-metrics.md                     # Scrum velocity formulas, burndown templates, defect logs
├── phase11-secure-build.md              # Phase 11: Branching strategy, secrets, Bandit/NPM audits
├── phase12-refactoring.md               # Phase 12: Before/after vulnerable vs. secure refactoring
├── phase13-docker-kubernetes.md         # Phase 13: Container & K8s security controls, Minikube
├── phase14-ci-cd-testing.md             # Phase 14: CI/CD pipeline, 33 tests, Fuzzing, Defect DEF-01
├── phase15-logging-monitoring-hardening.md # Phase 15: Audit events, monitoring alerts, hardening
├── phase16-final-security-review.md     # Phase 16: End-to-end requirement traceability chain
├── traceability-matrix.md               # Master bidirectional requirements traceability matrix
├── test-report.md                       # Pytest execution report (33/33 passed in 1.18s)
├── deployment-guide.md                  # Local, Docker Compose, and Minikube operations guide
├── security-test-cases.md               # Detailed breakdown of the 20 Security Test Cases
└── diagrams/                            # 16 Rendered Diagram Image Suites (PNG & SVG)
```

---

## 20. Known Limitations
1. **Single-Factor Authentication:** Uses password credentials with Bcrypt and rate limiting. Enterprise environments benefit from Multi-Factor Authentication (MFA / TOTP).
2. **Synchronous Capacity Rejection:** Over-capacity registrations are rejected synchronously with HTTP 409 rather than routed to an asynchronous distributed waitlist queue.

---

## 21. Future Improvements
1. **Time-Based One-Time Password (TOTP):** Implement RFC 6238 two-factor authentication for faculty and administrative roles.
2. **Asynchronous Distributed Waitlist:** Introduce Redis and Celery to manage dynamic attendee waitlists with automatic seat promotion upon cancellation.
