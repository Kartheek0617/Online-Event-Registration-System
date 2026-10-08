# Phase 10: Sprint Execution & Sprints Documentation

## 1. Overview & Agile Governance

This document details the two planned sprints for the **Online Event Registration System** within the Scrum framework with eXtreme Programming (XP) engineering disciplines. Per project requirements, Jira is not accessed directly; this specification provides the complete Jira-ready planning data for manual entry by the project team.

---

## 2. Sprint 1 Plan

### 2.1 Sprint Goal
> **"Build the secure core of the Online Event Registration System with authentication, authorization, event management, and basic registration."**

### 2.2 Sprint Duration & Team Capacity
- **Duration:** 2 Weeks (10 working days)
- **Target Velocity / Planned Story Points:** 37 Story Points
- **Scrum Team Roles:**
  - Product Owner / Security Auditor
  - Scrum Master
  - Full-Stack Developer 1 (Security & Backend focus)
  - Full-Stack Developer 2 (Frontend & UI focus)
  - QA / Security Test Engineer

### 2.3 Sprint 1 Backlog Items

| Story ID | Epic | User Story Summary | Est. Pts | Suggested Owner | Priority |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **US-01** | EP-01: Identity & Access | Secure Multi-Role Authentication | 5 | Dev 1 (Backend) | Must Have |
| **US-02** | EP-01: Identity & Access | Role-Based Authorization & Session Mgmt | 3 | Dev 1 (Backend) | Must Have |
| **US-03** | EP-02: Event Management | View Available Events Listing | 3 | Dev 2 (Frontend) | Must Have |
| **US-04** | EP-02: Event Management | View Complete Event Details | 2 | Dev 2 (Frontend) | Must Have |
| **US-05** | EP-02: Event Management | Faculty Event Creation & Validation | 5 | Dev 1 & Dev 2 | Must Have |
| **US-06** | EP-02: Event Management | Set Participant Limits & Deadlines | 3 | Dev 1 (Backend) | Must Have |
| **US-07** | EP-03: Registration | Student Event Registration Flow | 5 | Dev 1 & Dev 2 | Must Have |
| **US-08** | EP-03: Registration | Prevent Duplicate Registrations | 3 | Dev 1 (Backend) | Must Have |
| **US-11** | EP-03: Registration | View My Registrations Dashboard | 3 | Dev 2 (Frontend) | Must Have |
| **US-17** | EP-05: Verification | Core Security Unit Testing Suite | 5 | QA / Test Eng | Must Have |
| **Total** | | | **37** | | |

### 2.4 Sprint 1 Task Decomposition

#### US-01: Secure Multi-Role Authentication (5 pts)
- **TASK-1.1:** Configure PostgreSQL User model with Bcrypt password hashing (`cost=12`, test mode `cost=4`).
- **TASK-1.2:** Implement JWT issuance into secure `HttpOnly`, `SameSite=Lax`, `Secure` cookie.
- **TASK-1.3:** Build sliding-window IP rate limiter (`5 attempts / 60s`) on `/api/auth/login`.
- **TASK-1.4:** Create React `LoginPage` with credential input and 1-click academic demo credentials.
- **TASK-1.5:** Write unit and integration tests for valid/invalid login and brute-force rejection.

#### US-02: Role-Based Authorization & Session Management (3 pts)
- **TASK-2.1:** Implement FastAPI dependency `get_current_user` checking token expiry, signature, and active status.
- **TASK-2.2:** Implement `require_role(allowed_roles)` dependency returning HTTP 403 upon privilege mismatch.
- **TASK-2.3:** Implement `/api/auth/logout` endpoint that sets max-age=0 on the cookie.
- **TASK-2.4:** Build React `AuthContext` to manage in-memory user state without storing tokens in `localStorage`.

#### US-05 & US-06: Faculty Event Creation & Limit Enforcement (8 pts)
- **TASK-5.1:** Design `events` table schema with constraints (`participant_limit > 0`, `status IN ('OPEN', 'CLOSED')`).
- **TASK-5.2:** Implement `POST /api/events` with Pydantic validation (start time < end time, future date).
- **TASK-5.3:** Create React `CreateEventPage` with interactive validation, venue selection, and capacity setting.
- **TASK-5.4:** Verify object-level constraint: events are tagged with `organizer_id = current_user.id`.

#### US-07 & US-08: Student Event Registration & Duplicate Prevention (8 pts)
- **TASK-7.1:** Implement `POST /api/events/{id}/register` service method with PostgreSQL row lock (`with_for_update()`).
- **TASK-7.2:** Add partial unique index `uq_event_student_active` on `(event_id, student_id)` where `status = 'CONFIRMED'`.
- **TASK-7.3:** Implement React registration confirmation modal and immediate quota update.
- **TASK-7.4:** Write concurrency simulation test verifying no duplicate registration allowed.

### 2.5 Definition of Done (DoD) for Sprint 1
1. Code written in accordance with Secure Software Engineering guidelines.
2. All endpoint inputs validated via strict Pydantic schemas.
3. Passwords hashed using Bcrypt; no raw secrets logged or stored.
4. Unit and integration tests written and passing in CI (`100%` pass rate for planned stories).
5. Code reviewed by peer with check for IDOR and SQL injection vulnerabilities.
6. Frontend views render cleanly across mobile and desktop without console errors.

---

## 3. Sprint 2 Plan

### 3.1 Sprint Goal
> **"Complete secure registration workflows, auditability, security hardening, automated testing, containerization, deployment and monitoring."**

### 3.2 Sprint Duration & Team Capacity
- **Duration:** 2 Weeks (10 working days)
- **Target Velocity / Planned Story Points:** 45 Story Points

### 3.3 Sprint 2 Backlog Items

| Story ID | Epic | User Story Summary | Est. Pts | Suggested Owner | Priority |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **US-09** | EP-03: Registration | Prevent Overbooking Under Concurrency | 5 | Dev 1 (Backend) | Must Have |
| **US-10** | EP-03: Registration | Cancel Own Registration with Capacity Recovery | 3 | Dev 1 & Dev 2 | Must Have |
| **US-12** | EP-02: Event Management | Faculty Participant Management & Export | 3 | Dev 2 (Frontend) | Must Have |
| **US-13** | EP-02: Event Management | Faculty Close Event Registration | 2 | Dev 1 (Backend) | Must Have |
| **US-14** | EP-04: System Administration | Admin User and Event Oversight | 5 | Dev 1 & Dev 2 | Must Have |
| **US-15** | EP-04: System Administration | Immutable Security Audit Logging | 5 | Dev 1 (Backend) | Must Have |
| **US-16** | EP-05: Verification | Application Security Hardening (OWASP Headers, CORS) | 3 | Dev 1 (Backend) | Must Have |
| **US-18** | EP-05: Verification | Containerization with Docker & Compose | 5 | DevSecOps Eng | Must Have |
| **US-19** | EP-05: Verification | Kubernetes Minikube Manifests & Pod Security | 5 | DevSecOps Eng | Must Have |
| **US-20** | EP-05: Verification | CI/CD Pipeline & Health/Monitoring Hardening | 4 | DevSecOps Eng | Should Have |
| **Total** | | | **45** | | |

### 3.4 Sprint 2 Task Decomposition

#### US-09 & US-10: Atomic Capacity Enforcement & Self-Cancellation (8 pts)
- **TASK-9.1:** Execute atomic registration inside transactional block: `SELECT * FROM events WHERE id = :id FOR UPDATE`.
- **TASK-9.2:** Evaluate `current_count < participant_limit`; reject with HTTP 409 if full.
- **TASK-10.1:** Implement `DELETE /api/registrations/{id}` with strict ownership check: `registration.student_id == current_user.id`.
- **TASK-10.2:** Mark registration as `CANCELLED`, record `cancelled_at = now()`, release capacity.
- **TASK-10.3:** Test 1 and Test 2 verification: IDOR cancellation attempts by other students return HTTP 403/404.

#### US-12 & US-13: Faculty Participant Access & Event Closure (5 pts)
- **TASK-12.1:** Implement `GET /api/events/{id}/participants` verifying `event.organizer_id == current_user.id`.
- **TASK-12.2:** Mask sensitive fields and display participants in Faculty UI with CSV export.
- **TASK-13.1:** Implement `POST /api/events/{id}/close` setting `status = 'CLOSED'` with audit log entry.
- **TASK-13.2:** Verify Test 5 and Test 6: Cross-faculty participant access or event modification is rejected with HTTP 403.

#### US-14 & US-15: Administration & Audit Logging (10 pts)
- **TASK-14.1:** Implement `GET /api/admin/users`, `GET /api/admin/events`, `GET /api/admin/system-stats`.
- **TASK-14.2:** Create React `AdminDashboard` with security metrics and role filters.
- **TASK-15.1:** Create `audit_logs` table (`actor_id, action, entity_type, entity_id, timestamp, source_ip, result, metadata`).
- **TASK-15.2:** Emit audit logs on: `LOGIN_SUCCESS`, `LOGIN_FAILURE`, `EVENT_CREATE`, `EVENT_REGISTER`, `REGISTRATION_CANCEL`, `EVENT_CLOSE`, `UNAUTHORIZED_ACCESS`.
- **TASK-15.3:** Create React `AuditLogsPage` for Admin role with search and filter capabilities.

#### US-16, US-18, US-19, US-20: Security Hardening, Containerization & CI/CD (17 pts)
- **TASK-16.1:** Install security middleware with CSP, HSTS, X-Content-Type-Options, X-Frame-Options: DENY.
- **TASK-18.1:** Author multi-stage non-root `backend/Dockerfile` (`appuser:10001`) and Nginx `frontend/Dockerfile`.
- **TASK-18.2:** Author `docker-compose.yml` with health checks, private bridge network, and volume isolation.
- **TASK-19.1:** Write Minikube manifests with `securityContext` (`runAsNonRoot: true`, `readOnlyRootFilesystem`), resource quotas.
- **TASK-20.1:** Build GitHub Actions workflow running Bandit, Ruff, pip-audit, Pytest, Docker build, and K8s linting.

### 3.5 Definition of Done (DoD) for Sprint 2
1. All 20 Critical Security Test Cases implemented and passing.
2. Zero high or critical vulnerabilities detected by Bandit, pip-audit, or npm audit.
3. Multi-service Docker Compose starts successfully with healthy health checks.
4. Kubernetes manifests validate cleanly with dry-run against standard schemas.
5. Audit logging functional and verified against sensitive data leakage (no passwords or tokens).
6. End-to-end documentation completed across all 16 academic phases.

---

## 4. Scrum Ceremony Templates & Procedures

### 4.1 Daily Scrum Template (Standup)
Held daily at 09:30 AM (15 minutes maximum).

```markdown
### Daily Scrum Meeting Notes
- **Date:** [YYYY-MM-DD] | **Sprint:** [Sprint 1 / Sprint 2]
- **Attendees:** [List of Team Members Present]

#### Team Member Updates:
1. **[Developer Name]**
   - **What did I accomplish yesterday?** 
     - [e.g., Implemented row-locking logic in registration_service.py]
   - **What will I work on today?** 
     - [e.g., Write concurrent registration simulation tests in test_registrations.py]
   - **Are there any blockers / impediments?** 
     - [e.g., None / Need clarification on audit log schema for rejected requests]

#### Security & Quality Impediments Identified:
- [Item 1: Action Owner, Target Resolution Date]
```

### 4.2 Sprint Review Template
Held on the final Friday of the sprint.

```markdown
### Sprint Review Report
- **Sprint:** [1 or 2] | **Date:** [YYYY-MM-DD]
- **Sprint Goal:** [Goal statement]
- **Goal Met:** [Yes / Partially / No]

#### Demonstrated Features:
1. [Feature 1, e.g., Multi-role login with brute-force rate limiter] -> Accepted by PO
2. [Feature 2, e.g., Atomic event registration with row locking] -> Accepted by PO
3. [Feature 3, e.g., Cross-faculty IDOR rejection] -> Verified by Security QA

#### Backlog Status:
- Total Points Committed: [e.g., 37]
- Total Points Completed & Accepted: [e.g., 37]
- Stories Carried Over: [None / List]
```

### 4.3 Sprint Retrospective Template
Held immediately after Sprint Review (Prime Directive applied).

```markdown
### Sprint Retrospective Summary
- **Sprint:** [1 or 2] | **Date:** [YYYY-MM-DD]

#### 1. What Went Well?
- Concurrency control with `with_for_update()` worked on first integration run.
- Precomputing Bcrypt test password hashes reduced test runtime from 147s to 1.18s.
- HttpOnly cookie architecture eliminated tokens from frontend storage completely.

#### 2. What Could Be Improved?
- Static typing between FastAPI Pydantic models and TypeScript interfaces had minor field mismatches initially.
- PowerShell command runner on Windows required local execution proxy.

#### 3. Action Items for Next Sprint / Maintenance:
- [Action 1: Add automated OpenAPI-to-TypeScript client generation] -> Owner: Dev 2
- [Action 2: Integrate automated Semgrep rules in local pre-commit hooks] -> Owner: DevSecOps
```
