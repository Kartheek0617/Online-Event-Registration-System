# Comprehensive Requirements Traceability Matrix (RTM)

## 1. Overview & Methodological Standards

This matrix provides 100% bidirectional traceability linking every functional and security requirement of the **Online Event Registration System** across its entire engineering lifecycle: from initial requirements to architectural components, data models, threats, user stories, implementation classes, and test verification cases.

---

## 2. Master Bidirectional Traceability Table

| Req ID | Requirement Summary | Use Case | Design Component | DB Entity / API Route | STRIDE Threat | Security Control | User Story | Sprint | Implementation File / Method | Test Case Verification |
| :--- | :--- | :---: | :--- | :--- | :---: | :--- | :---: | :---: | :--- | :---: |
| **FR-01** | Browse Available Events | UC-01 | `EventService` | `GET /api/events` | N/A | SR-08, SR-10 | US-03 | S1 | `event_service.py::get_events` | TC-18 |
| **FR-02** | View Event Details | UC-02 | `EventService` | `GET /api/events/{id}` | N/A | SR-08, SR-10 | US-04 | S1 | `event_service.py::get_event_by_id` | TC-11 |
| **FR-03** | Register for Event | UC-04 | `RegistrationService` | `POST /api/events/{id}/register` | THR-06, THR-07 | SR-02, SR-04, SR-05 | US-07 | S1 | `registration_service.py::register_student` | TC-08, TC-12 |
| **FR-04** | Cancel Registration | UC-05 | `RegistrationService` | `DELETE /api/registrations/{id}` | THR-14 | SR-03, SR-09 | US-10 | S2 | `registration_service.py::cancel_registration`| TC-02 |
| **FR-05** | View Personal Registrations | UC-06 | `RegistrationService` | `GET /api/registrations/me` | THR-11 | SR-03, SR-06 | US-11 | S1 | `registration_service.py::get_student_registrations`| TC-01 |
| **FR-06** | Faculty Create Event | UC-07 | `EventService` | `POST /api/events` | THR-04 | SR-02, SR-08, SR-09 | US-05 | S1 | `event_service.py::create_event` | TC-03, TC-13 |
| **FR-07** | Set Participant Limit | UC-08 | `EventService` | `events.participant_limit` | THR-08 | SR-08 | US-06 | S1 | `schemas/event.py::EventCreate` | TC-09, TC-13 |
| **FR-08** | View Event Participants | UC-09 | `RegistrationService` | `GET /api/events/{id}/participants`| THR-05 | SR-03, SR-06, SR-09 | US-12 | S2 | `registration_service.py::get_event_participants`| TC-05 |
| **FR-09** | Close Event Registration | UC-10 | `EventService` | `POST /api/events/{id}/close` | THR-04 | SR-02, SR-03, SR-09 | US-13 | S2 | `event_service.py::close_event` | TC-04, TC-10 |
| **FR-10** | Secure Login & Session | UC-03 | `AuthService` | `POST /api/auth/login` | THR-01, THR-02 | SR-01, SR-07 | US-01 | S1 | `auth_service.py::authenticate_user` | TC-14, TC-17 |
| **FR-11** | Admin Oversight & Stats | UC-11 | `AdminService` | `GET /api/admin/system-stats` | THR-13 | SR-02, SR-09 | US-14 | S2 | `admin_service.py::get_system_stats` | TC-07 |
| **FR-12** | System Health Check | N/A | `HealthRouter` | `GET /health` | THR-12 | N/A | US-20 | S2 | `api/health.py::health_check` | TC-11 |
| **SR-01** | Bcrypt Password Hashing | UC-03 | `security.py` | `users.password_hash` | THR-01 | SR-01 | US-01 | S1 | `security.py::verify_password` | TC-14 |
| **SR-02** | Role-Based Access Control | All | `AuthService` | All private endpoints | THR-13 | SR-02 | US-02 | S1 | `api/auth.py::require_roles` | TC-03, TC-07 |
| **SR-03** | Object-Level Authorization | UC-05, UC-09 | Services Layer | Registrations / Events | THR-14 | SR-03 | US-10, US-12 | S2 | `registration_service.py` | TC-01, TC-02, TC-05, TC-06 |
| **SR-04** | Prevent Unauthorized Reg | UC-04 | `RegistrationService` | `POST /api/events/{id}/register` | THR-03 | SR-04 | US-07 | S1 | `registration_service.py::register_student` | TC-03, TC-12 |
| **SR-05** | Duplicate Reg Prevention | UC-04 | `RegistrationService` | `uq_event_student_active` index | THR-07 | SR-05 | US-08 | S1 | `models/registration.py` | TC-08 |
| **SR-06** | Participant Data Protection| UC-09 | `RegistrationService` | `GET /api/events/{id}/participants`| THR-05, THR-11 | SR-06 | US-12 | S2 | `registration_service.py::get_event_participants`| TC-05 |
| **SR-07** | HttpOnly Cookie Handling | UC-03 | `AuthService` | `access_token` cookie | THR-02 | SR-07 | US-01 | S1 | `api/auth.py::login` | TC-20 |
| **SR-08** | Pydantic Schema Validation| All | Schemas Layer | Pydantic v2 Models | THR-12 | SR-08 | US-16 | S2 | `schemas/*.py` | TC-13, Fuzzing Suite |
| **SR-09** | Immutable Security Audit | All | `AuditService` | `audit_logs` table | THR-09 | SR-09 | US-15 | S2 | `audit_service.py::log_action` | TC-15, TC-19 |
| **SR-10** | Safe Error Responses | All | Middleware | Standardized RFC 7807 | THR-11 | SR-10 | US-16 | S2 | `middleware.py` | TC-11, TC-13 |
| **SR-11** | Zero Hard-Coded Secrets | All | Core Config | `.env` / Pydantic Settings | THR-11 | SR-11 | US-16 | S2 | `core/config.py` | Bandit SAST Scan |
| **SR-12** | Concurrency Race Defense | UC-04 | `RegistrationService` | `with_for_update()` row lock | THR-06, THR-08 | SR-05, SR-12 | US-09 | S2 | `registration_service.py::register_student` | TC-09, TC-16 |
