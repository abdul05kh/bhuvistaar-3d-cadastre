# Product Requirements

Primary user: survey/land-record/urban GIS officer.

User jobs:
- understand vertical units within a parcel
- trace each unit to parent parcel and evidence
- detect inconsistencies before acceptance
- review machine-generated candidates
- export reproducible records

Success:
- 100% generated units retain parent ULPIN
- 100% retain provenance
- all invalid fixture geometries detected by their intended rules
- repeated deterministic generation yields identical VUIDs
- reviewer can understand a failed rule quickly

Trust questions every result must answer:
What is it? Where is it? What is it linked to? Which evidence produced it? How confident is it? Which rules passed? Who approved it and when?
