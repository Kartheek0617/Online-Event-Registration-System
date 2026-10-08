# Phase 1: Agile Process Selection & Secure Engineering Integration

## 1. Process Methodology Selection: Scrum with XP Practices
For the development of the **Online Event Registration System**, the engineering team adopted **Scrum combined with Extreme Programming (XP) secure engineering practices**.

### Justification for Secure Software Engineering
Scrum provides the macro-level organizational structure needed for academic milestones, sprint cadences, backlog grooming, and transparent role delineation across multi-functional roles (Students, Faculty, and Administrators). However, standard Scrum does not inherently mandate rigorous engineering hygiene. By fusing Scrum with XP engineering practices, we enforce:
1. **Test-Driven Development (TDD) & Automated Regression Testing:** Security boundaries, capacity invariants, and access control matrices are written into automated test suites (`pytest`) *before* and alongside feature implementation.
2. **Continuous Integration & Static Application Security Testing (CI/SAST):** Automated security scanners (Bandit, Ruff, pip-audit) inspect every code commit.
3. **Refactoring for Security & Simplicity:** Code is continually restructured to eliminate dangerous anti-patterns such as scattered authorization logic and non-atomic check-then-act database races.

---

## 2. Mapping Agile Manifesto Principles to the Project

| # | Agile Manifesto Principle | Concrete Implementation in EventHub |
| :--- | :--- | :--- |
| **1** | **Working Software over Comprehensive Documentation** | The primary measure of progress is a fully functional, containerized full-stack application backed by 33 automated tests validating actual security invariants, rather than theoretical design papers alone. |
| **2** | **Customer Collaboration over Contract Negotiation** | Constant alignment with college stakeholders (student council representatives and department faculty) ensures intuitive dashboards, accurate capacity feedback, and non-intrusive participant privacy controls. |
| **3** | **Responding to Change over Following a Plan** | When concurrency testing revealed race conditions under high-throughput registration surges, the backlog was dynamically reprioritized to implement row-level locking (`SELECT ... FOR UPDATE`) without disrupting sprint momentum. |
| **4** | **Frequent Delivery of Working Software** | Decomposed the project into two distinct 2-week iterations: Sprint 1 delivered the secure authentication and core event CRUD layer; Sprint 2 delivered atomic registrations, auditability, containerization, and Kubernetes manifests. |
| **5** | **Continuous Attention to Technical Excellence & Good Design** | Enforced cryptographic standards (Bcrypt with salt cost 12, PyJWT HS256, HttpOnly cookies, zero token leakage to `localStorage`, and parameterized ORM queries to extinguish SQL Injection). |
| **6** | **Continuous Feedback & Transparent Inspection** | Integrated structured security audit logging (`audit_logs`) and automated health checks (`/health`) providing real-time operational feedback to administrators and DevSecOps monitors. |

---

## 3. Concrete Refactoring Opportunities (Before vs. After)

### Refactoring Opportunity 1: Consolidating Scattered Authorization into a Reusable RBAC Dependency Factory
* **Problem:** In early conceptual drafts, role validation was duplicated across multiple route handlers with manual string checks (`if current_user.role != "FACULTY": raise ...`), leading to code duplication, inconsistent HTTP error codes, and maintenance vulnerability.
* **Refactoring:** Created a clean dependency injection factory `require_roles(allowed_roles: List[UserRole])` integrated directly into FastAPI's dependency graph with automated audit logging on denial.

#### Before Refactoring:
```python
# Anti-pattern: Controller bloat and inconsistent authorization logic
@router.post("/events")
def create_event(payload: EventCreate, user: User = Depends(get_current_user)):
    if user.role != "FACULTY" and user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    # create event ...
```

#### After Refactoring:
```python
# Clean Pattern: Reusable RBAC dependency with automatic security auditing
def require_roles(allowed_roles: List[UserRole]):
    def role_checker(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        if current_user.role not in allowed_roles:
            AuditService.log_event(
                db=db, action="RBAC_ACCESS_DENIED", entity_type="ENDPOINT",
                actor_id=current_user.id, result="DENIED",
                metadata={"user_role": current_user.role, "allowed_roles": [r.value for r in allowed_roles]}
            )
            raise HTTPException(status_code=403, detail=f"Access denied. Required role: {', '.join([r.value for r in allowed_roles])}")
        return current_user
    return role_checker

@router.post("/events", response_model=EventOut, status_code=201)
def create_event(payload: EventCreate, current_user: User = Depends(require_roles([UserRole.FACULTY, UserRole.ADMIN]))):
    # Pure business invocation
```

---

### Refactoring Opportunity 2: Non-Atomic Capacity Check to Transactional Locking & Database Constraint
* **Problem:** Registration capacity and duplicate checks originally ran as separate, non-atomic database queries. In high-concurrency scenarios, two students could register for the final seat simultaneously (Time-of-Check to Time-of-Use race condition), leading to overbooking.
* **Refactoring:** Restructured `RegistrationService.register_student_for_event` to execute inside an isolated transaction using row-level locking (`with_for_update()`) and created a database-level partial unique index (`uq_event_student_active`).

#### Before Refactoring:
```python
# Anti-pattern: Check-Then-Act Race Condition Vulnerability
count = db.query(Registration).filter_by(event_id=event_id).count()
if count >= event.participant_limit:
    raise HTTPException(status_code=400, detail="Full")

# Vulnerability window: Another thread inserts here!
new_reg = Registration(event_id=event_id, student_id=student.id)
db.add(new_reg)
db.commit()
```

#### After Refactoring:
```python
# Secure Pattern: Atomic Transaction with Row-Level Lock & Database Partial Unique Index
with _concurrency_lock:
    event = db.query(Event).filter(Event.id == event_id).with_for_update().first()
    if not event or event.status != EventStatus.OPEN:
        raise HTTPException(status_code=400, detail="Event closed or invalid")
    
    # Invariant checked while event row is exclusively locked
    confirmed = db.query(func.count(Registration.id)).filter(
        Registration.event_id == event_id, Registration.status == RegistrationStatus.CONFIRMED
    ).scalar() or 0
    
    if confirmed >= event.participant_limit:
        raise HTTPException(status_code=400, detail=f"Event capacity reached ({event.participant_limit} seats full).")
    
    reg = Registration(event_id=event.id, student_id=student.id, status=RegistrationStatus.CONFIRMED)
    db.add(reg)
    db.commit() # Atomic release
```

---

## 4. Agile Limitations & Risks for Security-Critical Systems

### Limitation 1: The "Speed Over Rigor" Trap (Skipping Non-Functional Security Architecture)
* **Risk:** In rapid Scrum iterations, teams frequently prioritize visible UI user stories over "invisible" non-functional requirements such as threat modeling, audit trails, and input boundary validation. This leads to severe architectural vulnerabilities discovered late in production.
* **Mitigation:** Integrated a **Security Definition of Done (DoD)** into every sprint. A story is strictly incomplete unless it passes:
  1. Role & object-level authorization checks.
  2. Input schema validation bounds.
  3. Non-exposure of passwords and tokens.
  4. Automated integration and security test cases.

### Limitation 2: Fragmented Threat Surface View
* **Risk:** Agile's incremental slicing of requirements into modular epics can obscure system-wide holistic threat vectors (such as distributed denial of service, session hijacking, or cross-cutting data leakage across services).
* **Mitigation:** Conducted a comprehensive baseline **STRIDE Threat Model** and **Attack Tree Analysis** during Sprint 0 / Phase 7 prior to sprint execution, ensuring that all subsequent user stories trace directly back to cataloged threats and mitigation controls.
