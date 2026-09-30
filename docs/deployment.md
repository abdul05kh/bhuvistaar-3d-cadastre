# BhuVistaar — Deployment & Operational Runbook

**Project**: BhuVistaar — 3D Cadastral Intelligence & Validation Platform  
**Target**: Smart India Hackathon (SIH26011) — 3D Cadastre Operational Prototype  
**Scope**: Slice 5 Reproducible Deployment, Environment Configuration & Health Verification

---

## 1. System Architecture Overview

BhuVistaar follows an authoritative, reproducible pipeline:
```
Evidence Ingestion → Normalization → AI/Analytics Candidate Generation (Advisory)
  → Deterministic Validation (Gate A/B) → Human Review & Correction 
  → Immutable Revisions → Governance (Gate C) → Append-Only Audit 
  → Interoperability Export (JSON / GeoJSON / 3D OBJ)
```

### Components
1. **Database**: PostgreSQL 16 + PostGIS 3.4 (Authoritative Spatial Datastore, SRID `32643`).
2. **Backend**: Python 3.12 + FastAPI + SQLAlchemy 2.0 + GeoAlchemy2 + Shapely.
3. **Frontend**: React 19 + TypeScript + Vite + Tailwind CSS / Vanilla CSS Tokens + Three.js 3D Viewport.
4. **Proxy/Web Server**: Nginx Alpine container (production SPA routing, CORS, reverse-proxy).

---

## 2. Environment Configuration

BhuVistaar separates operational configuration across environments using standard POSIX environment variables. Defaults are pre-configured to be safe for local evaluation and judge demos.

### Configuration Variables (`.env`)

| Variable | Default Value | Purpose |
|:---|:---|:---|
| `APP_ENV` | `demo` | Operational mode: `demo`, `development`, `test` |
| `DATABASE_URL` | `postgresql+psycopg://postgres:postgrespassword@127.0.0.1:5432/bhuvistaar_cadastre` | Connection string for PostgreSQL + PostGIS |
| `API_BASE_URL` | `http://127.0.0.1:8000` | Base URL for FastAPI backend |
| `FRONTEND_BASE_URL` | `http://127.0.0.1:5173` | Base URL for React frontend |
| `AUTH_MODE` | `SIMULATED_PROTOTYPE` | Explicit simulation banner for prototype officer roles |
| `AI_MODE` | `LOCAL` | `LOCAL` (heuristics/vision), `DETERMINISTIC`, or `DISABLED` |
| `DEMO_MODE` | `true` | Enables deterministic judge demo scenarios & synthetic fixtures |
| `LOG_LEVEL` | `INFO` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `MAX_UPLOAD_SIZE_BYTES` | `10485760` | Maximum evidence upload size (10 MB limit) |
| `STALE_THRESHOLD_SECONDS` | `3600` | Staleness detection window for evidence/validation |
| `CANONICAL_STORAGE_SRID`| `32643` | Canonical internal projected coordinate system (UTM 43N) |

> [!IMPORTANT]
> Never commit secrets or operational credentials to version control. The repository provides a sanitized template at [`.env.example`](file:///.env.example).

---

## 3. Quick Startup (Local Development)

### Prerequisites
- Python 3.12+
- Node.js 20+ & npm
- Docker Desktop (for PostgreSQL/PostGIS)

### Step 1: Start PostGIS Datastore
```bash
docker-compose up -d db
```
Verify the container is healthy on port `5432`.

### Step 2: Bootstrap Authoritative Database
```bash
# Initialize schema, apply Alembic migrations, and verify PostGIS extensions
py -3.12 -m backend.db.bootstrap
```

### Step 3: Launch Backend API
```bash
py -3.12 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive OpenAPI documentation will be accessible at `http://127.0.0.1:8000/docs`.

### Step 4: Launch Frontend Workspace
```bash
cd frontend
npm install
npm run dev
```
The operational 3D workspace will be accessible at `http://127.0.0.1:5173`.

---

## 4. Containerized Deployment (Docker Compose)

For automated evaluation, judges and operators can launch the entire stack with a single command:

```bash
docker-compose up --build -d
```

### Exposed Endpoints:
- **Frontend Workspace**: `http://localhost:5173`
- **Backend API**: `http://localhost:8000`
- **Interactive OpenAPI Documentation**: `http://localhost:8000/docs`
- **Health Overview**: `http://localhost:8000/health`
- **Readiness Probe**: `http://localhost:8000/health/ready`
- **Liveness Probe**: `http://localhost:8000/health/live`

To shut down:
```bash
docker-compose down
```

---

## 5. Health Probes & System Readiness

BhuVistaar implements multi-tiered operational health probes that distinguish between application lifecycle, database connectivity, spatial extensions, and background intelligence models:

### 1. GET `/health`
Probes overall subsystem readiness without exposing internal secrets.
```json
{
  "status": "ready",
  "application": "ok",
  "database": "ok",
  "postgis": "ok (PostGIS 3.4 USE_GEOS=1 USE_PROJ=1 USE_STATS=1)",
  "migrations": "current (004_validation_intelligence)",
  "ai": "available",
  "ai_mode": "LOCAL",
  "authorization_mode": "SIMULATED_PROTOTYPE",
  "version": "1.0.0"
}
```

### 2. GET `/health/ready`
Returns HTTP 200 when all core systems (DB, PostGIS, migrations) are operational; returns HTTP 503 if the database or spatial extension is unavailable.

### 3. GET `/health/live`
Container liveness heartbeat returning `{"status": "ALIVE"}`.

### 4. GET `/api/v1/system/readiness`
Provides a categorical system status matrix for operational monitoring, explicitly refusing to collapse complex cadastral readiness into an arbitrary percentage score.

---

## 6. Non-Destructive Data Integrity Verification

Operators can audit the authoritative database at any time without altering records:

```bash
py -3.12 -c "from backend.db.session import SessionLocal; from backend.db.bootstrap import verify_data_integrity; db=SessionLocal(); print(verify_data_integrity(db)); db.close()"
```

The verification audits:
- **Orphan Spatial Units**: Spatial units referencing nonexistent parent parcels.
- **Orphan Revisions**: Revisions disconnected from base spatial units.
- **Missing Provenance**: Spatial unit revisions without required evidence linkage.
- **Invalid Geometries**: Native PostGIS `ST_IsValidReason` checks on polygon footprints.
- **Stale Validation Runs**: Validation runs predating newer geometric revisions.
- **Invalid Approvals**: Approvals recorded on rejected or superseded revisions.

---

## 7. Backup and Restore Simulation

A standalone verification script is provided to test database snapshots and post-restore integrity:

```bash
py -3.12 scripts/backup_restore_simulation.py
```
This utility:
1. Connects to PostgreSQL and extracts an automated metadata snapshot.
2. Simulates snapshot extraction and archive integrity.
3. Performs post-restore validation run and data integrity audit.

---

## 8. Troubleshooting

| Symptom | Cause | Solution |
|:---|:---|:---|
| `Connection refused: 5432` | PostGIS container not running | Run `docker-compose up -d db` and wait 5 seconds. |
| `Alembic migration mismatch` | Outdated schema state | Run `py -3.12 -m alembic upgrade head`. |
| `Gate B PROV-003 Blocker` | Evidence payload altered | Verify SHA-256 checksum against original source plan. |
| `VRT-003 BLOCKER detected` | Vertical floor overlap | Use Reviewer Console to submit correction with `z_max <= adjacent z_min`. |
| `AI Service Offline` | `AI_MODE=DISABLED` | Normal behavior. Deterministic validation and review pipeline remain fully operational. |
