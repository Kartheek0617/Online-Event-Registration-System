# Scrum Metrics & Performance Tracking Framework

## 1. Overview

This document specifies the quantitative metrics collection, calculation formulas, burndown tracking templates, and defect governance procedures for the **Online Event Registration System**. In compliance with examination instructions, actual metrics are not fabricated; rather, concrete mathematical formulations and execution templates are provided for the engineering team to populate as Jira sprints execute.

---

## 2. Velocity Tracking & Calculation Method

### 2.1 Velocity Definition
Velocity is the measure of the amount of work a Scrum team successfully completes per sprint, expressed in **Story Points**. A story is only counted toward velocity when it satisfies the **Definition of Done (DoD)** and is formally accepted by the Product Owner during the Sprint Review.

### 2.2 Mathematical Formulas

$$\text{Sprint Velocity } (V_s) = \sum_{i \in \text{Accepted Stories}} \text{Story Points}_i$$

$$\text{Rolling Average Velocity } (\bar{V}_k) = \frac{1}{k} \sum_{j=1}^{k} V_j$$

Where:
- $k$ is the number of completed historical sprints (typically $k=3$ for rolling forecasting).
- $V_j$ is the accepted velocity in sprint $j$.

### 2.3 Velocity Tracking Table (Template)

| Sprint Name | Planned Points | Committed Points | Completed & Accepted Points | Incomplete / Spilled Points | Sprint Completion Rate (%) | Notes & Anomalies |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Sprint 1** | 37 | 37 | *[To be entered]* | *[To be entered]* | $\frac{\text{Completed}}{\text{Committed}} \times 100$ | Core security & auth baseline |
| **Sprint 2** | 45 | 45 | *[To be entered]* | *[To be entered]* | $\frac{\text{Completed}}{\text{Committed}} \times 100$ | Hardening, testing, K8s, CI/CD |
| **Average** | 41 | 41 | *[Pending]* | *[Pending]* | *[Pending]* | Baseline for future releases |

---

## 3. Sprint Burndown Templates

### 3.1 Ideal vs. Actual Burndown Formula
For a sprint with $T$ working days and $S_0$ committed story points:

$$\text{Ideal Remaining Points on Day } d = S_0 \times \left( 1 - \frac{d}{T} \right), \quad d \in [0, T]$$

### 3.2 Sprint 1 Burndown Data Template (Committed: 37 Story Points, 10 Days)

| Working Day | Date | Ideal Remaining Points | Actual Remaining Points | Points Completed (Day) | Points Added/Removed | Blockers / Variance Notes |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Day 0** | Mon (Sprint Start) | 37.0 | 37 | 0 | 0 | Sprint Planning finalized |
| **Day 1** | Tue | 33.3 | [Enter] | [Enter] | [Enter] | US-01 task breakdown underway |
| **Day 2** | Wed | 29.6 | [Enter] | [Enter] | [Enter] | Database models & seed verified |
| **Day 3** | Thu | 25.9 | [Enter] | [Enter] | [Enter] | Auth & Rate limiter complete |
| **Day 4** | Fri | 22.2 | [Enter] | [Enter] | [Enter] | US-01 accepted (5 pts) |
| **Day 5** | Mon | 18.5 | [Enter] | [Enter] | [Enter] | Mid-sprint progress check |
| **Day 6** | Tue | 14.8 | [Enter] | [Enter] | [Enter] | Event creation API verified |
| **Day 7** | Wed | 11.1 | [Enter] | [Enter] | [Enter] | Registration service row locking |
| **Day 8** | Thu | 7.4 | [Enter] | [Enter] | [Enter] | Duplicate prevention test passes |
| **Day 9** | Fri | 3.7 | [Enter] | [Enter] | [Enter] | Core unit testing suite passes |
| **Day 10** | Mon (Sprint End) | 0.0 | [Enter] | [Enter] | [Enter] | Sprint 1 Review & Retro |

### 3.3 Sprint 2 Burndown Data Template (Committed: 45 Story Points, 10 Days)

| Working Day | Date | Ideal Remaining Points | Actual Remaining Points | Points Completed (Day) | Points Added/Removed | Blockers / Variance Notes |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Day 0** | Mon (Sprint Start) | 45.0 | 45 | 0 | 0 | Sprint 2 Backlog committed |
| **Day 1** | Tue | 40.5 | [Enter] | [Enter] | [Enter] | Concurrency testing harness setup |
| **Day 2** | Wed | 36.0 | [Enter] | [Enter] | [Enter] | US-09 overbooking check verified |
| **Day 3** | Thu | 31.5 | [Enter] | [Enter] | [Enter] | Self-cancellation endpoint ready |
| **Day 4** | Fri | 27.0 | [Enter] | [Enter] | [Enter] | Faculty participant viewer ready |
| **Day 5** | Mon | 22.5 | [Enter] | [Enter] | [Enter] | Admin oversight & audit logs |
| **Day 6** | Tue | 18.0 | [Enter] | [Enter] | [Enter] | Docker containerization passes |
| **Day 7** | Wed | 13.5 | [Enter] | [Enter] | [Enter] | Kubernetes manifests dry-run |
| **Day 8** | Thu | 9.0 | [Enter] | [Enter] | [Enter] | CI/CD GitHub Actions setup |
| **Day 9** | Fri | 4.5 | [Enter] | [Enter] | [Enter] | All 20 security tests pass |
| **Day 10** | Mon (Sprint End) | 0.0 | [Enter] | [Enter] | [Enter] | Sprint 2 Review & Final Audit |

---

## 4. Defect Tracking & Quality Governance

### 4.1 Defect Severity Classification Matrix

| Severity Level | Definition | Impact on Release | SLA Target |
| :--- | :--- | :--- | :--- |
| **S1 - Critical** | Security vulnerability (e.g., IDOR, SQLi, Auth bypass), data loss, or total service outage. | **Release Blocker**; stop sprint delivery until resolved. | Immediate (< 4 hours) |
| **S2 - Major** | Core workflow impaired without workaround (e.g., overbooking under concurrency, duplicate registrations). | Must be fixed before sprint conclusion. | < 24 hours |
| **S3 - Moderate** | Functional defect with existing technical workaround; UI alignment defect. | Scheduled within current or next sprint. | < 3 days |
| **S4 - Low** | Cosmetic bug, minor typographical error, non-critical enhancement. | Product backlog triage. | Future sprint |

### 4.2 Defect Lifecycle States
$$\text{New} \longrightarrow \text{Triaged} \longrightarrow \text{In Progress} \longrightarrow \text{Fixed} \longrightarrow \text{Retest Verified} \longrightarrow \text{Closed}$$

### 4.3 Defect Log Template

| Defect ID | Summary | Discovered In | Severity | Related Story / Component | Root Cause Category | Resolution Status | Verified By |
| :--- | :--- | :--- | :---: | :--- | :--- | :---: | :--- |
| **DEF-01** | ThreadPool SQLite `no such table` during parallel tests | Sprint 1 Test Run | S2 | Backend Test Harness | Test Architecture (isolated SQLite instances) | Fixed (StaticPool) | QA Lead |
| **DEF-02** | *[Template Entry]* | Sprint 2 | S3 | UI Validation | Frontend Regex | Closed | Peer Dev |

### 4.4 Defect Metrics Formulas

$$\text{Defect Density} = \frac{\text{Total Defects Found}}{\text{Total Story Points Delivered}}$$

$$\text{Defect Escape Rate (DER)} = \frac{\text{Defects Found in UAT / Production}}{\text{Total Defects (Internal QA + Production)}} \times 100\%$$

$$\text{Security Vulnerability Escape Rate} = \frac{\text{Security Findings Post-Release}}{\text{Total Security Findings Tested}} \times 100\% \quad (\text{Target: } 0.0\%)$$
