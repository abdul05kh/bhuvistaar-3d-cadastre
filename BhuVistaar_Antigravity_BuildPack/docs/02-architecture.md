# Architecture

```mermaid
flowchart TB
UI[React + CesiumJS]-->API[FastAPI]
API-->GEN[3D Generator]
API-->VAL[Validation Engine]
API-->EVID[Provenance]
API-->DB[(PostgreSQL + PostGIS)]
GEN-->DB
VAL-->DB
EVID-->DB
API-->EXP[Export]
```

Frontend visualizes; it does not make authoritative geometry decisions.
API validates requests and orchestrates.
Generator performs deterministic extrusion/floor construction.
Validator produces stable rule-coded issues.
PostGIS stores spatial objects and relationships.
Export produces machine-readable audit/provenance packages.

Failure rule: validation failure or service failure must never silently become "valid".
