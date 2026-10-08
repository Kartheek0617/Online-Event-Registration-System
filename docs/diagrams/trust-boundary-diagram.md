# Trust Boundaries Diagram

```mermaid
flowchart TB
    subgraph TB0 ["Boundary 0: Public Untrusted Zone"]
        GuestUser["👤 Untrusted Guest Browser"]
        StudentUser["🎓 Student Client Browser"]
        FacultyUser["👨‍🏫 Faculty Client Browser"]
        Attacker["🥷 Malicious Adversary (Spoofer / Scanner)"]
    end

    subgraph TB1 ["Trust Boundary 1: Transport & Ingress Perimeter (TLS / HTTPS)"]
        Nginx["🛡️ Reverse Proxy / Ingress Nginx<br/>- TLS Termination<br/>- Rate Limiter (5 req/min on login)<br/>- Security Headers Filter"]
    end

    subgraph TB2 ["Trust Boundary 2: Application API & RBAC Enforcement Tier"]
        AuthMiddleware["🔒 Auth Middleware & Session Validator<br/>- HttpOnly Cookie Inspection<br/>- PyJWT Signature & Expiry Check"]
        RBAC["🛡️ RBAC Guard & Object Authorizer<br/>- Role Verification (STUDENT, FACULTY, ADMIN)<br/>- Ownership Check (event.organizer_id == user.id)"]
        
        subgraph AppServices ["FastAPI Service Layer"]
            EventSvc["EventService<br/>- Input Sanitization<br/>- Schema Validation"]
            RegSvc["RegistrationService<br/>- Atomic Lock<br/>- Capacity & Duplicate Rules"]
            AdminSvc["AdminService<br/>- Role Upgrades<br/>- System Oversight"]
            AuditSvc["AuditService<br/>- Non-repudiation Event Logger"]
        end
    end

    subgraph TB3 ["Trust Boundary 3: Secure Data Storage Tier"]
        DBEngine["🗄️ PostgreSQL Database Engine<br/>- Parameterized SQL (SQLAlchemy ORM)<br/>- Row-level Lock (FOR UPDATE)<br/>- Partial Unique Index uq_event_student_active"]
        DataStores[("Encrypted Persistent Volume<br/>users, events, registrations, audit_logs")]
    end

    %% Cross-boundary connections
    GuestUser & StudentUser & FacultyUser & Attacker -->|"HTTP/HTTPS (Untrusted Requests)"| Nginx
    Nginx -->|"Sanitized Proxied Stream"| AuthMiddleware
    AuthMiddleware -->|"Decoded Claims Context"| RBAC
    RBAC -->|"Authorized Invocations"| AppServices
    AppServices -->|"Parameterized Queries / Locked Transactions"| DBEngine
    DBEngine <--> DataStores
```

### Trust Boundary Analysis
| Boundary | Name | Trust Transition | Enforced Security Controls |
| :--- | :--- | :--- | :--- |
| **TB-0 / TB-1** | Perimeter Boundary | Untrusted Internet $\rightarrow$ Ingress | TLS/HTTPS encryption, Rate limiting, CORS origin restrictions, OWASP security headers (CSP, HSTS). |
| **TB-1 / TB-2** | Application Boundary | Ingress $\rightarrow$ API Gateway | Cryptographic JWT verification, HttpOnly cookie extraction, Pydantic input schema validation. |
| **TB-2 / TB-3** | Internal Auth Boundary | API Layer $\rightarrow$ Core Services | Role-Based Access Control (RBAC), Object-level ownership validation (IDOR defense), Least privilege execution. |
| **TB-3 / TB-4** | Persistence Boundary | Service Layer $\rightarrow$ PostgreSQL | SQLAlchemy parameterized queries (SQLi prevention), Database transactional row locking, Database unique constraints. |
