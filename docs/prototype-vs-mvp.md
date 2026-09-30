# BhuVistaar — Prototype vs MVP vs Production

To maintain strict technical honesty, this document delineates what BhuVistaar implements today versus what is required for a municipal pilot (MVP) and a full-scale statutory production deployment.

---

## 1. What Exists Today (Prototype Scope)

- **Persistence:** Real PostgreSQL 16 + PostGIS 3.4 database running in Docker, managed with Alembic migrations (`004_validation_intelligence`).
- **Spatial Engine:** EPSG:32643 metric geometry, representation-invariant deterministic VUID derivation from canonical WKB hashes, Shapely 2.0 and PostGIS relational spatial operations.
- **Validation Engine:** Deterministic Gate A (`GEO-001..004`, `TOP-001`, `VRT-001..003`) and Gate B (`PROV-001..004`) rules with mathematical blocker guards.
- **Governance:** Non-destructive revisioning (spawning Revision 2 while preserving Revision 1), reviewer queue, Gate C adjudication blocking approval on blockers, unreviewed revisions, stale validations, or missing provenance.
- **Explainability:** Fact-grounded mathematical breakdown of overlaps without LLM hallucination; Disagreement Engine tracking Cases A, B, C, and D.
- **Operational Maturity:** Containerized environment (Docker Compose), tri-level health probes (`/health/ready`), correlation ID middleware, 11 deterministic field simulation scenarios, and BhuVistaar JSON v1.0.0, 2D GeoJSON, and 3D Wavefront OBJ exports with round-trip verification.
- **Testing:** 79 unit/integration tests passing (100% green) against live PostGIS, plus Playwright browser E2E test.

---

## 2. What Is Needed for a Municipal Pilot (MVP Scope)

1. **Multi-Zone Coordinate Pipelines:**
   - Automated detection and reprojection across Indian UTM zones (e.g. Zone 42N to Zone 45N) and local municipal grid datum shifts.
2. **Production Authentication & Role-Based Access Control:**
   - Replacing `SIMULATED_PROTOTYPE` headers with OpenID Connect (OIDC) / Keycloak issuing signed JWT tokens.
3. **Persistent Offline Field Storage:**
   - Integrating client-side IndexedDB persistence and ServiceWorker background sync for field surveyors working in low-connectivity areas.
4. **Enhanced Architectural Plan Parsing:**
   - Computer vision OCR pipeline to extract text elevation callouts and room boundaries directly from multi-page PDF/DWG files.
5. **Additional Interoperability Formats:**
   - OGC CityGML v2.0 LOD2 export and LandXML 1.2 volumetric parcel serialization.

---

## 3. What Requires Statutory & Production Infrastructure (Production Scope)

1. **Legislative / Statutory Recognition:**
   - Amendments to State Land Revenue Acts and Registration Acts recognizing 3D volumetric parcels as legal cadastral entities.
2. **Statutory 3D ULPIN Issuance:**
   - Official national formulation of a 3D ULPIN numbering schema by the Department of Land Resources (DoLR).
3. **Production State Registry Direct Integration:**
   - Secure mutual-TLS API bridges with state portals (e.g. Karnataka Bhoomi, Telangana Dharani, Maharashtra e-Mahabhumi).
4. **Cryptographic PKI Signatures:**
   - Integration with licensed Certifying Authorities (CAs) for Class 3 Digital Signature Certificates (DSC) and Aadhaar eSign.
5. **Statutory Land Dispute Settlement:**
   - Formal appellate court procedures for disputed cadastral boundaries and title adjudication.
