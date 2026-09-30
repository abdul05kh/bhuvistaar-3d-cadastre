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
10. **Delivers AI-Assisted Cadastral Intelligence (Slice 3)**: Controlled candidate spatial-unit generation, topology anomaly scanning, reviewer queue prioritization, and end-to-end data lineage (*Trace Origin*).

---

## 🤖 Slice 3 — AI Cadastral Intelligence Architecture

> [!IMPORTANT]
> **AI IS NOT THE AUTHORITY.**
> ```
> EVIDENCE → AI PROPOSAL → DETERMINISTIC ENGINE → GATE A/B VALIDATION → HUMAN REVIEW → GATE C APPROVAL
> ```
> AI output is strictly a proposal (`AI_CANDIDATE`). It never bypasses deterministic spatial validation or mandatory human officer adjudication.

### The Four Intelligence Layers
- **Layer A (Evidence Understanding)**: `evidence-extractor-001` normalizes architectural blueprints and drone survey evidence into structured `EvidenceObservation` items with SHA-256 checksum tracking.
- **Layer B (Candidate Generation)**: `prismatic-candidate-001` proposes 3D spatial unit candidates with transparent reason codes and policy confidence bands (HIGH/MED/LOW).
- **Layer C (Anomaly Detection)**: `cadastral-anomaly-001` independently scans vertical strata for collisions (`OVERLAPPING_LEVELS`), unexplained gaps, and multi-source evidence discrepancies.
- **Layer D (Reviewer Intelligence)**: Prioritizes the Reviewer Attention Queue by urgency and generates fact-based cadastral explanations grounded in measured geometric facts.

Detailed model disclosures and limitations:
- [Model Card: Prismatic Candidate Generator](file:///d:/projects/BhuVistaar/docs/model-card-prismatic-candidate-001.md)
- [Model Card: Cadastral Anomaly Detector](file:///d:/projects/BhuVistaar/docs/model-card-cadastral-anomaly-001.md)
- [Full Slice 3 Specification](file:///d:/projects/BhuVistaar/docs/phase-3-ai-intelligence.md)

---

## 🛠️ Technology Stack
- **Geospatial & Computational Geometry:** Shapely 2.0, PyProj 3.8, GeoAlchemy2, NumPy
- **Authoritative Spatial Database:** PostgreSQL 16 + PostGIS 3.4 (`EPSG:32643` canonical metric storage)
- **Database Migrations:** Alembic (Migrations `001`, `002`, `003` for spatial schema, governance, and AI intelligence)
- **Backend API:** FastAPI, Pydantic v2, SQLAlchemy 2.0, Uvicorn
- **AI & Evaluation Engine:** Rule-assisted statistical heuristics, empirical benchmark harness (`SYNTHETIC_CADASTRE_V1`)
- **Frontend Workspace:** React, TypeScript, Three.js (WebGL 3D Viewer with translucent AI candidate meshes), Lucide Icons, Vite
- **Quality Assurance & Verification:** Pytest, Hypothesis, TestClient (49 passing tests)

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

Run the full automated test suite (49 tests covering Slice 1A, Slice 1B, Slice 2 E2E, and Slice 3 AI pipeline):
```bash
py -3.12 -m pytest tests/ -v
```

Execute the dedicated Slice 3 AI Pipeline integration test:
```bash
py -3.12 -m pytest tests/integration/test_ai_pipeline_integration.py -v
```

Run empirical model evaluation against synthetic benchmark fixtures (Scenarios A through G):
```bash
py -3.12 -m pytest tests/unit/test_ai_evaluator.py -v
```

---

## 🎯 Flagship Judge Demonstration Scenarios

In the web interface (`http://localhost:5173`), choose a scenario from the top bar:
1. **Flagship Golden Path (AI Proposal + VRT-003 Overlap Blocker)**:
   - Click "1. Flagship" in the Demo Bar or "Regenerate Proposals".
   - AI generates 4 candidate levels with explicit confidence scores and reason codes.
   - Deterministic validator detects `VRT-003 BLOCKER` (0.50m collision between L01 and L02).
   - Reviewer attempts Gate C approval $\to$ strictly blocked.
   - Reviewer clicks "Request Correction" $\to$ adjusts ceiling from `106.50m` to `106.00m`.
   - Backend creates Revision 2 with regenerated deterministic VUID. Historical Revision 1 is fully preserved.
   - Automatic revalidation drops blockers to 0.
   - Officer records "ACCEPT" review $\to$ Gate C approves $\to$ inspect audit trail and structured export.
2. **Evidence Conflict Scenario**: Click "2. Conflict" to see conflicting drawing vs survey metadata flagged as an anomaly.
3. **Low Confidence Proposal**: Click "3. Low Conf" to view an ambiguous sketch candidate flagged for mandatory on-site survey.
4. **Trace Origin Lineage**: Click "Trace Origin" in the top bar to inspect the complete 8-stage cryptographic audit path.

---

## 👥 Contributors & Team Attribution
Refer to [CONTRIBUTORS.md](file:///d:/projects/BhuVistaar/CONTRIBUTORS.md) for core team members, role breakdowns, and multi-author commit attribution protocol.
