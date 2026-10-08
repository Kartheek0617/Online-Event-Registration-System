# Phase 13: Docker Containerization & Kubernetes Orchestration

## 1. Overview & Cloud-Native Security Strategy

Containerization and orchestration for the **Online Event Registration System (EventHub)** adhere to the principle of least privilege, defense-in-depth, immutable infrastructure, and strict runtime isolation. The system is packaged into minimal, multi-stage Docker containers and managed via Kubernetes manifests engineered for local execution on Minikube or enterprise-grade managed clusters (EKS/GKE/AKS).

---

## 2. Docker Architecture & Hardening Controls

### 2.1 Backend Dockerfile ([backend/Dockerfile](file:///d:/Kartheek/WAS/SSE/backend/Dockerfile))
- **Base Image:** Minimal `python:3.11-slim` image eliminating development tools (compilers, debuggers).
- **Non-Root Execution:** Dedicated unprivileged user `appuser` (`uid: 10001`, `gid: 10001`) created with `--no-create-home`. The container process never executes as root.
- **Port Control:** Exposes strictly TCP port `8000`.
- **Filesystem Permissions:** Application files are copied into `/app` with ownership assigned to `appuser:10001`.
- **Zero Embedded Secrets:** Configuration is strictly injected via environment variables at container instantiation time.
- **Health Check:** Embedded `HEALTHCHECK` running `curl -f http://localhost:8000/health || exit 1`.

### 2.2 Frontend Dockerfile ([frontend/Dockerfile](file:///d:/Kartheek/WAS/SSE/frontend/Dockerfile))
- **Multi-Stage Build:**
  - *Stage 1 (Builder):* Uses `node:20-alpine` to install dependencies and execute `npm run build`, producing optimized static assets in `/app/dist`.
  - *Stage 2 (Runtime):* Uses `nginx:alpine` to serve static assets; Node.js runtimes, package managers, and development dependencies are discarded from the production image.
- **Hardened Nginx Configuration ([frontend/nginx.conf](file:///d:/Kartheek/WAS/SSE/frontend/nginx.conf)):**
  - Serves Single Page Application with fallback to `/index.html`.
  - Injects OWASP security headers (`X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Content-Security-Policy`).
  - Proxies `/api/` traffic to the backend service.

### 2.3 Multi-Service Orchestration ([docker-compose.yml](file:///d:/Kartheek/WAS/SSE/docker-compose.yml))
The compose configuration coordinates three isolated services on an internal bridge network `eventhub-net`:
1. `db`: PostgreSQL 16 Alpine with health check `pg_isready -U postgres` and persistent volume `postgres_data`.
2. `backend`: FastAPI backend depending on healthy database condition with automatic database seeding.
3. `frontend`: Nginx web server mapping port 80/3000 depending on backend availability.

---

## 3. Kubernetes Orchestration & Security Architecture

All Kubernetes manifests are located in [k8s/](file:///d:/Kartheek/WAS/SSE/k8s/) and configured for the isolated namespace `event-reg-system`.

```
                  ┌──────────────────────────────────────────────┐
                  │       Namespace: event-reg-system            │
                  │                                              │
 [Ingress / NodePort] ──► [Frontend Service (Port 80)]           │
                  │              │                               │
                  │              ▼                               │
                  │      [Frontend Pods (x2)]                    │
                  │              │                               │
                  │              ▼                               │
                  │    [Backend Service (Port 8000)]             │
                  │              │                               │
                  │              ▼                               │
                  │      [Backend Pods (x2)]                     │
                  │              │ (TLS / TCP 5432)              │
                  │              ▼                               │
                  │  [Postgres StatefulSet (x1)]                 │
                  │              │                               │
                  │              ▼                               │
                  │      [PersistentVolumeClaim]                 │
                  └──────────────────────────────────────────────┘
```

### 3.1 Implemented Kubernetes Security Controls
1. **Namespace Isolation ([k8s/namespace.yaml](file:///d:/Kartheek/WAS/SSE/k8s/namespace.yaml)):** Segregates all resources into `event-reg-system` preventing accidental cross-tenant interaction with default namespace workloads.
2. **Pod Security Context ([k8s/backend-deployment.yaml](file:///d:/Kartheek/WAS/SSE/k8s/backend-deployment.yaml)):**
   - `runAsNonRoot: true`
   - `runAsUser: 10001`
   - `allowPrivilegeEscalation: false`
   - `capabilities: drop: ["ALL"]`
3. **Resource Limits & Requests:**
   - Backend Pods: CPU request `100m` / limit `500m`, Memory request `128Mi` / limit `512Mi`. Prevents "noisy neighbor" resource exhaustion attacks (DoS).
4. **Secret Decoupling ([k8s/secret.example.yaml](file:///d:/Kartheek/WAS/SSE/k8s/secret.example.yaml)):** Sensitive keys (`SECRET_KEY`, `POSTGRES_PASSWORD`) are mounted as Kubernetes `Secret` references and never committed to source control.
5. **Readiness & Liveness Probes:** Both backend and database configurations define HTTP/exec probes ensuring traffic is only routed to healthy pods.

---

## 4. Operational Execution Commands

### 4.1 Local Docker Compose Execution
```bash
# 1. Build and start all services in detached mode
docker compose up -d --build

# 2. Inspect container status and health
docker compose ps

# 3. View streaming logs
docker compose logs -f backend

# 4. Tear down containers and networks
docker compose down -v
```

### 4.2 Minikube / Kubernetes Deployment Workflow
```bash
# 1. Start Minikube cluster
minikube start --driver=docker --cpus=4 --memory=8192

# 2. Create target namespace
kubectl apply -f k8s/namespace.yaml

# 3. Create Secret from example template
kubectl create secret generic backend-secrets \
  --namespace=event-reg-system \
  --from-literal=SECRET_KEY="super-secret-cryptographic-key-change-me" \
  --from-literal=POSTGRES_PASSWORD="secure-postgres-password"

# 4. Apply ConfigMap and Database StatefulSet
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/postgres-statefulset.yaml

# 5. Wait for database readiness
kubectl rollout status statefulset/postgres-db -n event-reg-system

# 6. Deploy Backend and Frontend Workloads
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml

# 7. Verify All Pods Running and Healthy
kubectl get pods -n event-reg-system -o wide

# 8. Access Frontend via Minikube Service URL
minikube service frontend-service -n event-reg-system
```
