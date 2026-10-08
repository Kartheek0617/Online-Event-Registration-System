# Production & Local Deployment Operations Guide

## 1. Overview

This guide details the step-by-step deployment procedures for the **Online Event Registration System (EventHub)** across three deployment targets:
1. **Local Development (Bare-Metal / Hybrid)**
2. **Containerized Multi-Service (Docker Compose)**
3. **Cloud-Native Cluster (Kubernetes / Minikube)**

---

## 2. Target 1: Local Development Setup

### 2.1 Prerequisites
- Python 3.11+
- Node.js 18+ (Node 20 / 22 recommended)
- PostgreSQL 16 (Optional: application automatically falls back to local SQLite if PostgreSQL is unreachable)

### 2.2 Backend Setup & Execution
```bash
# 1. Navigate to backend directory
cd backend

# 2. Create and activate virtual environment (optional but recommended)
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# 3. Install pinned dependencies
pip install -r requirements.txt

# 4. Copy configuration template
cp ../.env.example ../.env

# 5. Seed the database with demo accounts & events
python -m app.seed

# 6. Start the FastAPI development server
python run.py
# Server starts at: http://localhost:8000
# OpenAPI documentation: http://localhost:8000/docs
```

### 2.3 Frontend Setup & Execution
```bash
# 1. Open a new terminal and navigate to frontend directory
cd frontend

# 2. Install Node dependencies
npm install

# 3. Start Vite development server
npm run dev
# Web application available at: http://localhost:5173
```

---

## 3. Target 2: Docker Compose Multi-Service Deployment

### 3.1 Preparation
1. Ensure Docker Desktop / Docker Engine is running.
2. Verify [.env.example](file:///d:/Kartheek/WAS/SSE/.env.example) is duplicated as `.env`:
   ```bash
   cp .env.example .env
   ```

### 3.2 Build & Execution
```bash
# 1. Build and launch all three services (Postgres, Backend, Frontend)
docker compose up -d --build

# 2. Inspect container status and health
docker compose ps

# Output should show:
# - eventhub_db (healthy) on port 5432
# - eventhub_backend (healthy) on port 8000
# - eventhub_frontend (healthy) on port 3000 / 80

# 3. Inspect real-time backend logs
docker compose logs -f backend

# 4. Access Web Interface
# Open browser to: http://localhost:3000
```

### 3.3 Tear Down & Volume Management
```bash
# Stop containers and preserve database volume:
docker compose down

# Stop containers and wipe database volume (clean reset):
docker compose down -v
```

---

## 4. Target 3: Kubernetes / Minikube Orchestration

All manifests are configured in [k8s/](file:///d:/Kartheek/WAS/SSE/k8s/) and enforce namespace isolation under `event-reg-system`.

### 4.1 Cluster Initialization
```bash
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --driver=docker
```

### 4.2 Provisioning Manifests
```bash
# 1. Create isolated namespace
kubectl apply -f k8s/namespace.yaml

# 2. Provision Kubernetes Secrets (Do not commit plaintext secret to VCS)
kubectl create secret generic backend-secrets \
  --namespace=event-reg-system \
  --from-literal=SECRET_KEY="cryptographically-secure-random-key-32-chars-min" \
  --from-literal=POSTGRES_PASSWORD="secure-production-db-password"

# 3. Apply ConfigMap and Database StatefulSet
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/postgres-statefulset.yaml

# 4. Wait for database pod to become Ready
kubectl rollout status statefulset/postgres-db -n event-reg-system --timeout=120s

# 5. Apply Backend and Frontend Deployments
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml

# 6. Verify Pod Status
kubectl get pods -n event-reg-system
```

### 4.3 Accessing the Application
```bash
# Direct Minikube service tunneling:
minikube service frontend-service -n event-reg-system

# Or Port-Forwarding:
kubectl port-forward svc/frontend-service 3000:80 -n event-reg-system
# Web UI accessible at: http://localhost:3000
```

---

## 5. Academic Demonstration Credentials

The database seeder automatically initializes the following accounts:

| Role | Email Address | Password | Permissions & Dashboard Scope |
| :--- | :--- | :--- | :--- |
| **Student** | `student@college.edu` | `Student@123` | Browse events, view details, register, cancel own registrations. |
| **Faculty 1** | `faculty@college.edu` | `Faculty@123` | Create events, set quotas, view attendees of own events, close registration. |
| **Faculty 2** | `faculty2@college.edu` | `Faculty@123` | Second coordinator used to test cross-faculty IDOR isolation. |
| **Admin** | `admin@college.edu` | `Admin@123` | System oversight, role management, security audit log inspector. |
| **Guest** | *Unauthenticated* | *N/A* | Public browsing of event listings only. |
