# Testing Strategy

Risk order:
1 geometry correctness
2 ULPIN linkage
3 validation false negatives
4 provenance
5 API/schema integrity
6 approval/audit integrity
7 UI/backend consistency

Pyramid:
- many unit/property tests
- fewer integration/contract tests
- very few E2E tests

Targets:
- geometry utilities >=90% branch-oriented
- ID generation >=95%
- validation rules >=95%
- schema/domain >=90%

Top tests:
1 invalid polygon rejected
2 missing CRS rejected
3 z_min >= z_max rejected
4 floor overlap detected
5 valid adjacent floors pass
6 outside-parent footprint detected
7 ULPIN preserved
8 VUID deterministic
9 checksum required
10 BLOCKER prevents approval

CI under 10 minutes: lint/type, unit/property, integration, frontend, one E2E smoke, build.
