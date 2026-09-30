# Security

Threats: malicious GeoJSON, oversized uploads, path traversal, malformed coordinates, SQL injection, unauthorized approval, evidence tampering, XSS, secrets.

Controls:
- strict schemas
- upload size/type limits
- sanitized filenames
- parameterized queries
- server-side authorization
- checksums
- audit events
- safe error responses
- secret/dependency scanning
- least privilege

Roles:
Viewer, Survey Analyst, Reviewer, Administrator.

Never let external evidence bypass validation/provenance boundaries.
