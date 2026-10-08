# Phase 6: User Interface (UI/UX) Design & Interaction Specification

## 1. Design System Foundations & Aesthetics
The user interface for **EventHub** was crafted under modern **Midnight Indigo Glassmorphic** principles. The design balances visual appeal with strict academic accessibility (WCAG 2.1 AA compliant contrast ratios and keyboard navigation).

* **Color Tokens:** Deep midnight backdrop (`#0b0f19`), surface cards (`#111827`), glowing primary indigo (`#6366f1`), semantic emerald success (`#10b981`), amber warnings (`#f59e0b`), and crimson danger (`#ef4444`).
* **Design Heuristics:**
  - *Visibility of System Status:* Real-time seat capacity gauges, status badges (OPEN, CLOSED, FULL), and loading indicators.
  - *Error Prevention:* Confirmation modals before destructive actions (cancellation, event closure, role alteration).
  - *User Control & Freedom:* Easy navigation exits, ESC key dialog dismissal, and explicit logout controls.
  - *Security Consciousness:* Zero token storage in `localStorage`, masked password fields, and strict isolation of student participant personal data.

---

## 2. Comprehensive Screen Specifications

### Screen 1: Login Screen (`/login`)
* **Primary Users:** Guest, Student, Faculty, Administrator.
* **Goal:** Authenticate identity and establish a secure, HttpOnly cookie-bound session.
* **Navigation:** Accessible from top navbar "Sign In" button or automatic redirect from protected routes.
* **Inputs:** Email address, password, one-click academic demo preset buttons (Student, Faculty, Admin).
* **Outputs:** Authenticated user session; redirects user to role-specific dashboard.
* **Feedback:** Loading indicator during authentication; instant badge transition in navbar upon sign-in.
* **Error Handling:** Inline red alert banner on invalid credentials or rate limiting (HTTP 401 / 429).
* **Security Considerations:** Generic error messages prevent username enumeration; rate limiting blocks brute-force attacks; tokens are set in HttpOnly cookies (inaccessible to XSS).

```
+--------------------------------------------------------------+
|                        EventHub                              |
|                [ Sign In to EventHub ]                       |
|                                                              |
|   College Email: [ student.aarav@college.edu               ] |
|   Password:      [ ••••••••••••••••                        ] |
|                                                              |
|   [               Sign In Securely                         ] |
|                                                              |
|   Academic Demo Presets:                                     |
|   [ Student: Aarav ]  [ Faculty: Dr. Sharma ]  [ Admin ]     |
|                                                              |
|   [ Browse Public Events as Guest ]                          |
+--------------------------------------------------------------+
```

---

### Screen 2: Events Discovery & Listing (`/events`)
* **Primary Users:** Guest, Student, Faculty, Administrator.
* **Goal:** Browse campus events, execute real-time searches, and filter by technical/cultural categories.
* **Navigation:** Accessible via navbar "Browse Events".
* **Inputs:** Search keyword field, category filter buttons (All, Cybersecurity, AI, Web, Cultural, Symposium, Robotics).
* **Outputs:** Grid of interactive glassmorphic cards showing event title, date, time, venue, remaining seats, and status badges.
* **Feedback:** Instant filtered results with debounced live search; visual empty state if no events match.
* **Error Handling:** Graceful network error alert banner if API is unreachable.
* **Security Considerations:** All search query parameters are sanitized on the backend through parameterized SQLAlchemy ORM queries, rendering SQL injection payloads inert.

---

### Screen 3: Event Details & Registration Screen (`/events/:id`)
* **Primary Users:** Guest, Student, Faculty Organizer, Administrator.
* **Goal:** Review full event details, inspect live capacity meter, and register (Students) or inspect attendees (Faculty).
* **Navigation:** Click on any event card from `/events`.
* **Inputs:** "Register Now" button, registration confirmation modal submit.
* **Outputs:** Complete event description, logistics schedule grid, interactive capacity meter bar (`%` filled), and registration status.
* **Feedback:** Dynamic registration confirmation modal; instant update to "✓ You are Registered" and seat counter decrement.
* **Error Handling:** Descriptive alerts for capacity full, event closed, or duplicate registration conflicts.
* **Security Considerations:** Student ID is extracted from verified server-side JWT claims, completely preventing student impersonation.

```
+--------------------------------------------------------------+
| <- Back to All Events                                        |
| [CYBERSECURITY] [OPEN]                                       |
|                                                              |
| Cybersecurity Awareness Workshop                             |
| Comprehensive hands-on workshop covering OWASP Top 10...     |
|                                                              |
| Logistics Schedule:                                          |
| Date: 2026-11-15 | Time: 10:00-13:00 | Venue: Auditorium A   |
| Coordinator: Dr. Ramesh Sharma | Deadline: 2026-11-14        |
|                                                              |
| Registered Capacity: [====================......] 50/50 Full |
|                                                              |
| [ Register Now for this Event ]                              |
+--------------------------------------------------------------+
```

---

### Screen 4: Student Dashboard & My Registrations (`/student`, `/my-registrations`)
* **Primary Users:** Authenticated Student.
* **Goal:** Track personal confirmed event bookings and cancel registrations if schedules change.
* **Navigation:** Navbar "Student Dashboard" / "My Registrations".
* **Inputs:** "Cancel Registration" button, cancellation modal confirmation.
* **Outputs:** Table of personal registrations with registration ID, title, date, venue, timestamp, and status badge.
* **Feedback:** Confirmation modal warns that seat will be released immediately; table updates instantly on confirmation.
* **Error Handling:** Alerts if cancellation fails or if session has expired.
* **Security Considerations:** Strict object authorization: Students can only view and cancel registrations matching their own user ID.

---

### Screen 5: Faculty Hub & Manage Events (`/faculty`, `/manage-events`, `/create-event`)
* **Primary Users:** Authenticated Faculty members.
* **Goal:** Create new campus events, edit event logistics, close active registrations, and access participant rosters.
* **Navigation:** Navbar "Faculty Hub", "Create Event", "Manage Events".
* **Inputs:** Title, description, category, venue, dates, participant limit, deadline.
* **Outputs:** Metric overview cards (Events organized, total attendees, active events); table of owned events.
* **Feedback:** Creation redirect to dashboard; confirmation modal before closing registration.
* **Error Handling:** Form validation errors highlighted inline; 422 errors handled safely.
* **Security Considerations:** Faculty can only edit or close events where `organizer_id == current_user.id`. Attempts to alter another faculty member's event return HTTP 403 Forbidden.

---

### Screen 6: Registered Participants Roster (`/events/:id/participants`)
* **Primary Users:** Faculty Coordinator who created the event, System Administrator.
* **Goal:** Inspect confirmed attendee names and emails for attendance management; export CSV.
* **Navigation:** Click "Attendees (Count)" from Faculty Hub or Manage Events.
* **Inputs:** "Export Attendance CSV" button.
* **Outputs:** Data table with Registration ID, Student ID, Student Name, Institutional Email, and Registered Timestamp.
* **Feedback:** Instant CSV file download triggered locally in browser.
* **Security Considerations:** Student personal data protection: endpoint rejects students and non-owner faculty with HTTP 403 Forbidden.

---

### Screen 7: Admin Console & Audit Logs (`/admin`, `/admin/audit-logs`)
* **Primary Users:** System Administrator.
* **Goal:** Monitor system statistics, oversee users, adjust assigned roles, and inspect security audit logs.
* **Navigation:** Navbar "Admin Console", "Audit Logs".
* **Inputs:** User role dropdown selector, confirmation modal, audit log search filter.
* **Outputs:** High-level metrics (Total users, students, faculty, events, active events, registrations, audit logs); user roster; chronological audit trail.
* **Feedback:** Role update confirmation alert; instant filtered log entries.
* **Security Considerations:** Admin-only routes rejected with HTTP 403 for students and faculty. Passwords and tokens are never displayed in audit metadata.
