# Validation Engine

Rule families:
- GEO-001 non-empty
- GEO-002 valid geometry
- GEO-003 explicit CRS
- GEO-004 finite coordinates
- VRT-001 z_min < z_max
- VRT-002 ordered floor intervals
- VRT-003 no unintended vertical overlap
- VRT-004 expected adjacency/gap
- TOP-001 child footprint within parent where required
- TOP-002 no unintended 3D peer overlap
- TOP-003 duplicate geometry
- TOP-004 shared-boundary consistency
- ID-001 parent ULPIN present
- ID-002 VUID unique
- ID-003 VUID deterministic
- PROV-001 evidence exists
- PROV-002 checksum exists
- PROV-003 method/version recorded
- REV-001 BLOCKER prevents approval
- REV-002 approval records actor/time

Severity: INFO < WARN < ERROR < BLOCKER.

Every result is structured with rule_code, severity, object_id, passed, message, measured_value, threshold and suggested_action.

The seeded demo MUST contain one overlapping floor pair and the validator MUST detect it.
