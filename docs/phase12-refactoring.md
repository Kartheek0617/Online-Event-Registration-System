# Phase 12: Secure Coding & Refactoring Evidence

## 1. Executive Summary & Module Selection

In accordance with Secure Software Engineering principles, this phase examines the **Registration Management** module (`registration_service.py` and `registrations.py`). This module is the most security-sensitive domain in the system as it handles concurrency, capacity quotas, duplicate prevention, and student identity authorization.

This document presents a rigorous academic comparative analysis between an initial naive/vulnerable implementation pattern (conceptual before) and the hardened, production-grade implementation (secure after) currently executing in the system.

---

## 2. Refactoring Comparison 1: Atomic Capacity Check & Race Condition Elimination

### 2.1 The Vulnerability: Time-of-Check to Time-of-Use (TOCTOU) Overbooking
In naive implementations, registration capacity checks are decoupled from registration insertion without database locks. If two concurrent requests arrive for an event with 1 available slot, both read `current_count < limit` simultaneously, both proceed, and both insert a record, causing overbooking beyond the hard limit.

### 2.2 Conceptual Vulnerable Implementation (Before)
```python
# VULNERABLE CONCEPTUAL CODE (Do NOT deploy)
def register_student_vulnerable(db: Session, event_id: int, student_id: int):
    # STEP 1: Non-locking read (vulnerable to TOCTOU)
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise Exception("Event not found")
        
    if event.status != "OPEN":
        raise Exception("Registration closed")
        
    # STEP 2: Count query without row lock
    count = db.query(Registration).filter(
        Registration.event_id == event_id,
        Registration.status == "CONFIRMED"
    ).count()
    
    # RACE CONDITION WINDOW: Another thread can commit here!
    if count >= event.participant_limit:
        raise Exception("Event is full")
        
    # STEP 3: Blind insertion
    reg = Registration(event_id=event_id, student_id=student_id, status="CONFIRMED")
    db.add(reg)
    db.commit() # Database committed without atomicity
    return reg
```

### 2.3 Hardened Secure Implementation (After - Implemented in `backend/app/services/registration_service.py`)
```python
# SECURE PRODUCTION IMPLEMENTATION
def register_student(
    self, db: Session, event_id: int, student: User, request_ip: Optional[str] = None
) -> Registration:
    # 1. Enforce Role Precondition
    if student.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students may register for events"
        )

    # 2. Acquire Pessimistic Row Lock on Event row (Eliminates TOCTOU Race Condition)
    event = db.query(Event).filter(Event.id == event_id).with_for_update().first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID {event_id} not found"
        )

    # 3. State & Deadline Verification
    if event.status != EventStatus.OPEN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration for this event is closed"
        )
    if event.registration_deadline and event.registration_deadline < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration deadline for this event has passed"
        )

    # 4. Check for Existing Active Registration (Defense-in-Depth Layer 1)
    existing_reg = db.query(Registration).filter(
        Registration.event_id == event_id,
        Registration.student_id == student.id,
        Registration.status == RegistrationStatus.CONFIRMED
    ).first()
    if existing_reg:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You are already registered for this event"
        )

    # 5. Atomic Capacity Check within Protected Transaction Window
    confirmed_count = db.query(Registration).filter(
        Registration.event_id == event_id,
        Registration.status == RegistrationStatus.CONFIRMED
    ).count()

    if confirmed_count >= event.participant_limit:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Event has reached its maximum participant limit"
        )

    # 6. Atomic Record Creation with Partial Unique Index Enforcement (Defense-in-Depth Layer 2)
    registration = Registration(
        event_id=event.id,
        student_id=student.id,
        status=RegistrationStatus.CONFIRMED,
        registered_at=datetime.utcnow()
    )
    db.add(registration)
    try:
        db.commit()
        db.refresh(registration)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Duplicate registration detected at database boundary"
        )

    # 7. Immutable Audit Trail
    self.audit_service.log_action(
        db, actor_id=student.id, action="EVENT_REGISTER",
        entity_type="REGISTRATION", entity_id=registration.id,
        result="SUCCESS", source_ip=request_ip,
        metadata={"event_id": event.id, "event_title": event.title}
    )
    return registration
```

---

## 3. Refactoring Comparison 2: Insecure Direct Object Reference (IDOR) Cancellation

### 3.1 The Vulnerability: Missing Object-Level Authorization
In vulnerable applications, cancellation endpoints accept a `registration_id` and delete or cancel the record based purely on the user being logged in, without checking if the current authenticated user actually owns the record. An attacker can iterate over IDs (`1, 2, 3...`) and cancel arbitrary students' registrations.

### 3.2 Conceptual Vulnerable Implementation (Before)
```python
# VULNERABLE CONCEPTUAL CODE (Do NOT deploy)
@router.delete("/registrations/{registration_id}")
def cancel_registration_vulnerable(registration_id: int, current_user = Depends(get_current_user), db = Depends(get_db)):
    # Vulnerability: Accepts any authenticated user, no ownership check
    reg = db.query(Registration).filter(Registration.id == registration_id).first()
    if not reg:
        return {"error": "Not found"}
        
    # IDOR Vulnerability: Deletes regardless of whether reg.student_id == current_user.id
    reg.status = "CANCELLED"
    db.commit()
    return {"message": "Cancelled"}
```

### 3.3 Hardened Secure Implementation (After - Implemented in `backend/app/services/registration_service.py`)
```python
# SECURE PRODUCTION IMPLEMENTATION
def cancel_registration(
    self, db: Session, registration_id: int, current_user: User, request_ip: Optional[str] = None
) -> Registration:
    # 1. Fetch Target Registration Object
    registration = db.query(Registration).filter(Registration.id == registration_id).first()
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Registration with ID {registration_id} not found"
        )

    # 2. Strict Object-Level Ownership Authorization (IDOR Defense)
    # Permitted only if current_user is the student owner OR system administrator
    if registration.student_id != current_user.id and current_user.role != UserRole.ADMIN:
        # Audit suspicious tampering attempt
        self.audit_service.log_action(
            db, actor_id=current_user.id, action="UNAUTHORIZED_CANCEL_ATTEMPT",
            entity_type="REGISTRATION", entity_id=registration_id,
            result="FAILURE", source_ip=request_ip,
            metadata={"target_student_id": registration.student_id}
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to cancel another student's registration"
        )

    # 3. Idempotency Check
    if registration.status == RegistrationStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration is already cancelled"
        )

    # 4. State Transition & Capacity Recovery
    registration.status = RegistrationStatus.CANCELLED
    registration.cancelled_at = datetime.utcnow()
    db.commit()
    db.refresh(registration)

    # 5. Security Audit Log
    self.audit_service.log_action(
        db, actor_id=current_user.id, action="REGISTRATION_CANCEL",
        entity_type="REGISTRATION", entity_id=registration.id,
        result="SUCCESS", source_ip=request_ip,
        metadata={"event_id": registration.event_id}
    )
    return registration
```

---

## 4. Refactoring Comparison 3: Cross-Faculty Participant Data Protection

### 4.1 The Vulnerability: Broken Object Level Authorization on Participant Rosters
Faculty members organize events. However, an endpoint `GET /api/events/{event_id}/participants` that merely checks `user.role == 'FACULTY'` allows Faculty A to view the student attendee lists (names, emails) of events organized by Faculty B.

### 4.2 Hardened Implementation Summary
In [registration_service.py](file:///d:/Kartheek/WAS/SSE/backend/app/services/registration_service.py), `get_event_participants`:
1. Retrieves the event entity.
2. Evaluates `event.organizer_id != current_user.id and current_user.role != UserRole.ADMIN`.
3. If true, emits an `UNAUTHORIZED_PARTICIPANTS_ACCESS` security audit entry and immediately rejects the request with `HTTP 403 Forbidden`.
4. This explicitly satisfies **Test 5** and **Test 6** in the security verification suite.

---

## 5. Security Summary Matrix of Refactoring

| Vulnerability Dimension | Initial Conceptual Flaw | Secure Refactored Solution | Test Case Verification |
| :--- | :--- | :--- | :--- |
| **Concurrency & Quotas** | Non-atomic count check; TOCTOU race condition | Pessimistic row locking (`with_for_update()`) + serial transaction block | `test_concurrent_registrations_capacity_overflow` (TC-16) |
| **Duplicate Records** | Frontend disabled button only; race window inserts dupes | Application pre-check + Database partial unique index (`uq_event_student_active`) | `test_duplicate_registration_rejected` (TC-08) |
| **Object Access (IDOR)** | Missing ownership validation on registration cancel | `registration.student_id == current_user.id` authorization check | `test_student_cannot_cancel_other_registration` (TC-02) |
| **Data Exposure** | Any faculty can list all event rosters | `event.organizer_id == current_user.id` verification | `test_faculty_cannot_view_other_event_participants` (TC-05) |
| **Error Handling** | Raw exception strings exposing database schema | Standardized RFC 7807 Pydantic / FastAPI HTTPExceptions | `test_invalid_event_id_handled_safely` (TC-11) |
