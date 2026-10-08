# Phase 11: Secure Development and Build

## 1. Overview & Repository Strategy

Secure software engineering requires that security controls are not merely applied post-development, but integrated into source control workflows, build pipelines, and configuration management. This document defines the branching strategy, access governance, secret prevention mechanisms, dependency supply chain controls, and static security scanning results for the **Online Event Registration System**.

---

## 2. Git Branching Model & Workflow

The repository adheres to a hardened GitFlow branching strategy:

```
[feature/US-01-auth] ────┐ (PR + Review + CI)
                         ▼
[develop] ────────────────────────────────────────► [main] (Production Releases / Tagged)
                         ▲
[feature/US-07-reg] ─────┘ (PR + Review + CI)
```

### 2.1 Branch Topology & Purpose
1. **`main` (Production Branch):**
   - Represents verified, deployable production artifacts.
   - Strictly protected; direct commits and force-pushes (`git push --force`) are disabled.
   - Merges permitted strictly via Pull Requests from `develop` accompanied by green CI checks and cryptographic release tagging (e.g., `v1.0.0`).
2. **`develop` (Integration Branch):**
   - Aggregates validated feature branches for integration testing.
   - Requires automated CI passes (unit tests, integration tests, SAST scans) prior to merge.
3. **`feature/*` (Topic Branches):**
   - Named semantically: `feature/US-<ID>-<short-description>` (e.g., `feature/US-07-atomic-registration`).
   - Short-lived, rebased frequently against `develop` to minimize merge conflicts.

---

## 3. Core Secure Development Principles

### 3.1 Least Privilege
- Developers possess write access solely to feature branches and pull request creation.
- Service accounts used in CI/CD pipelines are provisioned with repository-scoped, read-only permissions for source checkout and tightly bounded tokens for publishing images.
- Database credentials in production restrict DDL access during runtime application execution.

### 3.2 Secret Management & Zero-Secret Policy
- **Absolute Rule:** Secrets, private keys, database passwords, and JWT secret keys MUST NEVER be committed to Git.
- A standardized template [.env.example](file:///d:/Kartheek/WAS/SSE/.env.example) is committed to document required environment variables without providing real credentials.
- [.gitignore](file:///d:/Kartheek/WAS/SSE/.gitignore) rigorously excludes:
  - `.env`, `.env.local`, `.env.*.local`
  - `*.pem`, `*.key`, `*.cert`
  - SQLite development files (`*.db`, `*.sqlite3`)
  - Node modules and Python virtual environments (`__pycache__`, `venv/`, `dist/`)

### 3.3 Dependency Supply Chain Control
- Dependencies are pinned with strict or compatible release specifiers in `requirements.txt` and `package-lock.json`.
- Python dependencies leverage cryptographic hash checking via `pip` and auditing via `pip-audit`.
- Frontend dependencies are scanned via `npm audit` during every build cycle.

### 3.4 Mandatory Peer Code Review
- All pull requests require at least one mandatory code review approval from a peer engineer.
- Review checklist specifically enforces:
  - Verification of object-level authorization (IDOR checks on event IDs and registration IDs).
  - Parameterized ORM queries only (no raw string formatting in SQL).
  - Absence of sensitive parameters in log statements.

### 3.5 Protected Branches Configuration
- Required status checks:
  - Backend pytest suite (100% pass required).
  - Frontend TypeScript compilation and Vite build (`npm run build`).
  - SAST scanner clean pass (zero High or Critical vulnerabilities).
- Branch protection rules prohibit administrative bypass.

### 3.6 Reproducible Builds & Artifact Integrity
- Container images are generated using deterministic multi-stage Dockerfiles.
- Base images are pinned to specific distribution versions (e.g., `python:3.11-slim`, `node:20-alpine`, `nginx:alpine`).
- Production frontend static assets are bundled into immutable, content-hashed bundles.

### 3.7 Environment Separation
- Three distinct environments are maintained:
  - **Development:** Local Docker Compose or lightweight SQLite fallback for isolated feature development.
  - **Testing/CI:** Ephemeral PostgreSQL container or memory-isolated SQLite instance for deterministic test runs.
  - **Production/K8s:** Hardened Kubernetes namespace (`event-reg-system`) with ConfigMaps and Secrets injected securely from external secret stores.

---

## 4. Automated Static & Dependency Security Scans

### 4.1 Dependency Audit (NPM Audit)
During build verification of the React frontend, `npm audit` was executed:
- **Scan Command:** `npm audit`
- **Identified Finding 1:**
  - **Component:** `esbuild <= 0.24.2` (Vite dev server dependency)
  - **Advisory:** GHSA-67mh-4wv8-2f99 (Moderate)
  - **Description:** Development server CORS reading vulnerability under specific localhost multi-tab environments.
  - **Remediation & Analysis:** The finding affects local Vite dev server HMR and does not impact the production distribution artifact, which compiles static files served via hardened Nginx. For development, upstream Vite upgrade patch path is documented.
- **Identified Finding 2:**
  - **Component:** `react-router`
  - **Advisory:** GHSA-wrjc-x8rr-h8h6 / CVE-2025-68470
  - **Description:** Open redirect via backslash in `<Link>` component.
  - **Remediation & Analysis:** The application uses relative path navigation exclusively with internal enum-validated routes; external redirects via query parameters are explicitly prohibited in the client router.

### 4.2 Python SAST & Security Verification (Bandit / Flake8 / Pytest)
- **Tooling:** Bandit (Python Security Linter) and Pytest security suite.
- **Verification Rule:** Zero High-severity issues allowed.
- **Bcrypt Cost Factor Finding:**
  - **Finding:** Bcrypt hashing with default work factor 12 caused high latency in automated test harnesses (147 seconds for 33 tests), leading to threadpool starvation risks during parallel execution.
  - **Remediation:** Configured environment-aware work factor in [security.py](file:///d:/Kartheek/WAS/SSE/backend/app/core/security.py) (`rounds = 4` in `test` environment, `rounds = 12` in `development` and `production`), combined with fixture-level precomputation in test suites. This brought test execution down to **1.18 seconds** without compromising production cryptographic hardness.
