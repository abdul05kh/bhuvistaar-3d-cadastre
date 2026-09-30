# BhuVistaar — Feasibility & Production Evolution Matrix

This document provides a rigorous, transparent breakdown of technical feasibility, data prerequisites, and architectural requirements across three developmental tiers: **Current Prototype**, **Pilot MVP**, and **Full Production**.

---

## 1. Feasibility Matrix

| Cadastral Capability | Current Prototype Status | Technical Feasibility | Required Data Input | Current Prototype Limitations | Pilot MVP Requirement | National Production Requirement |
|---|---|---|---|---|---|---|
| **2D Parcel Anchor Preservation** | **VERIFIED** | High | 14-digit ULPIN, 2D boundary polygon (EPSG:32643). | Single synthetic coordinate frame (Bangalore UTM 43N). | Support all UTM projected zones across India. | Automated sync with State Cadastral Portals (Bhoomi, Dharani, BhuNaksha). |
| **Deterministic 3D Unit (VUID) Derivation** | **VERIFIED** | High | Clean boundary vertices, floor elevation intervals [z_min, z_max]. | Limited to extruded prisms; non-planar curved volumes not supported. | Support multi-tier vertical strata (mezzanines, shared utility risers). | Statutory gazette formulation of 3D ULPIN standard. |
| **Gate A Topology Validation** | **VERIFIED** | High | Metric coordinate points, parcel boundaries. | CPU-bound PostGIS spatial relational queries. | Spatial R-tree indexing optimization. | GPU/Distributed spatial partitioning for district-wide queries. |
| **Fact-Grounded Explainability** | **VERIFIED** | High | Boundary coordinates, recorded elevations. | Explanations limited to implemented rules (GEO, TOP, VRT). | Rule coverage expansion to municipal setback bylaws. | Automated statutory legal notice drafting. |
| **Non-Destructive Revisioning** | **VERIFIED** | High | Corrected polygon rings or z-extents. | Single-branch linear revision history per unit. | Multi-officer branch review and merge workflows. | Immutable state archival with cryptographic timestamping. |
| **AI Candidate Proposal** | **PROTOTYPE** | Medium | Floorplan CAD / Vector PDF drawings. | Heuristic extrusion and synthetic candidate proposals. | Fine-tuned computer vision segmentation on real architectural blueprints. | Direct ingestion of BIM / IFC 4.3 models and LiDAR point clouds. |
| **Evidence Provenance & SHA-256 Checksums** | **VERIFIED** | High | Raw file uploads (GeoJSON, DXF). | Local file storage with filesystem UUID naming. | S3-compatible cloud object storage with WORM retention. | Statutory digital evidence locker integration (DigiLocker / CORD). |
| **Field Surveyor Degraded Operation** | **SIMULATED** | High | Survey measurements, local offline cache. | Session/browser memory sync; no local SQLite/IndexedDB persistence. | IndexedDB client cache with background ServiceWorker sync. | Native Android/iOS surveyor PWA with bluetooth total station bridge. |
| **Statutory Role Authorization** | **SIMULATED** | High | Simulated headers (`X-Officer-Role`). | No OAuth2/OIDC token verification or DSC digital signatures. | Keycloak/OIDC integration with role-based access control. | Aadhaar-based eSign / PKI USB token integration. |
| **Interoperable Data Export** | **VERIFIED** | High | Active spatial revision models. | BhuVistaar JSON v1.0.0, 2D GeoJSON, 3D OBJ mesh. | LandXML and CityGML v2.0 LOD2 export. | OGC 3D Tiles and IFC 4.3 BIM standardized streaming. |

---

## 2. Summary of Maturity Tiers

- **Current Prototype (Slice 6 Release Candidate):**
  A verified, reproducible engineering system demonstrating that 3D cadastral intelligence, deterministic spatial validation, non-destructive revisioning, human review, and auditable exports can execute end-to-end without hallucinated legal claims.
- **Pilot MVP (Controlled District Sandbox):**
  Requires multi-zone projected CRS transformations, Keycloak/OIDC authentication, IndexedDB offline field caching, and integration with a municipal development authority sandbox.
- **National Production:**
  Requires statutory legislative amendment of land survey acts to recognize 3D volumetric rights, PKI cryptographic digital signatures for surveyors and registrars, and direct integration with state land record backends.
