# Master Security Test Cases Specification & Verification Protocol

## 1. Overview & Protocol Standard

This document catalogs the **20 Mandatory Security Test Cases** enforced for the academic examination of the **Online Event Registration System**. Each test case verifies a foundational security invariant, detailing the threat vector, execution procedure, expected security behavior, and implementation reference in [backend/tests/test_security_critical_20.py](file:///d:/Kartheek/WAS/SSE/backend/tests/test_security_critical_20.py).

---

## 2. The 20 Mandatory Security Test Cases

### TC-01: Cross-Student Registration Isolation (Test 1)
- **Objective:** Verify that Student A cannot access Student B's registration details.
- **Threat Vector:** Insecure Direct Object Reference (IDOR) / Information Disclosure.
- **Endpoint:** `GET /api/registrations/me`
- **Execution:** Authenticate as Student A (`student@college.edu`). Request personal registrations. Verify that records belonging to Student B (`student2@college.edu`) are omitted.
- **Expected Outcome:** HTTP 200 containing strictly Student A's records.
- **Test Code:** `test_student_a_cannot_view_student_b_registration`
- **Result:** **PASSED**

### TC-02: Prevent IDOR Cancellation of Another Student's Registration (Test 2)
- **Objective:** Verify that Student A cannot delete or cancel Student B's registration.
- **Threat Vector:** IDOR / Tampering.
- **Endpoint:** `DELETE /api/registrations/{student_b_reg_id}`
- **Execution:** Authenticate as Student A. Dispatch DELETE request specifying `id` of Student B's registration.
- **Expected Outcome:** HTTP 403 Forbidden with detail `"You are not authorized to cancel another student's registration"`.
- **Test Code:** `test_student_a_cannot_cancel_student_b_registration`
- **Result:** **PASSED**

### TC-03: Bar Student from Creating Events (Test 3)
- **Objective:** Ensure non-organizer roles cannot create campus events.
- **Threat Vector:** Privilege Escalation / Missing Functional Level Access Control.
- **Endpoint:** `POST /api/events`
- **Execution:** Dispatch event creation payload with authenticated Student cookie.
- **Expected Outcome:** HTTP 403 Forbidden; zero records inserted into `events` table.
- **Test Code:** `test_student_cannot_create_event`
- **Result:** **PASSED**

### TC-04: Bar Student from Closing Events (Test 4)
- **Objective:** Ensure student attendees cannot close event registration.
- **Threat Vector:** Unauthorized Business Logic Execution.
- **Endpoint:** `POST /api/events/{id}/close`
- **Execution:** Dispatch close request authenticated as Student.
- **Expected Outcome:** HTTP 403 Forbidden. Event status remains `OPEN`.
- **Test Code:** `test_student_cannot_close_event`
- **Result:** **PASSED**

### TC-05: Cross-Faculty Participant Roster Isolation (Test 5)
- **Objective:** Verify Faculty A cannot inspect participant rosters for events created by Faculty B.
- **Threat Vector:** Broken Object Level Authorization (BOLA) / PII Harvesting.
- **Endpoint:** `GET /api/events/{faculty_b_event_id}/participants`
- **Execution:** Authenticate as Faculty A. Request attendee roster of Faculty B's event.
- **Expected Outcome:** HTTP 403 Forbidden. Emits `UNAUTHORIZED_PARTICIPANTS_ACCESS` audit log.
- **Test Code:** `test_faculty_a_cannot_view_faculty_b_participants`
- **Result:** **PASSED**

### TC-06: Cross-Faculty Event Modification Guard (Test 6)
- **Objective:** Prevent Faculty A from altering or updating Faculty B's event details.
- **Threat Vector:** Unauthorized Object Modification.
- **Endpoint:** `PUT /api/events/{faculty_b_event_id}`
- **Execution:** Dispatch update payload authenticated as Faculty A.
- **Expected Outcome:** HTTP 403 Forbidden; event attributes remain unchanged.
- **Test Code:** `test_faculty_a_cannot_modify_faculty_b_event`
- **Result:** **PASSED**

### TC-07: Administrator Endpoint Privilege Protection (Test 7)
- **Objective:** Ensure administrative management endpoints reject student and faculty requests.
- **Threat Vector:** Administrative Privilege Escalation.
- **Endpoint:** `GET /api/admin/users`
- **Execution:** Dispatch request authenticated as Student.
- **Expected Outcome:** HTTP 403 Forbidden.
- **Test Code:** `test_admin_only_endpoint_rejects_student`
- **Result:** **PASSED**

### TC-08: Duplicate Registration Prevention (Test 8)
- **Objective:** Guarantee a student cannot register more than once for the same event.
- **Threat Vector:** Ticket Hoarding / Invariant Breach.
- **Endpoint:** `POST /api/events/{id}/register`
- **Execution:** Student registers for Event 1 (succeeds with HTTP 201). Student immediately submits second registration for Event 1.
- **Expected Outcome:** HTTP 409 Conflict: `"You are already registered for this event"`. Database partial unique index enforces boundary.
- **Test Code:** `test_student_cannot_register_twice`
- **Result:** **PASSED**

### TC-09: Participant Limit Hard Ceiling Enforcement (Test 9)
- **Objective:** Ensure total active registrations never exceed `participant_limit`.
- **Threat Vector:** Overbooking Vulnerability.
- **Endpoint:** `POST /api/events/{id}/register`
- **Execution:** Event created with `participant_limit = 2`. Student 1 and Student 2 register. Student 3 attempts registration.
- **Expected Outcome:** HTTP 409 Conflict: `"Event has reached its maximum participant limit"`.
- **Test Code:** `test_registration_cannot_exceed_participant_limit`
- **Result:** **PASSED**

### TC-10: Closed Event Registration Rejection (Test 10)
- **Objective:** Ensure events with status `CLOSED` reject incoming registrations.
- **Threat Vector:** State-Bypass Tampering.
- **Endpoint:** `POST /api/events/{closed_event_id}/register`
- **Execution:** Faculty closes event. Student attempts registration.
- **Expected Outcome:** HTTP 400 Bad Request: `"Registration for this event is closed"`.
- **Test Code:** `test_closed_event_rejects_registration`
- **Result:** **PASSED**

### TC-11: Safe Handling of Invalid Identifiers (Test 11)
- **Objective:** Verify non-existent resource IDs return clean error representations without stack traces.
- **Threat Vector:** Information Leakage / Debugger Probing.
- **Endpoint:** `GET /api/events/999999`
- **Execution:** Query extreme non-existent ID.
- **Expected Outcome:** HTTP 404 Not Found with structured JSON error; zero internal file paths or tracebacks exposed.
- **Test Code:** `test_invalid_event_id_handled_safely`
- **Result:** **PASSED**

### TC-12: Rejection of Unauthenticated Registrations (Test 12)
- **Objective:** Ensure unauthenticated guests cannot register for events.
- **Threat Vector:** Anonymous Spam Registration.
- **Endpoint:** `POST /api/events/{id}/register`
- **Execution:** Dispatch registration POST request without session cookie or token.
- **Expected Outcome:** HTTP 401 Unauthorized.
- **Test Code:** `test_unauthenticated_registration_rejected`
- **Result:** **PASSED**

### TC-13: Robust Schema Rejection of Malformed Input (Test 13)
- **Objective:** Verify Pydantic v2 rejects malicious payloads before business execution.
- **Threat Vector:** Malformed Payload / Buffer Overflow / Negative Quantities.
- **Endpoint:** `POST /api/events`
- **Execution:** Submit event creation with `participant_limit = -10` and empty title.
- **Expected Outcome:** HTTP 422 Unprocessable Entity with structured validation error.
- **Test Code:** `test_malformed_input_rejected_safely`
- **Result:** **PASSED**

### TC-14: Prohibition of Password Hash Leakage in API Responses (Test 14)
- **Objective:** Verify that password hashes are never returned by any API endpoint.
- **Threat Vector:** Sensitive Data Exposure.
- **Endpoint:** `GET /api/auth/me`, `GET /api/admin/users`
- **Execution:** Authenticate and inspect JSON responses. Search for keys `password`, `password_hash`, `hash`.
- **Expected Outcome:** Password fields completely absent from serialized schemas.
- **Test Code:** `test_passwords_never_returned_by_apis`
- **Result:** **PASSED**

### TC-15: Zero Sensitive Tokens in Audit Logs (Test 15)
- **Objective:** Ensure audit logging records security events without capturing JWTs or passwords.
- **Threat Vector:** Log-Injection / Token Harvesting via Observability.
- **Endpoint:** `GET /api/admin/audit-logs`
- **Execution:** Inspect database rows in `audit_logs`.
- **Expected Outcome:** Zero raw tokens, secret keys, or passwords present in metadata.
- **Test Code:** `test_sensitive_tokens_secrets_not_logged`
- **Result:** **PASSED**

### TC-16: Concurrent Registration Race Condition Defense (Test 16)
- **Objective:** Validate that concurrent registration requests cannot breach event capacity.
- **Threat Vector:** Time-of-Check to Time-of-Use (TOCTOU) Race Condition.
- **Execution:** Execute multiple simultaneous registration calls on an event with 1 available slot using threading.
- **Expected Outcome:** Exactly 1 registration succeeds; remaining attempts receive HTTP 409 Conflict. Total confirmed registrations equal exactly 1.
- **Test Code:** `test_concurrent_registrations_capacity_overflow`
- **Result:** **PASSED**

### TC-17: Sliding-Window Login Brute-Force Protection (Test 17)
- **Objective:** Ensure authentication endpoints enforce IP-based rate limiting.
- **Threat Vector:** Credential Stuffing / Automated Brute-Force.
- **Endpoint:** `POST /api/auth/login`
- **Execution:** Dispatch 6 rapid incorrect login attempts from the same source IP.
- **Expected Outcome:** Attempts 1-5 return HTTP 401; Attempt 6 returns HTTP 429 Too Many Requests.
- **Test Code:** `test_login_rate_limiting_brute_force`
- **Result:** **PASSED**

### TC-18: Parameterized SQL Injection Resilience (Test 18)
- **Objective:** Confirm SQL injection payloads cannot manipulate database execution.
- **Threat Vector:** SQL Injection (CWE-89).
- **Endpoint:** `GET /api/events?category=' OR '1'='1' --`
- **Execution:** Inject classic SQL injection string into search filter.
- **Expected Outcome:** Query executes safely as literal text; returns HTTP 200 with 0 matches; no SQL errors or table dumps.
- **Test Code:** `test_sql_injection_resilience`
- **Result:** **PASSED**

### TC-19: Audit Trail Generation on Security Violations (Test 19)
- **Objective:** Verify that unauthorized requests generate immutable security audit events.
- **Threat Vector:** Non-Repudiation Failure.
- **Execution:** Perform an unauthorized action (e.g., cross-student IDOR cancellation). Inspect `audit_logs` table.
- **Expected Outcome:** Audit row created with action `UNAUTHORIZED_CANCEL_ATTEMPT`, actor ID, timestamp, and source IP.
- **Test Code:** `test_unauthorized_action_generates_audit`
- **Result:** **PASSED**

### TC-20: Cryptographic Session Invalidation on Logout (Test 20)
- **Objective:** Verify that calling logout invalidates authenticated access immediately.
- **Threat Vector:** Session Fixation / Replay Attacks.
- **Endpoint:** `POST /api/auth/logout`
- **Execution:** Login, obtain cookie, call `/api/auth/logout`, then attempt to call `/api/auth/me`.
- **Expected Outcome:** Logout sets `max-age=0` clearing cookie; subsequent call returns HTTP 401 Unauthorized.
- **Test Code:** `test_logout_invalidates_session`
- **Result:** **PASSED**
