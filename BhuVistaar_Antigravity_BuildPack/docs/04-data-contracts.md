# Data Contracts

Parcel:
```json
{"ulpin":"12345678901234","crs":"EPSG:32643","geometry":{"type":"Polygon","coordinates":[]}}
```

Floor input:
```json
{"level":"L01","z_min":103.4,"z_max":106.6}
```

Generated unit must contain:
`prototype_vuid`, `parent_ulpin`, `semantic_type`, `level_code`, `geometry`, `z_min`, `z_max`, `confidence`, `source_ids`, `validation_status`.

Evidence must contain source ID, type, checksum, reference/acquisition time, CRS where spatial, provenance reference, processing step and version.

Strict ingestion: reject unknown/malformed fields, non-finite coordinates, missing CRS and invalid polygon structure.
