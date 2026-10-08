# Phase 15: Logging, Monitoring, Hardening & Operational Controls

## 1. Security-Relevant Audit & Operational Logging

The **Online Event Registration System (EventHub)** implements a centralized, append-only security audit architecture ([backend/app/services/audit_service.py](file:///d:/Kartheek/WAS/SSE/backend/app/services/audit_service.py)) coupled with structured application logging ([backend/app/core/middleware.py](file:///d:/Kartheek/WAS/SSE/backend/app/core/middleware.py)).

### 1.1 Mandated Security Events Logged

| Event Type | Action Key | Trigger Condition | Logged Attributes | Security Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Failed Login** | `LOGIN_FAILURE` | Invalid credentials or inactive user | `email, source_ip, timestamp, result="FAILURE"` | Detects credential stuffing & brute-force attacks |
| **Successful Login** | `LOGIN_SUCCESS` | Valid credentials authenticated | `actor_id, source_ip, timestamp, result="SUCCESS"` | Establishes session provenance |
| **User Logout** | `LOGOUT` | User invokes `/api/auth/logout` | `actor_id, source_ip, timestamp, result="SUCCESS"` | Session lifecycle tracking |
| **Role Elevation** | `USER_ROLE_CHANGE` | Admin alters user role | `actor_id, target_user_id, old_role, new_role` | Privilege governance & non-repudiation |
| **Event Creation** | `EVENT_CREATE` | Faculty publishes an event | `actor_id, event_id, participant_limit, title` | Accountability of event coordinators |
| **Event Registration**| `EVENT_REGISTER` | Student registers for event | `actor_id, registration_id, event_id` | Provenance of registration commitments |
| **Registration Cancel**| `REGISTRATION_CANCEL`| Student cancels own registration | `actor_id, registration_id, event_id` | Capacity recovery auditing |
| **Event Closure** | `EVENT_CLOSE` | Faculty closes registration | `actor_id, event_id, total_confirmed_count` | Prevents dispute on event closure timing |
| **Unauthorized Access**| `UNAUTHORIZED_ACCESS`| IDOR attempt or role mismatch | `actor_id, target_entity_id, attempted_action, source_ip`| Rapid threat detection & incident response |
| **Administrative Action**| `ADMIN_OVERSIGHT` | Admin queries stats/users | `actor_id, query_type, source_ip` | Supervision of privileged administrators |

### 1.2 Data Sanitization & Prohibition Policy
To avoid data compromise through logs, the logging pipeline strictly enforces:
- **Zero Cleartext Passwords:** Password fields are stripped prior to serialization.
- **Zero Authentication Tokens:** JWT tokens, cookie headers, and session secrets are never output to stdout or written to `audit_logs`.
- **Zero Sensitive PII Overexposure:** Student registration records in logs only reference database integer identifiers (`actor_id`, `event_id`).

---

## 2. Monitoring Metrics & Alerting Thresholds

The system exports telemetry via the `/health` endpoint and structured log metrics designed for Prometheus, Grafana, or CloudWatch:

| # | Metric Name | Metric Description | Alert Trigger Threshold | Operational Severity | Recommended Action |
| :-: | :--- | :--- | :--- | :---: | :--- |
| **1** | `auth_login_failures_total` | Rate of failed login attempts by IP / subnet. | $> 10\text{ failures / min}$ from single IP | **High** | Temporary IP rate limit lock via firewall/middleware. |
| **2** | `security_unauthorized_attempts_total`| Count of HTTP 403 Forbidden / IDOR attempts. | $> 5\text{ attempts / 5 min}$ by single user | **High** | Account review for potential credential compromise. |
| **3** | `registration_failures_rate` | Ratio of rejected registration attempts (status 409/400).| $> 25\%\text{ of total attempts}$ | **Medium** | Inspect whether popular event reached capacity limit. |
| **4** | `event_capacity_anomaly` | Variance between confirmed registrations and event cap. | $\text{Confirmed} > \text{Limit}$ ($> 0$) | **Critical** | Database transaction freeze; capacity invariant alert. |
| **5** | `http_server_errors_5xx` | Unhandled exceptions and database connection timeouts. | $> 1\%\text{ of total requests}$ | **High** | Inspect pod restarts, connection pool starvation. |
| **6** | `app_health_status` | Readiness status of `/health` endpoint. | Status $\ne 200\text{ for } > 30\text{ seconds}$ | **Critical** | Trigger automated Kubernetes pod restart. |
| **7** | `db_connection_pool_saturation`| Active connections relative to `DB_POOL_SIZE`. | $\text{Active} > 85\%\text{ of pool size}$ | **Medium** | Scale backend replicas or increase pool size. |

---

## 3. Comprehensive System Hardening Checklist

### 3.1 Identity, Authentication & Authorization
- [x] Passwords hashed using Bcrypt with salt cost factor 12.
- [x] JWT tokens issued strictly in `HttpOnly`, `SameSite=Lax`, and `Secure` cookies.
- [x] Tokens barred from `localStorage` and `sessionStorage`.
- [x] In-memory sliding-window rate limiting on login (5 attempts per minute).
- [x] Declarative role-based access control (RBAC) enforced on all private API endpoints.
- [x] Object-level ownership validation enforced on registrations and faculty events.

### 3.2 Network, Services & Middleware
- [x] OWASP security headers injected on all responses (CSP, HSTS, X-Content-Type-Options, X-Frame-Options: DENY).
- [x] Strict CORS origin whitelisting configured via environment variables.
- [x] Only essential ports exposed (Backend: 8000; Frontend: 80/3000; Database: 5432).
- [x] Parameterized SQL queries via SQLAlchemy 2.0 preventing SQL injection.

### 3.3 Container & Kubernetes Infrastructure
- [x] Backend container executes under dedicated non-root user `appuser:10001`.
- [x] Frontend container served via unprivileged Alpine Nginx.
- [x] Kubernetes namespace isolation (`event-reg-system`).
- [x] Kubernetes `securityContext` enforces `allowPrivilegeEscalation: false` and drops all capabilities.
- [x] Resource quotas (CPU and Memory limits) enforced on all pods.
- [x] Secrets decoupled from container images and source code.

---

## 4. Physical & Operational Security Controls

### 4.1 Physical Security Controls
- **Data Center Tiering:** Cloud-hosted instances deployed in Tier III / SOC 2 Type II compliant facilities with biometric access control and redundant power.
- **Hardware Isolation:** Dedicated virtual machine tenants for production database instances.

### 4.2 Operational Security Controls
- **Incident Response Plan:** Standard Operating Procedure (SOP) activated upon high-frequency audit failure alerts.
- **Key Rotation Schedule:** Cryptographic `SECRET_KEY` and database passwords rotated every 90 days.
- **Backup & Disaster Recovery:** Automated daily encrypted database dumps stored in write-once-read-many (WORM) storage.

---

## 5. Pre-Deployment Verification Checklist

Prior to production release, DevOps engineers must verify:
1. `.env` file verified absent from source control (`git status`).
2. Production `SECRET_KEY` generated with $\ge 256$ bits of entropy (`openssl rand -hex 32`).
3. Database migrations executed and partial unique indexes verified.
4. Static security analysis (Bandit SAST and npm audit) executed with zero critical findings.
5. All 33 automated tests passing cleanly in CI.
6. Kubernetes readiness probes responding with HTTP 200 on `/health`.
