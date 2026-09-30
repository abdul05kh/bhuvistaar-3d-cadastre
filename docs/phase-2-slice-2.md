# BHUVISTAAR — PHASE 2 SLICE 2 SPECIFICATION & DOCUMENTATION
## 3D Cadastral Workspace & Interactive Governance

### 1. Scope
Slice 2 implements an integrated, operational 3D cadastral workspace that exposes the authoritative Slice 1A/1B engine through an interactive enterprise interface.

**Core Principle:**
> Backend decides. Frontend visualizes, explains, and requests actions.
> The frontend never independently computes approvals, silently repairs geometries, or generates authoritative VUIDs.

---

### 2. Architecture & Modules

```
                    BHUVISTAAR 3D WORKSPACE
                    
                         ┌───────────────┐
                         │ Parcel Context│ (Parent ULPIN, UTM 43N)
                         └───────┬───────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
              3D Spatial View          Spatial Unit Inspector
         (Three.js CAD Engine)          (Elevation, Metrics, VUID)
                    │                         │
                    └────────────┬────────────┘
                                 │
                         Validation Panel (Gate A & B Issues, VRT-003)
                                 │
                    ┌────────────┴────────────┐
                    │                         │
               Evidence Panel           Revision Comparison
         (SHA-256 Checksum Proofs)       (Rev 1 vs Rev 2 Lineage)
                    │                         │
                    └────────────┬────────────┘
                                 │
                           Human Review (ACCEPT / REJECT)
                                 │
                                 ↓
                     Non-Destructive Correction
                     (Creates Revision 2, recomputes VUID)
                                 │
                                 ↓
                           Revalidation (0 Blockers)
                                 │
                                 ↓
                       Gate C Approval Adjudication
                                 │
                         Audit Timeline + Export
```

#### Implemented Modules:
- **Module A: Application Shell:** High-contrast government/enterprise dark navy theme, top indicator bar with parent ULPIN, blocker count, workflow state, and simulated prototype authorization badge.
- **Module B: 3D Cadastral Viewer:** WebGL Three.js spatial viewport rendering 40m × 30m parent parcel boundary, building footprint, 3D extruded floor prisms (B1, G, L01, L02), CAD edge outlines, camera controls (Orbit, Pan, Zoom, 2D Plan View, Iso View, Explode floors), and translucent glowing red conflict bounding box for the 0.50m VRT-003 overlap.
- **Module C: Spatial Unit Inspector:** Displays Prototype VUID (with explicit non-official disclaimer), parent ULPIN, floor elevation stratum ($z_{\min}, z_{\max}$), volumetric extrusion ($m^3$), footprint area ($m^2$), and centroid.
- **Module D: Validation / Issue Center:** Gate A and Gate B atomic issue cards, filterable by severity (`BLOCKER`, `FAILED`, `ALL`), with 3D camera focus and direct correction actions.
- **Module E: Evidence & Provenance Viewer:** Authoritative evidence cards showing document types, source references, provider, and SHA-256 cryptographic checksums.
- **Module F: Human Review Workspace:** Review justification input and decision recording (`ACCEPT`, `REQUEST_CORRECTION`, `REJECT`).
- **Module G: Correction Workflow:** Non-destructive dialog allowing reviewers to adjust vertical intervals ($z_{\max}$ from 106.50m down to 106.00m) with mandatory audit justification.
- **Module H: Revision Comparison:** Side-by-side diff table comparing historical Revision 1 (preserved, blocked) against active Revision 2 (clean, regenerated VUID, predecessor pointer).
- **Module I: Audit Timeline:** Chronological ledger of append-only audit events logging actor, action, previous/new states, and timestamps.
- **Module J: Export Center:** Live preview of structured JSON export with syntax highlighting, copy-to-clipboard, and download functionality.
- **Module K: Demo Scenario Controller:** Integrated 6-stage judge walkthrough controller and one-click database reset button.
- **Module L: UI & E2E Testing:** Automated end-to-end integration test (`tests/integration/test_slice2_workspace_e2e.py`) validating the 16-step golden path against real PostGIS.

---

### 3. Golden Demo Narrative for Judges

1. **Synthetic Parcel Ingested:** Parent ULPIN `12345678901234` loaded in EPSG:32643 with 4 candidate 3D floors (`B1`, `G`, `L01`, `L02`).
2. **Defect Detected:** Gate A validation identifies a **0.50m vertical collision** between Level L01 ($z_{\max} = 106.50\text{m}$) and Level L02 ($z_{\min} = 106.00\text{m}$). The 3D viewer displays a glowing red overlap box.
3. **Approval Prohibited:** An officer attempts approval on defective Revision 1; Gate C strictly rejects the request with HTTP 409 Conflict.
4. **Non-Destructive Correction:** The officer enters a correction adjusting L01 ceiling down to 106.00m.
5. **New Revision Created:** The backend spawns **Revision 2**, regenerates a distinct deterministic Prototype VUID (`BV-12345678901234-BLDG-L01-D4A2D4`), and preserves Revision 1 in the database.
6. **Revalidation:** Automated revalidation runs against Revision 2; blocker count drops to 0.
7. **Human Review:** The officer records an `ACCEPT` review decision.
8. **Gate C Approval:** With 0 blockers and an ACCEPT review, Gate C permits prototype workflow approval.
9. **Audit Trail & Export:** All actions appear in the append-only audit timeline, and the resulting structured JSON record is ready for export.

---

### 4. Running the Workspace

#### 1. Backend (FastAPI + PostgreSQL/PostGIS)
```bash
# Ensure Docker container is running
docker start bhuvistaar-postgis

# Run backend API
py -3.12 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

#### 2. Frontend (Vite + React)
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:5173 in browser
```

#### 3. Verification Suite
```bash
# Full test suite (38 tests)
py -3.12 -m pytest tests/ -v

# E2E Golden Path Test
py -3.12 -m pytest tests/integration/test_slice2_workspace_e2e.py -v
```

---

### 5. Known Prototype Limitations & Disclaimer

- **Prototype Identifier:** The identifier remains **Prototype VUID** and is **not an official 3D ULPIN**.
- **No Legal Adjudication:** BhuVistaar validates spatial/topological consistency and records human administrative decisions; it does not issue legal title or certify ownership.
- **Simulated Authorization:** User roles (`SIM-OFFICER-001`, `SIM-APPROVER-001`) operate under `SIMULATED_PROTOTYPE` mode pending enterprise IAM integration in Phase 3.
