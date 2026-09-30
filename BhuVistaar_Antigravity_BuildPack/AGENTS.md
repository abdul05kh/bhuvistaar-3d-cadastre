# BhuVistaar Agent Rules

Read before editing. Inspect actual files first. Plan before implementation. Make minimal changes. Test every meaningful change.

Security: validate all external inputs; parameterized DB queries; no eval/exec; no secrets; safe upload handling; authorization on mutations; no stack traces to clients.

Spatial: every geometry has explicit CRS; never mix degrees/metres; reject invalid/empty/self-intersecting geometry unless a recorded repair step exists; parent ULPIN is immutable; every 3D unit has parent, geometry, z-range, semantic type, evidence, confidence, validation status and audit metadata.

AI: predictions are candidates only; never infer legal ownership from imagery; deterministic geometry rules cannot be bypassed by ML.

UI: professional, dense, accessible, audit-first; do not use government logos or imply certification.

Done means implementation + tests + failure handling + docs + clean reproducible startup.
