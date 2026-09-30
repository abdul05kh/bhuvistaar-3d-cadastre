# API Contract

POST /api/v1/parcels
POST /api/v1/parcels/{ulpin}/generate
GET /api/v1/parcels/{ulpin}
GET /api/v1/units/{vuid}
POST /api/v1/validation/run
GET /api/v1/validation/issues
POST /api/v1/units/{vuid}/approve
POST /api/v1/units/{vuid}/reject
GET /api/v1/export/{ulpin}

All mutation endpoints validate authorization and create audit events.
Error envelope:
```json
{"error":{"code":"INVALID_GEOMETRY","message":"Input polygon is self-intersecting.","request_id":"..."}}
```
Never expose stack traces.
