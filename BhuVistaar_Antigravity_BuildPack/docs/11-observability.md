# Observability

Demo SLOs:
- API availability >=99.5%
- validation success >=99%
- p95 validation latency <2s for seeded parcel
- zero silent validation failures

Logs: request_id, operation, object_id, rule/model version, duration, result, error code.
Do not log document contents.

Metrics: generation_count, validation_count, blocker_count, units_generated, evidence_missing_count, approval_count, API_latency, DB_latency.

Health: /health/live and /health/ready.

If 3D rendering fails, data and validation panels must remain usable.
