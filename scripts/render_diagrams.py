"""
Enhanced Professional Diagram Renderer for Online Event Registration System (EventHub)
Generates publication-quality, academic-grade rendered PNG (300 DPI) and SVG diagrams.
Features refined typography, structured visual hierarchy, clean card containers,
orthogonal/curved routing, distinct trust boundaries, and true hierarchical attack trees.
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs", "diagrams"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Cohesive Academic Engineering Palette
CANVAS_BG = "#0b1120"      # Deep Navy Canvas
CARD_BG = "#131e36"        # Midnight Slate Card
CARD_BORDER = "#2e3f60"    # Subtle Border
CARD_HEADER_BG = "#1e293b" # Section Header
TEXT_TITLE = "#f8fafc"     # High-contrast White
TEXT_BODY = "#e2e8f0"      # Slate Light
TEXT_MUTED = "#94a3b8"     # Medium Muted Slate

# Semantic Accents
ACCENT_BLUE = "#38bdf8"    # Sky Blue (Frontend / Public)
ACCENT_INDIGO = "#818cf8"  # Indigo (Services / Auth)
ACCENT_GREEN = "#34d399"   # Emerald (Database / Confirmed)
ACCENT_AMBER = "#fbbf24"   # Amber (Processes / Warnings)
ACCENT_ROSE = "#f87171"    # Rose (Threats / Admin / Untrusted)
ACCENT_PURPLE = "#c084fc"  # Purple (Registrations / Tokens)

def setup_canvas(title: str, subtitle: str, width: float = 15.0, height: float = 9.5):
    fig, ax = plt.subplots(figsize=(width, height), facecolor=CANVAS_BG)
    ax.set_facecolor(CANVAS_BG)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # Document Header Title Block
    ax.text(50, 96.5, title.upper(), fontsize=15, fontweight="bold", color=TEXT_TITLE, ha="center", va="top")
    ax.text(50, 93.0, f"EventHub Architectural Specification  |  {subtitle}", 
            fontsize=9.5, color=TEXT_MUTED, ha="center", va="top")
    
    # Subtle top divider line
    ax.plot([4, 96], [91.0, 91.0], color=CARD_BORDER, linewidth=1.2, linestyle="-")
    return fig, ax

def draw_card(ax, x, y, w, h, title="", lines=None, accent=ACCENT_INDIGO, bg=CARD_BG, title_bg=None, corner=1.5):
    """Draws a clean, modular card with a dedicated header banner and legible text lines."""
    # Outer box
    box = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad={corner}",
                         facecolor=bg, edgecolor=accent, linewidth=1.4, zorder=2)
    ax.add_patch(box)

    # Optional header band
    if title:
        header_h = min(6.0, h * 0.28)
        header_box = FancyBboxPatch((x, y + h - header_h), w, header_h,
                                    boxstyle=f"round,pad={corner}",
                                    facecolor=title_bg if title_bg else CARD_HEADER_BG,
                                    edgecolor="none", zorder=3)
        ax.add_patch(header_box)
        ax.text(x + w/2, y + h - (header_h/2), title, fontsize=9.5, fontweight="bold",
                color=TEXT_TITLE, ha="center", va="center", zorder=4)

    # Content text
    if lines:
        start_y = y + h - (header_h + 3.0 if title else 3.0)
        spacing = (start_y - y) / (len(lines) + 0.5) if len(lines) > 1 else 3.5
        for idx, line in enumerate(lines):
            curr_y = start_y - (idx * spacing)
            if curr_y > y + 0.5:
                # Distinguish bullet lines vs sub-headers
                if line.startswith("•") or line.startswith("+") or line.startswith("-"):
                    ax.text(x + 2.0, curr_y, line, fontsize=8.0, color=TEXT_BODY, ha="left", va="center", zorder=4)
                elif ":" in line and not line.startswith(" "):
                    parts = line.split(":", 1)
                    ax.text(x + 2.0, curr_y, parts[0] + ":", fontsize=8.0, fontweight="bold", color=accent, ha="left", va="center", zorder=4)
                    ax.text(x + 2.0 + len(parts[0])*0.85, curr_y, parts[1], fontsize=8.0, color=TEXT_BODY, ha="left", va="center", zorder=4)
                else:
                    ax.text(x + w/2, curr_y, line, fontsize=8.0, color=TEXT_MUTED, ha="center", va="center", zorder=4)
    return box

def draw_arrow(ax, x1, y1, x2, y2, label="", color=ACCENT_BLUE, style="->", lw=1.4, label_pos=0.5):
    """Draws a clean directed connection with a clear, readable text badge."""
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw, mutation_scale=11), zorder=5)
    if label:
        lx = x1 + (x2 - x1) * label_pos
        ly = y1 + (y2 - y1) * label_pos
        ax.text(lx, ly, f" {label} ", fontsize=7.5, fontweight="bold", color=TEXT_TITLE, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.25", facecolor=CANVAS_BG, edgecolor=CARD_BORDER, linewidth=0.8, alpha=0.92),
                zorder=6)

def save_diagram(fig, base_name: str):
    png_path = os.path.join(OUTPUT_DIR, f"{base_name}.png")
    svg_path = os.path.join(OUTPUT_DIR, f"{base_name}.svg")
    plt.tight_layout()
    fig.savefig(png_path, dpi=300, facecolor=CANVAS_BG, edgecolor="none")
    fig.savefig(svg_path, facecolor=CANVAS_BG, edgecolor="none")
    plt.close(fig)
    print(f"Verified rendered: {base_name}.png & {base_name}.svg")

# ==============================================================================
# 1. USE CASE DIAGRAM
# ==============================================================================
def render_use_case_diagram():
    fig, ax = setup_canvas("UML Use Case Diagram", "Actor Interactions & Core Functional Boundaries")

    # Boundary Container
    sys_box = FancyBboxPatch((28, 6), 68, 81, boxstyle="round,pad=1.5",
                             facecolor="#0e172a", edgecolor="#475569", linewidth=1.8, linestyle="--", zorder=1)
    ax.add_patch(sys_box)
    ax.text(62, 84.5, "SYSTEM BOUNDARY: EVENT REGISTRATION CORE (EVENTHUB)", fontsize=10.5, fontweight="bold", color=ACCENT_INDIGO, ha="center")

    # Actors
    actors = [
        ("Guest\n(Public Visitor)", 12, 72, ACCENT_BLUE),
        ("Student\n(Participant)", 12, 50, ACCENT_GREEN),
        ("Faculty\n(Organizer)", 12, 28, ACCENT_AMBER),
        ("Administrator\n(Superuser)", 12, 9, ACCENT_ROSE)
    ]
    for name, x, y, col in actors:
        circle = patches.Circle((x, y + 4.5), 2.8, facecolor=CARD_BG, edgecolor=col, linewidth=2, zorder=3)
        ax.add_patch(circle)
        ax.text(x, y - 2.5, name, fontsize=8.5, fontweight="bold", color=TEXT_TITLE, ha="center", va="top")

    # Use Cases
    ucs = [
        ("UC-01: Browse & Filter Events", 44, 75, ACCENT_BLUE),
        ("UC-02: View Event Details & Quota", 76, 75, ACCENT_BLUE),
        ("UC-03: Multi-Role Secure Login", 60, 63, ACCENT_INDIGO),
        ("UC-04: Register for Event (Atomic)", 44, 50, ACCENT_GREEN),
        ("UC-05: Cancel Own Registration", 76, 50, ACCENT_GREEN),
        ("UC-06: View Personal Registrations", 44, 38, ACCENT_GREEN),
        ("UC-07: Create Event & Set Limits", 44, 25, ACCENT_AMBER),
        ("UC-08: Close Registration Early", 76, 25, ACCENT_AMBER),
        ("UC-09: View Own Event Attendees", 44, 13, ACCENT_AMBER),
        ("UC-10: System Oversight & Audits", 76, 13, ACCENT_ROSE),
    ]
    for text, cx, cy, col in ucs:
        box = FancyBboxPatch((cx - 13, cy - 3.5), 26, 7, boxstyle="round,pad=2.2",
                             facecolor=CARD_BG, edgecolor=col, linewidth=1.3, zorder=3)
        ax.add_patch(box)
        ax.text(cx, cy, text, fontsize=8.0, fontweight="bold", color=TEXT_TITLE, ha="center", va="center", zorder=4)

    # Actor -> Use Case Connectors
    draw_arrow(ax, 16, 76, 31, 75, color=ACCENT_BLUE)
    draw_arrow(ax, 16, 76, 63, 75, color=ACCENT_BLUE)
    draw_arrow(ax, 16, 54, 31, 50, color=ACCENT_GREEN)
    draw_arrow(ax, 16, 54, 63, 50, color=ACCENT_GREEN)
    draw_arrow(ax, 16, 54, 31, 38, color=ACCENT_GREEN)
    draw_arrow(ax, 16, 32, 31, 25, color=ACCENT_AMBER)
    draw_arrow(ax, 16, 32, 63, 25, color=ACCENT_AMBER)
    draw_arrow(ax, 16, 32, 31, 13, color=ACCENT_AMBER)
    draw_arrow(ax, 16, 13, 63, 13, color=ACCENT_ROSE)

    save_diagram(fig, "use-case-diagram")

# ==============================================================================
# 2. CLASS DIAGRAM
# ==============================================================================
def render_class_diagram():
    fig, ax = setup_canvas("UML Class Diagram", "Domain Entities, Attributes, Methods & Service Interfaces")

    draw_card(ax, 5, 46, 26, 41, "User Entity", [
        "+ id: Integer [PK]",
        "+ email: String [UNIQUE]",
        "+ password_hash: String",
        "+ name: String",
        "+ role: UserRole (ENUM)",
        "+ is_active: Boolean",
        "+ created_at: DateTime",
        "+ updated_at: DateTime",
        "-----------------------",
        "+ verify_password(): Bool",
        "+ set_password(): Void",
        "+ is_student(): Bool"
    ], accent=ACCENT_INDIGO)

    draw_card(ax, 37, 46, 28, 41, "Event Entity", [
        "+ id: Integer [PK]",
        "+ organizer_id: Integer [FK]",
        "+ title: String (200)",
        "+ description: Text",
        "+ category: String (50)",
        "+ venue: String (100)",
        "+ event_date: Date",
        "+ participant_limit: Int",
        "+ status: EventStatus",
        "-----------------------",
        "+ is_open(): Bool",
        "+ has_capacity(): Bool",
        "+ close_registration(): Void"
    ], accent=ACCENT_AMBER)

    draw_card(ax, 71, 46, 25, 41, "Registration Entity", [
        "+ id: Integer [PK]",
        "+ event_id: Integer [FK]",
        "+ student_id: Integer [FK]",
        "+ registered_at: DateTime",
        "+ status: RegStatus",
        "+ cancelled_at: DateTime",
        "-----------------------",
        "+ cancel(): Void",
        "+ is_active(): Bool",
        "UQ: (event_id, student_id)",
        "    WHERE status='CONFIRMED'"
    ], accent=ACCENT_PURPLE)

    draw_card(ax, 16, 8, 30, 32, "AuditLog Entity", [
        "+ id: Integer [PK]",
        "+ actor_id: Integer [FK null]",
        "+ action: String (100)",
        "+ entity_type: String (50)",
        "+ entity_id: Integer",
        "+ timestamp: DateTime",
        "+ source_ip: String (45)",
        "+ result: String (SUCCESS/DENIED)",
        "+ metadata: JSONB"
    ], accent=ACCENT_ROSE)

    draw_card(ax, 54, 8, 32, 32, "RegistrationService", [
        "- db: Session",
        "- audit_service: AuditService",
        "-----------------------",
        "+ register_student(): Reg",
        "+ cancel_registration(): Reg",
        "+ get_event_participants(): List",
        "+ check_duplicate(): Bool",
        "+ acquire_row_lock(): Event"
    ], accent=ACCENT_GREEN)

    # Relationships
    draw_arrow(ax, 37, 68, 31, 68, "1 (organizer)", color=ACCENT_INDIGO)
    draw_arrow(ax, 65, 68, 71, 68, "1..* (registrations)", color=ACCENT_PURPLE)
    draw_arrow(ax, 71, 78, 31, 78, "1..* (student)", color=ACCENT_INDIGO)
    draw_arrow(ax, 31, 24, 18, 46, "0..* (audit)", color=ACCENT_ROSE)
    draw_arrow(ax, 70, 40, 70, 46, "manages", color=ACCENT_GREEN)

    save_diagram(fig, "class-diagram")

# ==============================================================================
# 3. SEQUENCE DIAGRAM: LOGIN
# ==============================================================================
def render_sequence_login():
    fig, ax = setup_canvas("UML Sequence Diagram: Secure Authentication", "Bcrypt Hash Verification, Token Issuance & HttpOnly Cookie")

    lifelines = [
        ("User / Student", 14, ACCENT_BLUE),
        ("React Client", 36, ACCENT_INDIGO),
        ("AuthRouter / API", 60, ACCENT_AMBER),
        ("Database / Bcrypt", 86, ACCENT_GREEN)
    ]
    for title, x, col in lifelines:
        draw_card(ax, x - 9, 81, 18, 7.5, title, accent=col)
        ax.plot([x, x], [10, 81], color=CARD_BORDER, linestyle="--", linewidth=1.3, zorder=1)

    steps = [
        (14, 36, 74, "1. Input Email & Password", ACCENT_BLUE),
        (36, 60, 66, "2. POST /api/auth/login", ACCENT_INDIGO),
        (60, 60, 59, "3. Check IP Sliding Rate Limiter (max 5/min)", ACCENT_AMBER),
        (60, 86, 52, "4. Query User record by email", ACCENT_AMBER),
        (86, 60, 45, "5. Return user & verify Bcrypt hash (cost=12)", ACCENT_GREEN),
        (60, 86, 38, "6. Insert AuditLog: LOGIN_SUCCESS", ACCENT_ROSE),
        (60, 36, 30, "7. HTTP 200 + Set-Cookie (HttpOnly, SameSite=Lax, Secure)", ACCENT_GREEN),
        (36, 14, 22, "8. Update In-Memory AuthContext & Redirect to Dashboard", ACCENT_BLUE)
    ]
    for x1, x2, y, text, col in steps:
        if x1 == x2:
            # Self-call loop
            ax.plot([x1, x1 + 5, x1 + 5, x1], [y + 1.5, y + 1.5, y - 1.5, y - 1.5], color=col, lw=1.3, zorder=4)
            ax.text(x1 + 6, y, text, fontsize=7.5, color=TEXT_BODY, va="center", zorder=5)
        else:
            draw_arrow(ax, x1, y, x2, y, text, color=col)

    save_diagram(fig, "sequence-login")

# ==============================================================================
# 4. SEQUENCE DIAGRAM: REGISTRATION
# ==============================================================================
def render_sequence_registration():
    fig, ax = setup_canvas("UML Sequence Diagram: Atomic Event Registration", "Pessimistic Row Locking, Quota Verification & Duplicate Prevention")

    lifelines = [
        ("Student Client", 12, ACCENT_BLUE),
        ("RegistrationRouter", 35, ACCENT_INDIGO),
        ("RegistrationService", 58, ACCENT_AMBER),
        ("PostgreSQL Database", 83, ACCENT_GREEN)
    ]
    for title, x, col in lifelines:
        draw_card(ax, x - 9, 81, 18, 7.5, title, accent=col)
        ax.plot([x, x], [8, 81], color=CARD_BORDER, linestyle="--", linewidth=1.3, zorder=1)

    steps = [
        (12, 35, 74, "1. POST /api/events/{id}/register (HttpOnly Cookie)", ACCENT_BLUE),
        (35, 58, 67, "2. require_roles([STUDENT]) validates JWT session claims", ACCENT_INDIGO),
        (58, 83, 60, "3. BEGIN TX: SELECT * FROM events WHERE id=:id FOR UPDATE", ACCENT_AMBER),
        (83, 58, 53, "4. Return locked row & verify status == OPEN", ACCENT_GREEN),
        (58, 83, 46, "5. Check duplicate active & count confirmed attendees", ACCENT_AMBER),
        (83, 58, 39, "6. Verify confirmed_count < participant_limit", ACCENT_GREEN),
        (58, 83, 32, "7. INSERT INTO registrations (status='CONFIRMED')", ACCENT_PURPLE),
        (83, 58, 25, "8. Partial unique index uq_event_student_active passes", ACCENT_GREEN),
        (58, 83, 18, "9. COMMIT TX & record AuditLog (EVENT_REGISTER)", ACCENT_ROSE),
        (58, 35, 13, "10. Return RegistrationOut (HTTP 201 Created)", ACCENT_GREEN),
        (35, 12, 9, "11. Update UI: Seat Quota Decremented & Badge Rendered", ACCENT_BLUE)
    ]
    for x1, x2, y, text, col in steps:
        draw_arrow(ax, x1, y, x2, y, text, color=col)

    save_diagram(fig, "sequence-registration")

# ==============================================================================
# 5. ACTIVITY DIAGRAM: REGISTRATION
# ==============================================================================
def render_activity_registration():
    fig, ax = setup_canvas("UML Activity Diagram: Event Registration Flow", "Decision Gates, Concurrency Invariants & Exception Paths")

    # Start Node
    start = patches.Circle((50, 87), 2.5, facecolor=ACCENT_BLUE, edgecolor=TEXT_TITLE, lw=2, zorder=3)
    ax.add_patch(start)
    ax.text(50, 91.5, "Start Registration Request", fontsize=8.5, fontweight="bold", color=TEXT_TITLE, ha="center")

    draw_card(ax, 38, 75, 24, 7, "Authenticate Request", ["• Extract JWT from cookie", "• Verify role == STUDENT"], accent=ACCENT_INDIGO)
    draw_arrow(ax, 50, 84.5, 50, 82, color=ACCENT_BLUE)

    draw_card(ax, 37, 59, 26, 8, "Acquire Row Lock", ["• SELECT ... FOR UPDATE", "• Atomic TX Isolation"], accent=ACCENT_AMBER)
    draw_arrow(ax, 50, 75, 50, 67, "Valid Role", color=ACCENT_GREEN)

    draw_card(ax, 35, 43, 30, 8, "Verify Capacity & Duplicates", ["• confirmed_count < limit", "• No existing active booking"], accent=ACCENT_PURPLE)
    draw_arrow(ax, 50, 59, 50, 51, "Locked Row", color=ACCENT_AMBER)

    draw_card(ax, 37, 27, 26, 8, "Commit Registration", ["• INSERT INTO registrations", "• Persist Security AuditLog"], accent=ACCENT_GREEN)
    draw_arrow(ax, 50, 43, 50, 35, "Constraints Satisfied", color=ACCENT_GREEN)

    # Rejection Box (Error path)
    draw_card(ax, 74, 51, 22, 12, "Rejection & Rollback", [
        "HTTP 409 / 400 / 403",
        "• Abort DB Transaction",
        "• Record Audit Failure",
        "• Return Safe Error JSON"
    ], accent=ACCENT_ROSE)
    draw_arrow(ax, 65, 47, 74, 56, "Full / Duplicate", color=ACCENT_ROSE)
    draw_arrow(ax, 62, 78, 80, 63, "Invalid Role", color=ACCENT_ROSE)

    # End Node
    end = patches.Circle((50, 13), 2.5, facecolor=ACCENT_GREEN, edgecolor=TEXT_TITLE, lw=2, zorder=3)
    ax.add_patch(end)
    ax.text(50, 7.5, "Registration Confirmed", fontsize=8.5, fontweight="bold", color=TEXT_TITLE, ha="center")
    draw_arrow(ax, 50, 27, 50, 15.5, color=ACCENT_GREEN)

    save_diagram(fig, "activity-registration")

# ==============================================================================
# 6. ER DIAGRAM
# ==============================================================================
def render_er_diagram():
    fig, ax = setup_canvas("Entity-Relationship (ER) Diagram", "PostgreSQL Relational Schema with Constraints, Foreign Keys & Partial Indexes")

    draw_card(ax, 5, 52, 26, 36, "USERS", [
        "PK  id: SERIAL",
        "UQ  email: VARCHAR(255)",
        "    password_hash: VARCHAR",
        "    name: VARCHAR(100)",
        "    role: VARCHAR(20)",
        "    is_active: BOOLEAN",
        "    created_at: TIMESTAMP",
        "    updated_at: TIMESTAMP"
    ], accent=ACCENT_INDIGO)

    draw_card(ax, 39, 50, 28, 38, "EVENTS", [
        "PK  id: SERIAL",
        "FK  organizer_id: INT (Users)",
        "    title: VARCHAR(200)",
        "    description: TEXT",
        "    category: VARCHAR(50)",
        "    venue: VARCHAR(100)",
        "    event_date: DATE",
        "    participant_limit: INT > 0",
        "    status: VARCHAR(20)",
        "    created_at: TIMESTAMP"
    ], accent=ACCENT_AMBER)

    draw_card(ax, 73, 52, 24, 36, "REGISTRATIONS", [
        "PK  id: SERIAL",
        "FK  event_id: INT (Events)",
        "FK  student_id: INT (Users)",
        "    registered_at: TIMESTAMP",
        "    status: VARCHAR(20)",
        "    cancelled_at: TIMESTAMP",
        "--------------------------",
        "UQ: (event_id, student_id)",
        "    WHERE status='CONFIRMED'"
    ], accent=ACCENT_PURPLE)

    draw_card(ax, 37, 8, 32, 32, "AUDIT_LOGS", [
        "PK  id: SERIAL",
        "FK  actor_id: INT (Users NULL)",
        "    action: VARCHAR(100)",
        "    entity_type: VARCHAR(50)",
        "    entity_id: INT NULL",
        "    timestamp: TIMESTAMP",
        "    source_ip: VARCHAR(45)",
        "    result: VARCHAR(20)",
        "    metadata: JSONB"
    ], accent=ACCENT_ROSE)

    # Connections
    draw_arrow(ax, 31, 70, 39, 70, "1 to Many (organizes)", color=ACCENT_INDIGO)
    draw_arrow(ax, 67, 70, 73, 70, "1 to Many (registrations)", color=ACCENT_AMBER)
    draw_arrow(ax, 73, 80, 31, 80, "Many to 1 (student)", color=ACCENT_PURPLE)
    draw_arrow(ax, 18, 52, 37, 24, "1 to Many (actions)", color=ACCENT_ROSE)

    save_diagram(fig, "er-diagram")

# ==============================================================================
# 7. DFD LEVEL 0
# ==============================================================================
def render_dfd_level_0():
    fig, ax = setup_canvas("Data Flow Diagram (DFD) — Level 0 Context Diagram", "System Context Boundary & External Entity Interactions")

    # Core System Process 0
    draw_card(ax, 37, 36, 30, 26, "PROCESS 0.0", [
        "ONLINE EVENT REGISTRATION",
        "SYSTEM (EVENTHUB CORE)",
        "• Multi-Role Authentication",
        "• Concurrency Quota Enforcement",
        "• Participant Roster Protection",
        "• Security Audit Subsystem"
    ], accent=ACCENT_INDIGO, bg="#111c38")

    # External Entities
    draw_card(ax, 6, 68, 22, 18, "Guest / Student", [
        "External Participant",
        "• Browse Event Listings",
        "• Atomic Registration",
        "• Self-Cancellation"
    ], accent=ACCENT_BLUE)

    draw_card(ax, 6, 14, 22, 18, "Faculty Coordinator", [
        "Event Organizer",
        "• Publish Events & Quotas",
        "• View Event Attendees",
        "• Close Registration"
    ], accent=ACCENT_AMBER)

    draw_card(ax, 74, 40, 22, 18, "System Administrator", [
        "Platform Governance",
        "• Manage User Roles",
        "• System Metrics",
        "• Inspect Security Audits"
    ], accent=ACCENT_ROSE)

    # Flows
    draw_arrow(ax, 28, 77, 37, 56, "Search / Register / Cancel", color=ACCENT_BLUE)
    draw_arrow(ax, 37, 51, 28, 70, "Confirmation & Event Details", color=ACCENT_GREEN)

    draw_arrow(ax, 28, 23, 37, 43, "Create Events / Close Registration", color=ACCENT_AMBER)
    draw_arrow(ax, 37, 39, 28, 18, "Attendee Rosters & Metrics", color=ACCENT_GREEN)

    draw_arrow(ax, 74, 52, 67, 52, "Manage Roles & Query Audits", color=ACCENT_ROSE)
    draw_arrow(ax, 67, 46, 74, 46, "System Stats & Audit Logs", color=ACCENT_BLUE)

    save_diagram(fig, "dfd-level-0")

# ==============================================================================
# 8. DFD LEVEL 1
# ==============================================================================
def render_dfd_level_1():
    fig, ax = setup_canvas("Data Flow Diagram (DFD) — Level 1 Decomposed Process Model", "Functional Subsystems, Data Stores & Inter-Process Pipelines")

    # Processes
    draw_card(ax, 8, 68, 24, 14, "P1.0: Authentication", ["• Verify Bcrypt Hash", "• Sliding Rate Limit", "• Issue HttpOnly JWT"], accent=ACCENT_INDIGO)
    draw_card(ax, 39, 68, 24, 14, "P2.0: Event Management", ["• Event Creation & Edit", "• Quota Boundary Check", "• Registration Closure"], accent=ACCENT_AMBER)
    draw_card(ax, 70, 68, 24, 14, "P3.0: Registration Engine", ["• Row-Level Lock Check", "• Duplicate Prevention", "• Status State Machine"], accent=ACCENT_PURPLE)
    draw_card(ax, 22, 18, 26, 14, "P4.0: Participant Management", ["• Cross-Faculty Check", "• Sanitized Roster Export", "• Privacy Enforcement"], accent=ACCENT_GREEN)
    draw_card(ax, 58, 18, 26, 14, "P5.0: Security Audit Subsystem", ["• Ingest Security Events", "• Sanitize Tokens/PII", "• Immutable Append-Only"], accent=ACCENT_ROSE)

    # Data Stores
    draw_card(ax, 8, 43, 22, 11, "D1: Users Store", ["Relational table (users)", "Bcrypt hashes & roles"], accent=ACCENT_BLUE, bg="#0d1527")
    draw_card(ax, 40, 43, 22, 11, "D2: Events Store", ["Relational table (events)", "Quotas & schedules"], accent=ACCENT_AMBER, bg="#0d1527")
    draw_card(ax, 72, 43, 22, 11, "D3: Registrations Store", ["Relational registrations", "Partial Unique Index"], accent=ACCENT_PURPLE, bg="#0d1527")

    # Connectors
    draw_arrow(ax, 20, 68, 19, 54, "Read / Write", color=ACCENT_INDIGO)
    draw_arrow(ax, 51, 68, 51, 54, "Update Events", color=ACCENT_AMBER)
    draw_arrow(ax, 82, 68, 82, 54, "Insert Confirmed", color=ACCENT_PURPLE)
    draw_arrow(ax, 70, 75, 62, 54, "Lock Event Row", color=ACCENT_AMBER)
    draw_arrow(ax, 71, 26, 71, 32, "Persist Logs", color=ACCENT_ROSE)

    save_diagram(fig, "dfd-level-1")

# ==============================================================================
# 9. TRUST BOUNDARY DIAGRAM
# ==============================================================================
def render_trust_boundary_diagram():
    fig, ax = setup_canvas("Trust Boundary & Security Perimeter Model", "Zone Classification, Defense-in-Depth Inspection Gates & Isolation Boundaries")

    # Zone 1: Untrusted Public Internet (Red tint)
    z1 = FancyBboxPatch((4, 7), 27, 82, boxstyle="round,pad=1.5", facecolor="#1e131d", edgecolor=ACCENT_ROSE, linewidth=2, linestyle="--", zorder=1)
    ax.add_patch(z1)
    ax.text(17.5, 85.5, "TRUST ZONE 1: UNTRUSTED CLIENT", fontsize=9.5, fontweight="bold", color=ACCENT_ROSE, ha="center")
    draw_card(ax, 7, 56, 21, 16, "Browser (React SPA)", ["• Guest / Student / Faculty", "• In-Memory State", "• Zero LocalStorage Tokens"], accent=ACCENT_BLUE)
    draw_card(ax, 7, 22, 21, 16, "External Scripts / Attackers", ["• Postman / Curl / Bots", "• Tampered Payload Probes", "• Brute-Force Attempts"], accent=ACCENT_ROSE)

    # Trust Boundary 1
    ax.plot([33.5, 33.5], [7, 89], color=ACCENT_ROSE, linewidth=2.2, linestyle=":", zorder=4)
    ax.text(33.5, 48, "TRUST BOUNDARY 1 (TLS 1.3 / CORS / IP RATE LIMITER)", fontsize=8.0, fontweight="bold", color=ACCENT_ROSE, rotation=90, va="center", ha="right")

    # Zone 2: Application Cluster & RBAC (Amber tint)
    z2 = FancyBboxPatch((36, 7), 31, 82, boxstyle="round,pad=1.5", facecolor="#181a2e", edgecolor=ACCENT_AMBER, linewidth=2, linestyle="--", zorder=1)
    ax.add_patch(z2)
    ax.text(51.5, 85.5, "TRUST ZONE 2: APPLICATION RUNTIME", fontsize=9.5, fontweight="bold", color=ACCENT_AMBER, ha="center")
    draw_card(ax, 39, 56, 25, 16, "FastAPI API Gateway", ["• Pydantic v2 Schemas", "• OWASP Security Headers", "• Sliding-Window Rate Limit"], accent=ACCENT_AMBER)
    draw_card(ax, 39, 22, 25, 16, "Core Security Engine", ["• require_roles RBAC Guard", "• Object-Level Authorizer", "• HttpOnly Cookie Verify"], accent=ACCENT_INDIGO)

    # Trust Boundary 2
    ax.plot([69.5, 69.5], [7, 89], color=ACCENT_GREEN, linewidth=2.2, linestyle=":", zorder=4)
    ax.text(69.5, 48, "TRUST BOUNDARY 2 (ISOLATED DATABASE BRIDGE NETWORK)", fontsize=8.0, fontweight="bold", color=ACCENT_GREEN, rotation=90, va="center", ha="right")

    # Zone 3: Secure Data Tier (Green tint)
    z3 = FancyBboxPatch((72, 7), 24, 82, boxstyle="round,pad=1.5", facecolor="#0d2222", edgecolor=ACCENT_GREEN, linewidth=2, linestyle="--", zorder=1)
    ax.add_patch(z3)
    ax.text(84.0, 85.5, "TRUST ZONE 3: PERSISTENCE TIER", fontsize=9.5, fontweight="bold", color=ACCENT_GREEN, ha="center")
    draw_card(ax, 74, 52, 20, 20, "PostgreSQL 16 Engine", ["• ACID Transactions", "• SELECT FOR UPDATE", "• Partial Unique Index", "• Non-Root Container"], accent=ACCENT_GREEN)
    draw_card(ax, 74, 18, 20, 18, "Audit Logs Store", ["• Append-Only Storage", "• Non-Repudiation Trail", "• IP / Actor / Metadata"], accent=ACCENT_ROSE)

    # Connections across boundaries
    draw_arrow(ax, 28, 64, 39, 64, "HTTPS + HttpOnly", color=ACCENT_BLUE)
    draw_arrow(ax, 64, 64, 74, 64, "SQLAlchemy (TLS)", color=ACCENT_GREEN)

    save_diagram(fig, "trust-boundary-diagram")

# ==============================================================================
# 10. SYSTEM ARCHITECTURE
# ==============================================================================
def render_system_architecture():
    fig, ax = setup_canvas("Full-Stack Layered System Architecture", "Presentation, API Gateway, Service Layer & Relational Persistence Engine")

    layers = [
        ("Layer 1: Presentation Tier (React 18 + Vite + TypeScript)", 6, 73, 88, 14, [
            "• Single Page Application Client | React Router v6 | Midnight Indigo Glassmorphic Design System",
            "• AuthContext (In-Memory State, Zero LocalStorage Tokens) | 12 Role-Governed Functional Views"
        ], ACCENT_BLUE),
        ("Layer 2: API Gateway & Security Perimeter (FastAPI 0.115)", 6, 53, 88, 14, [
            "• Asynchronous REST Endpoints | In-Memory Sliding-Window IP Rate Limiting (5 req/min)",
            "• OWASP Security Headers (CSP, HSTS, X-Frame: DENY) | Strict CORS Whitelisting"
        ], ACCENT_INDIGO),
        ("Layer 3: Business Logic & Authorization Tier", 6, 33, 88, 14, [
            "• Declarative RBAC Engine (require_roles) | Object-Level Ownership Validator (IDOR Mitigation)",
            "• Atomic Registration Concurrency Coordinator | Centralized Security Audit Emitter"
        ], ACCENT_AMBER),
        ("Layer 4: Relational Data Persistence Tier (PostgreSQL 16 Engine)", 6, 13, 88, 14, [
            "• SQLAlchemy 2.0 ORM with Connection Pooling | Pessimistic Row-Level Locking (with_for_update)",
            "• Partial Unique Index (uq_event_student_active) | Immutable Append-Only Audit Table"
        ], ACCENT_GREEN)
    ]
    for title, x, y, w, h, lines, col in layers:
        draw_card(ax, x, y, w, h, title, lines, accent=col)
        if y > 13:
            draw_arrow(ax, 50, y, 50, y - 6, color=TEXT_MUTED)

    save_diagram(fig, "system-architecture")

# ==============================================================================
# 11. COMPONENT DIAGRAM
# ==============================================================================
def render_component_diagram():
    fig, ax = setup_canvas("UML Component Diagram", "Modular Service Architecture, Component Interfaces & Dependencies")

    draw_card(ax, 5, 33, 25, 48, "Frontend Component (SPA)", [
        "React Pages:",
        "• LoginPage (Demo Presets)",
        "• StudentDashboard",
        "• EventsListPage (Filters)",
        "• EventDetailPage (Quotas)",
        "• MyRegistrationsPage",
        "• FacultyDashboard",
        "• CreateEventPage",
        "• ManageEventsPage",
        "• EventParticipantsPage",
        "• AdminDashboard",
        "• AuditLogsPage"
    ], accent=ACCENT_BLUE)

    draw_card(ax, 36, 58, 28, 23, "Auth & Security Component", [
        "• AuthService (Login/Logout)",
        "• SlidingRateLimiter (In-Memory)",
        "• SecurityMiddleware (Headers)",
        "• Passlib Bcrypt (Cost=12)",
        "• PyJWT Session Validator"
    ], accent=ACCENT_INDIGO)

    draw_card(ax, 36, 32, 28, 22, "Event Management Component", [
        "• EventService (Lifecycle)",
        "• EventRouter (REST /api/events)",
        "• Pydantic Schemas (Boundary)",
        "• Object Ownership Validator"
    ], accent=ACCENT_AMBER)

    draw_card(ax, 36, 6, 28, 22, "Registration Component", [
        "• RegistrationService (Core)",
        "• Concurrency Row Lock Engine",
        "• Partial Unique Index Guard",
        "• Capacity Quota Calculator"
    ], accent=ACCENT_PURPLE)

    draw_card(ax, 71, 46, 24, 26, "Audit & Admin Component", [
        "• AdminService (User/Role)",
        "• AuditService (Append-Only)",
        "• HealthCheck (/health)",
        "• Security Metric Aggregator"
    ], accent=ACCENT_ROSE)

    draw_card(ax, 71, 10, 24, 26, "Database Component", [
        "• PostgreSQL 16 Alpine",
        "• SQLAlchemy Session Factory",
        "• Partial Unique Constraints",
        "• Connection Pool (Size=10)"
    ], accent=ACCENT_GREEN)

    # Connections
    draw_arrow(ax, 30, 68, 36, 68, color=ACCENT_INDIGO)
    draw_arrow(ax, 30, 44, 36, 44, color=ACCENT_AMBER)
    draw_arrow(ax, 30, 20, 36, 18, color=ACCENT_PURPLE)
    draw_arrow(ax, 64, 45, 71, 56, color=ACCENT_ROSE)
    draw_arrow(ax, 64, 18, 71, 22, color=ACCENT_GREEN)

    save_diagram(fig, "component-diagram")

# ==============================================================================
# 12. DEPLOYMENT DIAGRAM
# ==============================================================================
def render_deployment_diagram():
    fig, ax = setup_canvas("Kubernetes Deployment Architecture", "Pod Topology, Namespace Isolation, StatefulSets & Secret Management")

    node_box = FancyBboxPatch((5, 6), 90, 82, boxstyle="round,pad=1.5", facecolor="#0e172a", edgecolor=ACCENT_BLUE, linewidth=2, zorder=1)
    ax.add_patch(node_box)
    ax.text(50, 85.5, "KUBERNETES CLUSTER (NAMESPACE: EVENT-REG-SYSTEM)", fontsize=11, fontweight="bold", color=ACCENT_BLUE, ha="center")

    # Pods
    draw_card(ax, 9, 48, 25, 29, "Pod: frontend-deployment", [
        "ReplicaSet: 2 Pods",
        "Container: Nginx Alpine",
        "Port: 80 / ClusterIP: 3000",
        "SecurityContext:",
        "  runAsNonRoot: true",
        "  readOnlyRootFilesystem"
    ], accent=ACCENT_BLUE)

    draw_card(ax, 38, 48, 27, 29, "Pod: backend-deployment", [
        "ReplicaSet: 2 Pods",
        "Container: Python 3.11",
        "FastAPI Uvicorn (Port 8000)",
        "SecurityContext:",
        "  runAsUser: 10001",
        "  allowPrivEscalation: false",
        "Limits: 500m CPU, 512MiB"
    ], accent=ACCENT_INDIGO)

    draw_card(ax, 69, 48, 22, 29, "Pod: postgres-statefulset", [
        "StatefulSet: 1 Pod",
        "PostgreSQL 16 Alpine",
        "Port: 5432 (Internal)",
        "PVC: postgres_data",
        "Health: pg_isready",
        "Volume Mount: Persistent"
    ], accent=ACCENT_GREEN)

    # Config / Secrets
    draw_card(ax, 22, 13, 26, 21, "ConfigMap (eventhub-config)", [
        "• ENVIRONMENT: production",
        "• COOKIE_SAMESITE: lax",
        "• ALLOWED_ORIGINS: domain",
        "• API_PREFIX: /api"
    ], accent=ACCENT_AMBER)

    draw_card(ax, 54, 13, 26, 21, "Secret (backend-secrets)", [
        "• SECRET_KEY: [256-bit encrypted]",
        "• POSTGRES_PASSWORD: [env]",
        "• JWT_ALGORITHM: HS256",
        "• Zero plaintext in source code"
    ], accent=ACCENT_ROSE)

    # Connectors
    draw_arrow(ax, 34, 62, 38, 62, "Proxy /api", color=ACCENT_BLUE)
    draw_arrow(ax, 65, 62, 69, 62, "TCP 5432 (TLS)", color=ACCENT_GREEN)

    save_diagram(fig, "deployment-diagram")

# ==============================================================================
# 13. INFORMATION FLOW DIAGRAM
# ==============================================================================
def render_information_flow_diagram():
    fig, ax = setup_canvas("Sensitive Information Flow & Cryptographic Boundary Diagram", "PII Isolation, Token Lifecycle, Audit Directionality & Credential Sanitization")

    flows = [
        ("Asset 1: User Passwords", 6, 67, 27, 21, [
            "• Plaintext input in Browser",
            "• Encrypted via TLS 1.3 in transit",
            "• Bcrypt hashed (cost=12)",
            "• Never returned in API / logged"
        ], ACCENT_BLUE),
        ("Asset 2: Session JWT Token", 37, 67, 27, 21, [
            "• Issued upon valid login",
            "• Stored in HttpOnly cookie",
            "• Signed with HS256 (256-bit key)",
            "• Expires in 120 minutes"
        ], ACCENT_INDIGO),
        ("Asset 3: Participant Rosters", 68, 67, 26, 21, [
            "• Student Names & Emails",
            "• Isolated to Event Organizer",
            "• Barred from students/public",
            "• Subject to object auth check"
        ], ACCENT_AMBER),
        ("Asset 4: Security Audit Logs", 21, 18, 27, 21, [
            "• Immutable append-only log",
            "• Captures Actor, IP, Action, Time",
            "• Passwords/tokens sanitized",
            "• Admin-only query access"
        ], ACCENT_ROSE),
        ("Asset 5: Database Credentials", 53, 18, 27, 21, [
            "• Injected via .env / K8s Secret",
            "• Barred from Git repositories",
            "• Parameterized ORM execution",
            "• Unprivileged connection pool"
        ], ACCENT_GREEN)
    ]
    for title, x, y, w, h, lines, col in flows:
        draw_card(ax, x, y, w, h, title, lines, accent=col)

    draw_arrow(ax, 33, 77, 37, 77, color=ACCENT_BLUE)
    draw_arrow(ax, 64, 77, 68, 77, color=ACCENT_INDIGO)
    draw_arrow(ax, 19, 67, 34, 39, color=ACCENT_ROSE)
    draw_arrow(ax, 50, 67, 66, 39, color=ACCENT_GREEN)

    save_diagram(fig, "information-flow-diagram")

# ==============================================================================
# 14. THREAT MODEL (STRIDE)
# ==============================================================================
def render_threat_model():
    fig, ax = setup_canvas("STRIDE Threat Model & Defense-in-Depth Mitigations", "Formal STRIDE Categorization, Identified Attack Vectors & Applied Security Controls")

    threats = [
        ("Spoofing (S)", 6, 54, 27, 34, [
            "Identified Threats:",
            "• Credential brute-force attack",
            "• Student identity impersonation",
            "Applied Mitigations:",
            "• Passlib Bcrypt hashing (cost=12)",
            "• 5 req/min sliding rate limiter",
            "• Identity from JWT sub claims"
        ], ACCENT_BLUE),
        ("Tampering (T)", 36, 54, 28, 34, [
            "Identified Threats:",
            "• Race-condition overbooking",
            "• Duplicate active registrations",
            "Applied Mitigations:",
            "• Pessimistic lock (FOR UPDATE)",
            "• Partial unique index (uq_active)",
            "• Atomic database transaction"
        ], ACCENT_AMBER),
        ("Repudiation (R)", 67, 54, 27, 34, [
            "Identified Threats:",
            "• Denying event registration",
            "• Denying unauthorized event edits",
            "Applied Mitigations:",
            "• Immutable audit_logs table",
            "• Captures IP, Actor, Timestamp",
            "• Non-repudiation security trail"
        ], ACCENT_GREEN),
        ("Information Disclosure (I)", 6, 11, 27, 34, [
            "Identified Threats:",
            "• Cross-faculty roster leakage",
            "• Password hash in API responses",
            "Applied Mitigations:",
            "• Object authorizer: organizer_id",
            "• Pydantic UserOut excludes hash",
            "• Tokens in HttpOnly cookies"
        ], ACCENT_ROSE),
        ("Denial of Service (D)", 36, 11, 28, 34, [
            "Identified Threats:",
            "• Auth endpoint volumetric flood",
            "• Malformed payload thread hang",
            "Applied Mitigations:",
            "• Sliding-window rate limiter",
            "• Pydantic boundary validation",
            "• K8s Pod CPU/memory quotas"
        ], ACCENT_PURPLE),
        ("Elevation of Privilege (E)", 67, 11, 27, 34, [
            "Identified Threats:",
            "• Student creates campus event",
            "• IDOR registration cancellation",
            "Applied Mitigations:",
            "• require_roles([FACULTY, ADMIN])",
            "• reg.student_id == user.id check",
            "• Administrative endpoint guards"
        ], ACCENT_BLUE)
    ]
    for title, x, y, w, h, lines, col in threats:
        draw_card(ax, x, y, w, h, title, lines, accent=col)

    save_diagram(fig, "threat-model")

# ==============================================================================
# 15. ATTACK TREE
# ==============================================================================
def render_attack_tree():
    fig, ax = setup_canvas("Attack Tree: Compromise Event Registration Integrity", "Hierarchical Tree: Root Goal -> Sub-Goals -> Attack Vectors -> Defense-in-Depth Controls")

    # Level 0: Root Goal (Red prominent card at top)
    draw_card(ax, 26, 78, 48, 12, "ROOT ATTACK GOAL [LOGICAL OR]", [
        "COMPROMISE EVENT REGISTRATION INTEGRITY",
        "(Unauthorized Bookings, Quota Tampering, or Attendee Exfiltration)"
    ], accent=ACCENT_ROSE, bg="#281216", title_bg="#451218")

    # Level 1: Sub-Goals
    vectors = [
        ("Sub-Goal 1: Auth & Credential Abuse", 5, 48, 28, 18, [
            "• Credential stuffing attacks",
            "• Session token interception",
            "• Student account takeover"
        ], ACCENT_BLUE),
        ("Sub-Goal 2: Concurrency & TOCTOU Race", 36, 48, 28, 18, [
            "• Concurrent multi-thread flood",
            "• Breach participant_limit ceiling",
            "• Insert duplicate active seats"
        ], ACCENT_AMBER),
        ("Sub-Goal 3: IDOR & Authorization Flaws", 67, 48, 28, 18, [
            "• Cancel another student's booking",
            "• Harvest other faculty rosters",
            "• Student creates campus events"
        ], ACCENT_PURPLE)
    ]
    for title, x, y, w, h, lines, col in vectors:
        draw_card(ax, x, y, w, h, title, lines, accent=col)
        draw_arrow(ax, 50, 78, x + w/2, y + h, color=ACCENT_ROSE)

    # Level 2: Mitigating Controls
    controls = [
        ("Controls: Authentication", 5, 12, 28, 26, [
            "Preventive:",
            "• Passlib Bcrypt cost=12 hashing",
            "• 5 req/min sliding rate limiter",
            "• HttpOnly SameSite=Lax cookie",
            "Detective: Audit LOGIN_FAILURE",
            "Corrective: Temporary IP block"
        ], ACCENT_GREEN),
        ("Controls: Concurrency", 36, 12, 28, 26, [
            "Preventive:",
            "• SELECT ... FOR UPDATE row lock",
            "• Atomic database transaction",
            "• Partial Unique Index (uq_active)",
            "Detective: Anomaly count monitor",
            "Corrective: DB transaction rollback"
        ], ACCENT_GREEN),
        ("Controls: Authorization", 67, 12, 28, 26, [
            "Preventive:",
            "• Server-side object ownership check",
            "• Declarative require_roles RBAC",
            "• Pydantic schema field exclusion",
            "Detective: Audit UNAUTHORIZED",
            "Corrective: HTTP 403 Forbidden"
        ], ACCENT_GREEN)
    ]
    for title, x, y, w, h, lines, col in controls:
        draw_card(ax, x, y, w, h, title, lines, accent=col)
        draw_arrow(ax, x + w/2, 48, x + w/2, y + h, color=ACCENT_GREEN)

    save_diagram(fig, "attack-tree")

# ==============================================================================
# 16. SECURITY ARCHITECTURE REFINEMENT
# ==============================================================================
def render_security_architecture():
    fig, ax = setup_canvas("Security Architecture & Defense-in-Depth Refinement", "Multi-Tier Security Architecture: Perimeter, Identity, Application & Data Controls")

    shields = [
        ("Perimeter & Edge Defense Tier", 6, 56, 42, 31, [
            "Security Controls:",
            "• TLS 1.3 Transport Encryption with HSTS",
            "• Strict-Transport-Security & Referrer-Policy",
            "• Content-Security-Policy & X-Frame: DENY",
            "• In-Memory Sliding-Window IP Rate Limiter",
            "• Strict CORS Origin Whitelisting"
        ], ACCENT_BLUE),
        ("Identity, Session & Auth Tier", 52, 56, 42, 31, [
            "Security Controls:",
            "• Passlib Bcrypt password hashing (cost=12)",
            "• Stateless JWT signed with HMAC-SHA256",
            "• Delivered strictly via HttpOnly Secure cookies",
            "• Zero token persistence in browser localStorage",
            "• Clean cookie invalidation upon logout"
        ], ACCENT_INDIGO),
        ("Application & Logic Defense Tier", 6, 13, 42, 32, [
            "Security Controls:",
            "• Declarative RBAC via FastAPI require_roles",
            "• Server-side object-level ownership validation",
            "• Insecure Direct Object Reference (IDOR) defense",
            "• Strict Pydantic v2 input boundary validation",
            "• Sanitized RFC 7807 error responses"
        ], ACCENT_AMBER),
        ("Data & Infrastructure Defense Tier", 52, 13, 42, 32, [
            "Security Controls:",
            "• ACID Transactional row locks (FOR UPDATE)",
            "• Partial Unique Index (uq_event_student_active)",
            "• Dedicated non-root container (appuser:10001)",
            "• Kubernetes securityContext & dropped capabilities",
            "• Immutable append-only audit_logs persistence"
        ], ACCENT_GREEN)
    ]
    for title, x, y, w, h, lines, col in shields:
        draw_card(ax, x, y, w, h, title, lines, accent=col)

    save_diagram(fig, "security-architecture")

def main():
    print(f"Beginning high-resolution rendering of all 16 diagram image suites into {OUTPUT_DIR}...")
    render_use_case_diagram()
    render_class_diagram()
    render_sequence_login()
    render_sequence_registration()
    render_activity_registration()
    render_er_diagram()
    render_dfd_level_0()
    render_dfd_level_1()
    render_trust_boundary_diagram()
    render_system_architecture()
    render_component_diagram()
    render_deployment_diagram()
    render_information_flow_diagram()
    render_threat_model()
    render_attack_tree()
    render_security_architecture()
    print("ALL 16 DIAGRAM IMAGE SUITES PROFESSIONALLY RENDERED AS PNG AND SVG!")

if __name__ == "__main__":
    main()
