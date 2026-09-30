# Implementation Roadmap

0 Foundation: repo, Docker, FastAPI, React, PostGIS, CI.
1 Spatial core: schema, CRS, parcel ingestion, deterministic IDs.
2 3D generation: extrusion, floors, basement, metrics.
3 Validation: geometry, vertical, topology, identity, provenance.
4 UI: Cesium workspace, tree, inspector, validation console, evidence, audit.
5 QA: property/integration/E2E/security/performance.
6 Demo hardening: deterministic seed, reset, one-command startup/test/export.

Parallel workstreams: backend/domain, frontend/viewer, validation/tests, fixtures/docs. Coordinate schema changes centrally.
