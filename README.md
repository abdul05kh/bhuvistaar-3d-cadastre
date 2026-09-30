# BhuVistaar — 3D Cadastral Intelligence & Validation Platform

*Machine-assisted 3D Cadastral Extension & Validation Layer for SIH26011*  
**Built and Maintained by Team VoidBreakers**

---

> [!IMPORTANT]
> **PROTOTYPE STATUS & LEGAL DISCLAIMER**  
> BhuVistaar is an engineering prototype developed for Smart India Hackathon (SIH 2026) under Problem Statement `SIH26011` (Ministry of Rural Development / Department of Land Resources).  
> - BhuVistaar is **NOT** an official Government of India system.
> - BhuVistaar does **NOT** alter, mutate, or replace the official 14-digit ULPIN (Bhu-Aadhaar).
> - Prototype Volumetric Unique Identifiers (**VUID**) are prototype data-layer keys and are **NOT** official 3D ULPINs.
> - The platform performs deterministic geometric and vertical validation; it does **NOT** adjudicate legal land titles or ownership rights.
> - All officer authorization headers operate strictly in `SIMULATED_PROTOTYPE` mode.

---

## 🏛️ Problem Overview & Core Thesis
Conventional land records associate land rights to a flat 2D parcel polygon identified by a 14-digit **ULPIN**. However, vertical property strata—such as multi-storey apartments, basements, utility shafts, and elevated structures—cannot be disambiguated in 2D space without losing volumetric fidelity.

BhuVistaar introduces a structured machine-assisted layer that:
1. **Preserves the parent ULPIN** as the authoritative immutable cadastral root.
2. **Derives 3D spatial units** via deterministic extrusion and vertical stratification.
3. **Assigns deterministic prototype VUIDs** that are representation-invariant (independent of CAD drawing vertex order or polygon winding).
4. **Executes Gate A deterministic validation** (`GEO`, `VRT`, `TOP`, `ID`) to detect physical and cadastral inconsistencies (such as overlapping floor strata and boundary encroachments).
5. **Maintains unbroken provenance** linking each 3D spatial unit back to its underlying survey and architectural evidence.
6. **Enforces human review and non-destructive corrections (Slice 1B)**: Corrections spawn new revisions, regenerate VUIDs, and preserve historical candidates intact.
7. **Adjudicates Gate C approvals**: Prohibits approval if unresolved blockers or unreviewed states exist.
8. **Logs append-only audit events and outputs structured JSON exports**: Captures the entire decision context for third-party auditing.
9. **Provides an integrated 3D Cadastral Workspace (Slice 2)**: Three.js WebGL visualizer, conflict highlight box, unit inspector, revision diff, and judge walkthrough.

---

## 🛠️ Technology Stack
- **Geospatial & Computational Geometry:** Shapely 2.0, PyProj 3.8, GeoAlchemy2, NumPy
- **Authoritative Spatial Database:** PostgreSQL 16 + PostGIS 3.4 (`EPSG:32643` canonical metric storage)
- **Database Migrations:** Alembic (upgradeable, downgradeable)
- **Backend API:** FastAPI, Pydantic v2, SQLAlchemy 2.0, Uvicorn
- **Frontend Workspace (Slice 2):** React, TypeScript, Three.js (WebGL 3D Viewer), Lucide Icons, Vite
- **Quality Assurance & Verification:** Pytest, Hypothesis (property-based testing), HTTPX, TestClient

---

## 🚀 Running the System Locally

### 1. Requirements
- Python 3.12+
- Node.js 20+ & npm 10+
- Docker (for PostGIS spatial database)

### 2. Launch PostGIS Database via Docker Compose
```bash
docker compose up -d db
```

### 3. Run Database Migrations
```bash
alembic upgrade head
```

### 4. Launch Backend API (Port 8000)
```bash
py -3.12 -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
API Documentation: `http://127.0.0.1:8000/docs`

### 5. Launch Frontend 3D Workspace (Port 5173)
```bash
cd frontend
npm install
npm run dev
```
Workspace UI: `http://localhost:5173`

---

## 🧪 Verification & Automated Testing

Run the full automated test suite (38 tests covering Slice 1A, Slice 1B, and Slice 2 E2E workflow):
```bash
py -3.12 -m pytest tests/ -v
```

Execute the dedicated Slice 2 Golden Path E2E workflow test:
```bash
py -3.12 -m pytest tests/integration/test_slice2_workspace_e2e.py -v
```

Execute the CLI 17-step demonstration script:
```bash
py -3.12 scripts/demo_slice1b_governance.py
```

---

## 🎯 14-Step Judge Demonstration Flow

In the web interface (`http://localhost:5173`), click **"Judge Guide"**:
1. **Load Defect Domain:** Ingests parcel `12345678901234` with 4 floors (`B1`, `G`, `L01`, `L02`).
2. **Observe 3D Conflict:** Floor L01 (103.0m - 106.5m) collides with L02 (106.0m - 109.0m) by 0.50m. A glowing red translucent bounding box highlights the vertical conflict.
3. **Attempt Premature Approval:** Gate C immediately blocks approval with HTTP 409 Conflict.
4. **Submit Correction:** Click "Request Correction" on L01, adjust ceiling from `106.50m` $\to$ `106.00m`, and provide audit justification.
5. **Observe Revision 2:** The backend spawns Revision 2 with a new deterministic VUID (`D4A2D4`), leaving historical Revision 1 completely intact.
6. **Automatic Revalidation:** Blocker count drops to 0.
7. **Officer Review:** Click "Accept" in the Human Review workspace.
8. **Gate C Approval:** Click "Approve (Prototype Workflow)". The revision status transitions to `APPROVED`.
9. **Audit Trail & Export:** Inspect the append-only audit timeline and download the deterministic structured JSON export.

---

## 👥 Contributors & Team Attribution
Refer to [CONTRIBUTORS.md](file:///d:/projects/BhuVistaar/CONTRIBUTORS.md) for core team members, role breakdowns, and multi-author commit attribution protocol.
