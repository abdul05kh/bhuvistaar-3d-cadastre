# BhuVistaar — Final Canonical Master Architecture

## 1. Executive Doctrine
BhuVistaar enforces a strict unidirectional trust chain:
```
PARCEL + PARENT ULPIN
          ↓
  EVIDENCE INGESTION (SHA-256 Checksum)
          ↓
   EVIDENCE QUALITY GATE (ACCEPTED / WARNING / BLOCKED)
          ↓
  EVIDENCE OBSERVATIONS
          ↓
  AI / ANALYTICS CANDIDATE PROPOSAL (Non-Authoritative)
          ↓
   DETERMINISTIC 3D GEOMETRY GENERATION
          ↓
    GATE A (Spatial) & GATE B (Provenance) VALIDATION
          ↓
     FACT-GROUNDED EXPLAINABILITY & DISAGREEMENT
          ↓
      HUMAN OFFICER REVIEW (ACCEPT / REVISE / REJECT)
          ↓
       NON-DESTRUCTIVE REVISIONING (Revision 2 + Predecessor Linkage)
          ↓
        REVALIDATION & VUID REGENERATION
          ↓
         GATE C STATUTORY ADJUDICATION
          ↓
       APPEND-ONLY AUDIT & REPRODUCIBILITY SNAPSHOT
          ↓
    INTEROPERABILITY EXPORT (JSON v1.0.0, 2D GeoJSON, 3D OBJ)
```

**Core Principle:** Machine intelligence proposes candidates; mathematical rules validate geometry; human officers govern approvals; append-only logs guarantee auditability.

---

## 2. End-to-End System Architecture (Mermaid)

```mermaid
graph TD
    subgraph Data Layer ["Authoritative Persistence (PostgreSQL 16 + PostGIS 3.4)"]
        PP[parent_parcels]
        SU[spatial_units]
        SUR[spatial_unit_revisions]
        ER[evidence_records]
        VR[validation_runs]
        RR[review_records]
        AD[approval_decisions]
        AE[audit_events]
        AIC[ai_candidates]
        DR[disagreement_records]
    end

    subgraph Input Layer ["Field & Evidence Ingestion"]
        TS[Total Station GeoJSON]
        AP[Architectural Plan DXF/PDF]
        LX[LandXML Survey]
        EQG[Evidence Quality Gate<br/>SHA-256 & CRS Check]
        TS --> EQG
        AP --> EQG
        LX --> EQG
    end

    subgraph Machine Layer ["AI & Heuristic Intelligence Layer"]
        PE[Prismatic Extrusion Model]
        FP[Floorplan ML Segmenter]
        AN[Anomaly Detection Engine]
        DE[Disagreement Engine Cases A-D]
        EQG --> PE
        EQG --> FP
        PE --> AN
        FP --> AN
    end

    subgraph Deterministic Core ["Authoritative Spatial Validation Engine"]
        GEN[Representation-Invariant VUID Generator]
        GATE_A[Gate A: GEO, VRT, TOP Rules]
        GATE_B[Gate B: PROV Evidence Integrity]
        EXP[Fact-Grounded Explainability]
        PE -. Proposal .-> GEN
        GEN --> GATE_A
        EQG --> GATE_B
        GATE_A --> EXP
        GATE_B --> EXP
        EXP --> DE
    end

    subgraph Governance Layer ["Human Review & State Machine"]
        REV_W[Review Workspace]
        CORR[Non-Destructive Correction]
        GATE_C[Gate C Adjudication Engine]
        EXP --> REV_W
        REV_W -- Request Correction --> CORR
        CORR -- New Revision --> GEN
        REV_W -- Officer ACCEPT --> GATE_C
    end

    subgraph Output Layer ["Interoperability & Auditing"]
        AUD[Append-Only Audit Timeline]
        REP[Cryptographic Reproducibility Service]
        EXP_JSON[Prototype JSON v1.0.0]
        EXP_GEO[2D GeoJSON RFC 7946]
        EXP_3D[3D Wavefront OBJ Mesh]
        GATE_C --> AUD
        GATE_C --> REP
        GATE_C --> EXP_JSON
        GATE_C --> EXP_GEO
        GATE_C --> EXP_3D
    end

    Data Layer <==> Deterministic Core
    Data Layer <==> Governance Layer
```

---

## 3. Subsystem Breakdown

### 3.1 Persistence Layer (`PostgreSQL 16 + PostGIS 3.4`)
- **Internal Storage CRS:** `EPSG:32643` (UTM Zone 43N metric coordinate reference system for Bangalore synthetic domain).
- **Geometric Integrity:** Enforces `ST_IsValid(footprint_geom) = TRUE` and strictly 2D/3D topological contracts.
- **Migration Head:** Managed via Alembic (`004_validation_intelligence`).

### 3.2 Machine Intelligence Boundary (AI Layer)
- Model outputs are classified as `AI_CANDIDATE` (never authoritative cadastre).
- AI confidence is bounded [0.0, 1.0].
- High confidence with geometric failure triggers **Disagreement Case A** (`AI_VALIDATION_DISAGREEMENT`), automatically generating a Gate A BLOCKER issue.

### 3.3 Deterministic Spatial Validation (Gate A & B)
- **TOP-001 (Parent Containment):** Uses `ST_Contains` and Shapely `contains_properly`. Encroachments produce a BLOCKER without auto-clipping.
- **VRT-003 (Vertical Stratification Overlap):** Validates that for vertically stacked units $U_1$ and $U_2$, $z_{\text{max}}(U_1) \le z_{\text{min}}(U_2) + \epsilon$ ($\epsilon = -0.001\text{m}$).
- **PROV-001..004 (Provenance Integrity):** Verifies that underlying evidence records exist, have valid checksums, and are uncorrupted.

### 3.4 Human Governance & Revisioning
- Corrections are non-destructive: correcting Level L01 ceiling spawns Revision 2, preserving Revision 1 intact.
- Revision predecessor pointers (`predecessor_revision_id`) form an immutable directed acyclic graph (DAG).
- Gate C strictly forbids approval if blockers exist, if validation is stale (`VALIDATION_OUTDATED`), or if human review has not been completed.

---

## 4. Legal & Prototype Boundaries
1. **Prototype VUID:** Derived from SHA-256 of canonical WKB geometry and vertical interval; **NOT** an official 3D ULPIN.
2. **Parent ULPIN:** Preserved as immutable 14-digit root; BhuVistaar never mutates official 2D parcel identifiers.
3. **No Statutory Adjudication:** System verifies physical/geometric validity; does not determine title or ownership.
