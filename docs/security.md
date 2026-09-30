# BhuVistaar — Prototype Security & Governance Baseline

**Document Version**: 1.0.0  
**Classification**: Prototype Security Specification  
**Context**: Smart India Hackathon Prototype (SIH26011)

---

## 1. Threat Model & Operational Boundaries

BhuVistaar is designed as an evidence-backed 3D cadastral intelligence workspace. Its primary security objective is **provenance preservation and decision accountability**: ensuring that no candidate spatial unit can be silently created, altered, or approved without an auditable chain of evidence and human governance.

### Threat Assumptions
- **Malicious or Corrupted Uploads**: Surveyors or external actors may upload malformed geometries, invalid coordinates, or corrupted files.
- **Unauthorized Candidate Approval**: Attackers or unauthorized actors may attempt to bypass spatial validation to approve overlapping property boundaries.
- **Evidence Tampering**: Surveyors or applicants may attempt to alter architectural blueprints after validation.
- **State Confusion**: Network interrupts may leave database transactions in partial states.

---

## 2. Defensive Controls Implemented

### 1. Zero Secrets in Version Control
- All credentials (e.g. database connection strings, API tokens) are strictly loaded via environment variables (`.env`).
- Repository contains a sanitized [`.env.example`](file:///.env.example) template.

### 2. Evidence Quality Gate & Input Validation
- **Checksum Verification**: Every evidence item must supply a valid cryptographic SHA-256 hash. Re-uploads of identical payloads are rejected as `DUPLICATE_EVIDENCE`.
- **Payload Limits**: Upload endpoints enforce a strict size cap (`MAX_UPLOAD_SIZE_BYTES = 10MB`).
- **Identifier Schema**: Identifiers are sanitized with alphanumeric and hyphen restrictions (`^[A-Za-z0-9-]+$`) to prevent injection and path traversal attacks.

### 3. Stale Data & Validation Tamper Protection
- If an evidence record's underlying payload is modified, candidates derived from it are marked `STALE_EVIDENCE` and barred from approval.
- If a spatial unit's geometry is corrected, previous validation results are flagged `VALIDATION_OUTDATED`. Gate C approval is strictly forbidden until re-validation passes with 0 blockers.

### 4. Append-Only Audit Logging
- All state transitions, corrections, rejections, approvals, and scenario executions write to an append-only audit datastore (`audit_events`).
- Audit rows contain cryptographic event hashes, timestamps, actor IDs, previous states, and target revision IDs.

---

## 3. Simulated Authorization Model (`SIMULATED_PROTOTYPE`)

BhuVistaar simulates multi-role institutional governance without implementing fake security theater:

| Role | Operational Scope | Restrictions |
|:---|:---|:---|
| **`VIEWER`** | Read-only inspection of parcels, 3D units, and validation reports. | Cannot submit reviews, corrections, or approvals. |
| **`REVIEWER`** | Inspects evidence, challenges AI proposals, requests geometric corrections. | Cannot issue final statutory cadastral approval (Gate C). |
| **`APPROVER`** | Performs Gate C compliance determination and grants approval. | Requires 0 blockers and prior reviewer `ACCEPT` decision. |
| **`ADMIN`** | Diagnostic management, database bootstrapping, and demo scenario resets. | Operations are logged to system audit. |

> [!WARNING]
> This authorization framework is labeled **`SIMULATED_PROTOTYPE`**. It establishes workflow boundaries for hackathon evaluation and does not substitute for state-grade Public Key Infrastructure (PKI), OAuth2/OIDC single sign-on, or hardware security tokens.
