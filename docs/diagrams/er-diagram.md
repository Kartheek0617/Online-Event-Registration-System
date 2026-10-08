# Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    USERS ||--o{ EVENTS : "organizes / owns"
    USERS ||--o{ REGISTRATIONS : "submits"
    USERS ||--o{ AUDIT_LOGS : "performs (actor)"
    EVENTS ||--o{ REGISTRATIONS : "receives"

    USERS {
        integer id PK "Primary Key (Auto-increment)"
        string name "Full Name (max 100)"
        string email UK "Unique Institutional Email (max 255)"
        string password_hash "Bcrypt Salted Hash (max 255)"
        user_role_enum role "STUDENT, FACULTY, ADMIN, GUEST"
        boolean is_active "Active Status Flag"
        timestamp created_at "Account Creation Timestamp"
        timestamp updated_at "Profile Last Updated"
    }

    EVENTS {
        integer id PK "Primary Key (Auto-increment)"
        integer organizer_id FK "References USERS(id) ON DELETE CASCADE"
        string title "Event Title (max 200)"
        text description "Full Event Specifications"
        string category "Event Domain/Category (max 100)"
        string venue "Campus Location or Virtual URL (max 200)"
        string event_date "Date format YYYY-MM-DD"
        string start_time "Start time HH:MM"
        string end_time "End time HH:MM"
        integer participant_limit "Seat Capacity (CHECK > 0)"
        string registration_deadline "ISO Datetime String"
        event_status_enum status "OPEN, CLOSED, CANCELLED"
        timestamp created_at "Creation Timestamp"
        timestamp updated_at "Update Timestamp"
    }

    REGISTRATIONS {
        integer id PK "Primary Key (Auto-increment)"
        integer event_id FK "References EVENTS(id) ON DELETE CASCADE"
        integer student_id FK "References USERS(id) ON DELETE CASCADE"
        timestamp registered_at "Registration Timestamp"
        registration_status_enum status "CONFIRMED, CANCELLED"
        timestamp cancelled_at "Cancellation Timestamp (Nullable)"
    }

    AUDIT_LOGS {
        integer id PK "Primary Key (Auto-increment)"
        integer actor_id FK "References USERS(id) ON DELETE SET NULL"
        string action "Event Identifier (e.g., AUTH_LOGIN, REG_SUCCESS)"
        string entity_type "Target Domain (AUTH, EVENT, REGISTRATION, USER)"
        integer entity_id "Target Record ID"
        timestamp timestamp "Chronological Timestamp"
        string source_ip "Client IPv4 / IPv6"
        string result "SUCCESS, FAILURE, DENIED"
        text metadata_json "Sanitized Contextual Metadata"
    }
```

> **Critical Database Security Constraint:**  
> A partial unique index `uq_event_student_active` is enforced on `REGISTRATIONS (event_id, student_id) WHERE status = 'CONFIRMED'`.  
> This guarantees at the database level that no student can ever maintain more than one active confirmed registration for any event.
