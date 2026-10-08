# Phase 16: Final Security Review & Traceability Chain

## 1. Complete End-to-End Traceability Chain

To validate the rigorous Secure Software Engineering methodology, this review traces the primary critical security invariant of the system through every single lifecycle artifact:

> **Critical Security Requirement:**  
> *"Only an authenticated student may register themselves for an event, and the system must prevent duplicate or unauthorized registration under concurrency."*

```
[Requirement: FR-03 / SR-04 / SR-05]
                 │
                 ▼
[Use Case: UC-04 (Register for Event)]
                 │
                 ▼
[Analysis Model: Student Registration Sequence & Activity Path]
                 │
                 ▼
[Data Model (ER): REGISTRATIONS Table + Partial Unique Index (uq_event_student_active)]
                 │
                 ▼
[Data Flow (DFD): Process 3.0 (Registration) across Trust Boundary 1 & 2]
                 │
                 ▼
[Threat Model: STRIDE T-01 (Capacity Tampering) & S-02 (Impersonation)]
                 │
                 ▼
[Vulnerability Analysis: VUL-01 (Check-Then-Act Race) & VUL-02 (Missing Object Auth)]
                 │
                 ▼
[Attack Tree: Path 2 (Race Condition / TOCTOU Under Load)]
                 │
                 ▼
[User Story: US-07 (Student Registration) & US-09 (Overbooking Prevention)]
                 │
                 ▼
[Sprint Assignment: Sprint 1 (Baseline) & Sprint 2 (Hardening)]
                 │
                 ▼
[Implementation: RegistrationService.register_student with_for_update() + Pydantic]
                 │
                 ▼
[Verification / Test: TC-08 (Duplicate Reject), TC-09 (Capacity Limit), TC-16 (Race)]
                 │
                 ▼
[Deployment Control: Non-Root K8s Pod (uid 10001) + Resource Limits + Health Probes]
```

### Traceability Breakdown Table
| Phase / Artifact | Specific Identifier / Reference | Concrete Realization |
| :--- | :--- | :--- |
| **Requirements** | `FR-03`, `SR-04`, `SR-05` | Formal specification in [docs/phase2-srs.md](file:///d:/Kartheek/WAS/SSE/docs/phase2-srs.md). |
| **Use Case** | `UC-04: Register for Event` | Actor: Student; Include: Authenticate; Guard: Open & capacity available. |
| **Analysis Model** | Activity & Sequence Models | Pre-check, row lock, atomic insert, audit logging. |
| **Data Model (ER)** | `REGISTRATIONS` entity | Foreign keys to `events` and `users`; partial unique index on confirmed status. |
| **Data Flow (DFD)** | Level-1 Process `3.0` | Inbound request through Trust Boundary 1 to locked Event Store. |
| **Threat Model** | `THR-06`, `THR-07` | STRIDE Tampering: Overbooking quota race & duplicate registration. |
| **Vulnerability** | `VUL-01`, `VUL-02` | Time-of-check to time-of-use (TOCTOU) concurrency race condition. |
| **Attack Tree** | Attack Path 2 | Concurrent registration requests fired simultaneously to exploit delay. |
| **User Stories** | `US-07`, `US-08`, `US-09` | Decomposed stories with specific acceptance criteria in Product Backlog. |
| **Sprint Plan** | Sprint 1 & Sprint 2 | Backlog prioritization and task execution in [docs/sprints.md](file:///d:/Kartheek/WAS/SSE/docs/sprints.md). |
| **Implementation** | `registration_service.py` | `with_for_update()`, atomic count evaluation, role assertion. |
| **Automated Tests** | `TC-08`, `TC-09`, `TC-16` | Automated pytest test cases in [test_security_critical_20.py](file:///d:/Kartheek/WAS/SSE/backend/tests/test_security_critical_20.py). |
| **Deployment** | `backend-deployment.yaml` | Kubernetes resource limits, unprivileged runtime, network isolation. |

---

## 2. Top Three Highest-Risk Issues & Defense-in-Depth Controls

### 2.1 Risk 1: Duplicate Registration & Overbooking via Concurrency Race (High / Critical)
- **Threat Mechanism:** Attackers launch automated concurrent registration requests using tools like Turbo Intruder or scripts to claim seats beyond the event's `participant_limit` or secure multiple tickets for one student.
- **Implemented Controls:**
  - *Preventive Control 1:* Database-level pessimistic locking (`SELECT ... FOR UPDATE`) guarantees serial execution of quota verification and record insertion.
  - *Preventive Control 2:* Database partial unique index (`uq_event_student_active`) on `(event_id, student_id)` where `status = 'CONFIRMED'` blocks duplicate entries at the database engine boundary even if application code fails.
  - *Detective Control:* Automated registration failure telemetry and audit logging of `EVENT_REGISTER` operations.
  - *Test Verification:* Passed `test_concurrent_registrations_capacity_overflow` and `test_duplicate_registration_rejected`.

### 2.2 Risk 2: Insecure Direct Object Reference (IDOR) & Broken Object Authorization (High)
- **Threat Mechanism:** A student attempts to cancel another student's registration by manipulating the `registration_id` in `DELETE /api/registrations/{id}`, or a faculty member accesses student participant rosters for other faculty events.
- **Implemented Controls:**
  - *Preventive Control:* Object-level authorization checks:
    ```python
    if registration.student_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    ```
  - *Detective Control:* Audit log captures `UNAUTHORIZED_CANCEL_ATTEMPT` with actor ID, target student ID, and source IP.
  - *Test Verification:* Passed `test_student_cannot_cancel_other_registration` (TC-02) and `test_faculty_cannot_view_other_event_participants` (TC-05).

### 2.3 Risk 3: Credential Stuffing & Token Theft (High)
- **Threat Mechanism:** Attackers brute-force student accounts or execute XSS attacks to steal session tokens stored in browser storage.
- **Implemented Controls:**
  - *Preventive Control 1:* Bcrypt password hashing with cost factor 12 enforces computational hardness against offline cracking.
  - *Preventive Control 2:* Sliding-window IP rate limiter limits authentication attempts to 5 per minute per IP.
  - *Preventive Control 3:* JWT tokens are issued strictly inside `HttpOnly`, `SameSite=Lax`, and `Secure` cookies. Zero tokens are stored in `localStorage` or accessible to client-side scripts.
  - *Detective Control:* Audit log records `LOGIN_FAILURE` with IP address.
  - *Test Verification:* Passed `test_login_rate_limiting_brute_force` (TC-17) and `test_passwords_never_returned_by_apis` (TC-14).

---

## 3. System Limitations & Future Engineering Roadmap

### 3.1 Limitation 1: Single-Factor Authentication (Lack of MFA / TOTP)
- **Context:** The current system uses single-factor password authentication. While secured with Bcrypt and rate limiting, enterprise environments benefit from Multi-Factor Authentication.
- **Future Roadmap:** Implement Time-Based One-Time Password (TOTP) RFC 6238 integration with authenticator apps (Google Authenticator) for Faculty and Administrator roles.

### 3.2 Limitation 2: Synchronous Waitlist Queuing Under Extreme Concurrency
- **Context:** When an event is full, excess registration requests are rejected synchronously.
- **Future Roadmap:** Integrate an asynchronous event-driven waitlist queue powered by Redis and Celery/RabbitMQ, automatically promoting waitlisted students upon cancellation events.
