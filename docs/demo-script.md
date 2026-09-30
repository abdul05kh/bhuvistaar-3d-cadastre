# BhuVistaar — 3-Minute Timed Presentation Script

**Total Duration:** 3 Minutes (180 Seconds)  
**Presenter Goal:** Prove that BhuVistaar enables traceable, deterministically validated, human-governed 3D cadastral intelligence without false legal or official claims.

---

### [0:00 - 0:20] The Problem & Statutory Anchor
**Presenter Action:** Point to top header showing ULPIN and 2D ground boundary in 3D viewer.  
**Presenter Speaks:**  
> "Good morning, respected judges. In India today, all land records are tied to a flat 2D ground parcel identified by a 14-digit ULPIN. But modern cities build vertically. When multi-storey buildings or basements are built, 2D GIS collapses multiple distinct owners into a single polygon, causing boundary ambiguity. BhuVistaar solves this. Notice here: the 14-digit parent ULPIN remains our immutable statutory anchor; we never mutate it."

---

### [0:20 - 0:40] Evidence Ingestion & Cryptographic Provenance
**Presenter Action:** Click **Inspect Attached Evidence** (moves to Step 2). Open Evidence tab.  
**Presenter Speaks:**  
> "To prevent detached, fake 3D models, every 3D unit in BhuVistaar must be cryptographically anchored to raw survey evidence. Here we see an ingested Total Station survey. The system immediately hashes it with SHA-256. If someone alters this evidence file later, dependent candidates become invalid."

---

### [0:40 - 1:00] Machine Candidate Proposal (AI IS NOT THE AUTHORITY)
**Presenter Action:** Click **Generate AI Proposals** (Step 3). Point to AI Proposals tab and confidence scores.  
**Presenter Speaks:**  
> "Here our machine models propose 4 candidate floor levels with high confidence—around 91%. But here is our core architectural doctrine: **AI IS NOT THE AUTHORITY.** In statutory land administration, machine learning models hallucinate. Therefore, AI proposals are strictly non-authoritative. They must enter independent mathematical validation."

---

### [1:00 - 1:20] 3D Prismatic Extrusion & Prototype VUID
**Presenter Action:** Click **3D Cadastral Viewer** (Step 4). Point to 3D extruded prisms and VUID in inspector.  
**Presenter Speaks:**  
> "Notice how our engine extrudes 3D volumetric prisms and derives a deterministic Prototype VUID. Because CAD vertex order can vary, our algorithm normalizes polygon winding and vertex start points, ensuring identical geometry always produces the exact same VUID. Notice our legal disclaimer: this is a prototype identifier, not an official 3D ULPIN."

---

### [1:20 - 1:40] Deterministic Spatial Validation (VRT-003 Blocker)
**Presenter Action:** Click **Detect Geometric Blocker** (Step 5). Point to red conflict highlight box.  
**Presenter Speaks:**  
> "Now observe what happens. The AI model was 91% confident, but our deterministic spatial validator ran Rule VRT-003 and detected a physical collision: Level L01's ceiling at 106.50 meters collides with Level L02's floor at 106.00 meters by exactly 0.50 meters. The validator emits an immovable BLOCKER. Gate C strictly prohibits approval."

---

### [1:40 - 2:00] Fact-Grounded Explainability & Disagreement Case A
**Presenter Action:** Click **Inspect Fact Breakdown** (Step 6). Open Explain modal.  
**Presenter Speaks:**  
> "Notice the explanation: it calculates the exact gap of -0.50 meters against our -0.001 meter tolerance from recorded database coordinates—zero LLM hallucination. Our Disagreement Engine explicitly flags this as Case A: high AI confidence, but deterministic spatial failure."

---

### [2:00 - 2:20] Human Review & Non-Destructive Correction
**Presenter Action:** Click **Open Correction Modal** (Step 7). Adjust L01 ceiling to 106.00m and click Apply.  
**Presenter Speaks:**  
> "Because land disputes require complete legal history, BhuVistaar never overwrites data. When the officer corrects the ceiling from 106.50 down to 106.00 meters, the system spawns Revision 2, links predecessor lineage, and preserves the defective Revision 1 intact in PostgreSQL."

---

### [2:20 - 2:40] Revalidation & Gate C Adjudication
**Presenter Action:** Click **Submit Officer ACCEPT** (Step 9). Open Gate C Approval.  
**Presenter Speaks:**  
> "Revision 2 is automatically revalidated: 0 blockers, new deterministic VUID. The reviewing officer signs with an ACCEPT decision. With all Gate C preconditions verified—0 blockers, verified provenance, and human review—the approving officer grants prototype approval."

---

### [2:40 - 3:00] Audit Trail & Interoperable Structured Export
**Presenter Action:** Click **Inspect Interoperable Export** (Step 10). Open Export Modal.  
**Presenter Speaks:**  
> "Finally, the action is permanently recorded in our append-only audit trail. The complete governed result can now be exported in structured JSON v1.0.0, standard 2D GeoJSON, or 3D Wavefront OBJ meshes, complete with round-trip verification. In 3 minutes, we have shown: evidence in, machine assistance, mathematical validation, human governance, historical revisions, and an auditable interoperable output. Thank you."
