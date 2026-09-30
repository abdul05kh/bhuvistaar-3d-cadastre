# Domain Model

Entities:
- ParentParcel: id, ULPIN, 2D geometry, CRS, source IDs, status
- SpatialUnit3D: VUID, parent ULPIN, semantic type, level, 3D geometry, z_min/z_max, area, volume, centroid, confidence, method, source IDs, validation/approval status
- EvidenceSource: id, type, reference, time, provider, checksum, CRS, resolution, metadata
- ValidationIssue: rule code, severity, object, message, measured value, threshold, action
- AuditEvent: actor, action, object, before/after hash, timestamp, reason

Prototype ID:
`BV-{parentULPIN}-{unitClass}-{level}-{shortHash}`

Example: `BV-12345678901234-BLDG-L02-7F3A9C`

This is not an official 3D ULPIN.

Semantic types: BUILDING_MASS, FLOOR_VOLUME, BASEMENT_VOLUME, UTILITY_CORRIDOR, AIRSPACE_VOLUME, OTHER_CANDIDATE.

Levels: B2/B1, G, L01/L02...
