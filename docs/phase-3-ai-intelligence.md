# BhuVistaar — Slice 3: AI-Assisted 3D Cadastral Intelligence

## 0. Executive Directive & Architectural Principle

> [!IMPORTANT]
> **AI IS NOT THE AUTHORITY.**
> 
> ```
> EVIDENCE
>    ↓
> AI / ML MODEL (Candidate Proposals)
>    ↓
> DETERMINISTIC GEOMETRY ENGINE (PostGIS EPSG:32643)
>    ↓
> DETERMINISTIC VALIDATION (Gate A / B)
>    ↓
> HUMAN REVIEW (Officer Inspection & Adjudication)
>    ↓
> GOVERNANCE / APPROVAL (Gate C)
> ```
> 
> **Never**: `Evidence -> AI -> Approved Property`.
> AI output is **ALWAYS** an unapproved candidate (`AI_CANDIDATE`). The deterministic spatial engine and governance rules remain authoritative. Human review remains mandatory.

---

## 1. Intelligence Layers Overview

Slice 3 structures cadastral machine intelligence into four distinct, loosely coupled layers:

| Layer | Component | Core Model | Function |
|---|---|---|---|
| **Layer A** | Evidence Understanding | `evidence-extractor-001` (v0.1.0) | Normalizes raw architectural drawings, drone orthoimagery, and survey metadata into structured `EvidenceObservation` items with SHA-256 checksum tracking. |
| **Layer B** | Candidate Generation | `prismatic-candidate-001` (v0.1.0) | Proposes 3D candidate spatial units (`CandidateSpatialUnit`) with explicit confidence scores, confidence policy bands (HIGH/MED/LOW), and transparent reason codes. Status is strictly `AI_CANDIDATE`. |
| **Layer C** | Anomaly Detection | `cadastral-anomaly-001` (v0.1.0) | Scans vertical strata for collisions (`OVERLAPPING_LEVELS`), unexplained gaps (`VERTICAL_GAP`), missing floor sequences, parcel boundary breaches, and evidence discrepancies. Geometry is never silently mutated. |
| **Layer D** | Reviewer Intelligence | `fact-based-explainer-001` (v0.1.0) | Prioritizes the Reviewer Attention Queue by urgency (Blockers > Anomalies > Low Confidence) and synthesizes plain-language explanations grounded strictly in geometric measurements and validation facts. |

---

## 2. Model Cards & Disclosures

Detailed specifications, architectural disclosures, training data sources, and operational limitations for each model:

- [`docs/model-card-prismatic-candidate-001.md`](file:///d:/projects/BhuVistaar/docs/model-card-prismatic-candidate-001.md)
- [`docs/model-card-cadastral-anomaly-001.md`](file:///d:/projects/BhuVistaar/docs/model-card-cadastral-anomaly-001.md)

### Synthetic Data Disclosure
All models in Slice 3 are calibrated on synthetic benchmark fixtures (`SYNTHETIC_CADASTRE_V1`, Scenarios A through G). No unauthorized government survey records or unverified production datasets are claimed or used.

---

## 3. Human-in-the-Loop & Governance Integration

### Candidate Acceptance Workflow
1. When a reviewing officer clicks **Accept as Candidate**, the proposal is promoted into the authoritative spatial database:
   - Extruded 3D geometry is normalized to canonical SRID EPSG:32643.
   - Deterministic Prototype VUID is generated (`BV-{ULPIN}-{CLASS}-{LEVEL}-{HASH}`).
   - Revision 1 is created with full provenance records linking source evidence IDs.
   - Gate A & B deterministic validation is executed.
   - Append-only audit events (`AI_REVIEWED`, `CANDIDATE_CREATED`, `VALIDATION_EXECUTED`) are logged.

### Candidate Rejection Workflow
1. When an officer clicks **Reject Proposal**:
   - Status updates to `REJECTED`.
   - Mandatory officer justification is recorded.
   - Candidate record is **permanently preserved** in the database (never deleted).
   - Audit event `AI_CANDIDATE_REJECTED` is recorded with officer attribution.

---

## 4. End-to-End Data Lineage ("Trace Origin")

The signature BhuVistaar audit graph enables tracing any cadastral candidate from its physical or drawing evidence origin all the way to legal deed export:

```
[1] SOURCE EVIDENCE (SHA-256 Checksum, Surveyor Division)
        ↓
[2] AI OBSERVATION (Floor boundary extraction, confidence)
        ↓
[3] AI CANDIDATE (Proposal ID, reason codes, confidence band)
        ↓
[4] DETERMINISTIC VALIDATION (Gate A: VRT-003 overlap blocker)
        ↓
[5] HUMAN REVIEW (Correction: Level 1 ceiling 106.50m -> 106.00m)
        ↓
[6] GOVERNED REVISION (Revision 2, deterministic VUID regenerated)
        ↓
[7] GATE C APPROVAL (Workflow Adjudication, Approver attribution)
        ↓
[8] STRUCTURED EXPORT (GeoJSON / LandInfra JSON bundle)
```

---

## 5. Architectural Independence & Fallback

- **Feature Flag**: `AI_ASSISTANCE_ENABLED=true` in `backend/config.py`.
- **Fault Tolerance**: If the AI inference service is disabled or encounters a failure, the core system continues operating with 100% functionality (deterministic parcel ingestion, spatial extrusion, Gate A/B validation, human review, Gate C approval, audit trail, and export remain fully accessible).

---

## 6. Flagship Demonstration Scenarios

Available via one-click selector in the **Demo Scenario Bar**:

1. **Flagship Golden Path (AI + VRT-003 Overlap Blocker)**:
   - AI synthesizes 4 floor proposals (B1, Ground, L01, L02).
   - Deliberate 0.50m collision between L01 (ceiling 106.50m) and L02 (floor 106.00m).
   - Deterministic validator detects `VRT-003 BLOCKER`.
   - Gate C strictly prohibits premature approval.
   - Reviewer applies non-destructive elevation correction (106.50m -> 106.00m), spawning Revision 2.
   - Revalidation yields 0 blockers; Gate C approves.
2. **Evidence Conflict**:
   - Architectural drawing specifies Level 2 at 106.00m while survey metadata specifies 107.00m.
   - Emits `EVIDENCE_CONFLICT` anomaly; prompts officer inspection.
3. **Low Confidence Proposal**:
   - Partial hand-drawn rooftop terrace sketch with 0.45 confidence.
   - Flagged with `LOW CONFIDENCE — HUMAN REVIEW REQUIRED`.
4. **Vertical Gap**:
   - Unexplained 1.50m inter-floor gap between Ground and L01.
   - Emits `VERTICAL_GAP` warning to investigate plenum or mezzanine.
