# BhuVistaar — Known Limitations & Unsupported Capabilities

In accordance with strict technical integrity, this document catalog’s all deliberate limitations, out-of-scope capabilities, and unsupported formats in the BhuVistaar prototype.

---

## 1. What BhuVistaar Is NOT

- **NOT an Official Statutory Cadastral System:** BhuVistaar is an engineering research prototype developed for SIH26011. It does not replace statutory revenue authorities.
- **NOT an Official 3D ULPIN Authority:** Prototype VUIDs are internal data-layer keys. No statutory 3D ULPIN standard exists or has been issued by BhuVistaar.
- **NOT a Legal Title Adjudication System:** The platform deterministically validates spatial and geometric consistency; it does not determine land ownership, resolve legal disputes, or certify legal boundaries.
- **NOT a Production Government Integration:** BhuVistaar does not connect to live government databases (Bhoomi, Dharani, BhuNaksha, DigiLocker, or Aadhaar).

---

## 2. Geometric & Spatial Limitations

1. **Extruded Prismatic Geometries Only:**
   - The platform models 3D units as polygonal 2D footprints extruded between horizontal vertical bounds $[z_{\text{min}}, z_{\text{max}}]$.
   - Arbitrary 3D polyhedral meshes with non-horizontal ceilings/floors (e.g., sloping roofs, spherical domes, spiral ramps, helical subterranean structures) are not currently validated by the extrusion engine.
2. **Single Calibrated Projected Coordinate System:**
   - The primary synthetic fixture is calibrated for Bangalore in `EPSG:32643` (WGS 84 / UTM Zone 43N).
   - While PyProj transformations are supported, state-specific local datum grid shifts (e.g. Everest 1830 polyconic transformations) require customized transformation tables not bundled in this prototype.
3. **No Automatic Geometric Healing / Auto-Clipping:**
   - By deliberate policy, BhuVistaar **refuses** to silently clip or adjust candidate geometries that breach boundaries. Defective units are rejected with a BLOCKER, requiring explicit human officer correction.

---

## 3. Operational & Security Limitations

1. **Simulated Role Authentication:**
   - Authorization headers (`X-Officer-Role`) simulate administrative boundaries (`VIEWER`, `REVIEWER`, `APPROVER`, `ADMIN`, `FIELD_OPERATOR`).
   - Production PKI authentication (OIDC, Keycloak, Class 3 DSC tokens) is not implemented in this prototype.
2. **In-Memory Observability Metrics:**
   - Operational counters (requests, validation executions, export generation) reside in memory and reset upon container restart. Production workloads require Prometheus/OpenTelemetry scrapers.
3. **Client-Side Field Sync Storage:**
   - The field operator view simulates degraded/offline mode using browser session memory rather than persistent IndexedDB disk storage.
4. **Synthetic AI Evaluation:**
   - Model benchmark metrics reflect performance against 10 controlled synthetic scenarios and do not represent measured real-world machine learning accuracy.
