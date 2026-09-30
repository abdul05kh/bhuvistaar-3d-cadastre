# Deterministic Demo Fixture

Parent parcel: synthetic ULPIN-like reference `12345678901234`, 40m x 30m, explicit projected CRS.

Building: 24m x 18m, base elevation 100m.
Floors:
B1 97-100
G 100-103
L01 103-106
L02 106-109

Evidence:
EVID-001 parcel boundary
EVID-002 building footprint
EVID-003 floor plan metadata

Defect fixture: make L01 end at 106.5 while L02 starts at 106.0. Expected overlap error.

Clean fixture: adjacent intervals only.

The fixture is synthetic and must be labelled as such.
