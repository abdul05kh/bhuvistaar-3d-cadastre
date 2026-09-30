# BhuVistaar — Operational User Workflows

This document specifies the operational procedures for distinct roles interacting with the BhuVistaar platform.

---

## 1. Persona Overview

| Persona | Role Identifier | Primary Responsibilities | Authorization Boundary |
|---|---|---|---|
| **Field Surveyor** | `FIELD_OPERATOR` | Uploads total station measurements, architectural floorplans, and survey metadata; verifies pre-flight quality and handles sync. | Can ingest evidence and review local sync state; cannot modify validation rules or grant approval. |
| **GIS / AI Analyst** | `REVIEWER` | Generates candidate spatial units, inspects model confidence, evaluates anomaly clusters, and inspects geometric discrepancies. | Can propose candidates and flag anomalies; cannot bypass validation or grant statutory approval. |
| **Cadastral Reviewing Officer** | `REVIEWER` | Audits evidence triads, challenges defects, requests non-destructive corrections, revalidates revisions, and signs review decisions. | Can accept, reject, or correct candidates; cannot approve final legal record without Gate C clearance. |
| **Approving Officer / Registrar** | `APPROVER` | Reviews complete provenance and validation trail; executes Gate C final statutory adjudication. | Full approval authority subject to 0 blockers, verified provenance, and human review sign-off. |
| **Auditor / System Admin** | `ADMIN` | Monitors system health, audits append-only event logs, verifies reproducibility snapshots, and manages database backups. | System management, demo scenario resets, and export generation; cannot bypass spatial integrity gates. |

---

## 2. Step-by-Step Persona Workflows

### 2.1 Field Surveyor Workflow
```
[Survey Total Station / Drone Scan]
                 ↓
[Ingest Raw Evidence File] ──> Pre-Flight Quality Gate (Checksum, CRS, Ring Closure)
                 ↓
          [Quality Status]
          ├── BLOCKED ──> Display Reason (e.g. Unclosed polygon) ──> Correct in CAD
          └── ACCEPTED ─> Upload to Authoritative PostGIS Persistence
                 ↓
[Review Local Sync Status] ──> Mark PENDING_SYNC / SYNCED
```

### 2.2 Cadastral Reviewing Officer Workflow
```
[Open Reviewer Attention Queue]
                 ↓
[Select High-Priority Candidate with Anomaly]
                 ↓
[Inspect 3D Cadastral Workspace] ──> Highlight Conflict Box (e.g., VRT-003 Overlap)
                 ↓
[Inspect Side-by-Side Evidence Triad] (Survey Record vs Arch Elevation vs 3D Prism)
                 ↓
[Examine Fact-Grounded Explainability] (Exact Overlap = -0.50m)
                 ↓
[Choose Review Action]
  ├── REJECT ──────────> Provide Rationale ──> Mark Candidate Inactive
  ├── ACCEPT ──────────> (Permitted only if 0 Blockers) ──> Sign Decision
  └── REQUEST_CORRECTION ──> Open Correction Modal
                                  ↓
                             Adjust z_max / Footprint
                                  ↓
                             Spawn Revision 2 (Keep Rev 1 intact)
                                  ↓
                             Regenerate Deterministic VUID
                                  ↓
                             Automatic Revalidation (Confirm 0 Blockers)
                                  ↓
                             Sign Review Decision (ACCEPT)
```

### 2.3 Approving Officer (Gate C) Workflow
```
[Select Candidate Revision]
                 ↓
[Evaluate Gate C Eligibility]
  ├── Precondition 1: Revision is not already approved?
  ├── Precondition 2: 0 Blockers on latest validation run?
  ├── Precondition 3: Validation run is current (created >= revision.created_at)?
  ├── Precondition 4: Provenance verified and evidence uncorrupted?
  └── Precondition 5: Human review recorded with decision == 'ACCEPT'?
                 ↓
      [Any Precondition Fails?]
      ├── YES ──> HTTP 409 Conflict: Gate C Approval Strictly Blocked
      └── NO ───> Submit Approval Justification
                       ↓
                  Save Approval Decision
                       ↓
                  Update Unit & Revision Status = APPROVED
                       ↓
                  Emit APPROVAL_GRANTED to Append-Only Audit Trail
                       ↓
                  Generate Prototype JSON v1.0.0, 2D GeoJSON & 3D OBJ Exports
```
