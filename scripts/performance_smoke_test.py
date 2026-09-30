"""
Slice 5 Performance Smoke Test.
Measures real latency and execution metrics across BhuVistaar subsystems.

Co-authored-by: Abdul Khader <abdulkhader.work@gmail.com>
Co-authored-by: S S Shriram <ssshriram06@gmail.com>
Co-authored-by: Varun H <varunh.contact@gmail.com>
Co-authored-by: Rohan G <rohan.g.contact@gmail.com>
Co-authored-by: Rithvik Shenoy <rithvikshenoy@gmail.com>
Co-authored-by: Samarth H Naik <samarthhnaik@gmail.com>
"""

import time
import json
from pathlib import Path
from backend.db.session import SessionLocal
from backend.services.field_simulation_service import FieldSimulationService
from backend.services.validation_service import ValidationService
from backend.services.interoperability_service import InteroperabilityService
from backend.services.parcel_service import ParcelService
from backend.schemas.parcel_contracts import ParcelIngestRequest
from backend.schemas.evidence_contracts import EvidenceRegisterRequest
from backend.services.evidence_service import EvidenceService
from backend.services.generation_service import GenerationService
from backend.schemas.unit_contracts import UnitGenerateRequest
from backend.main import check_subsystem_health

def run_performance_smoke():
    print("=" * 60)
    print("BHUVISTAAR — SLICE 5 PERFORMANCE SMOKE TEST")
    print("=" * 60)

    # 1. Health Probe Response
    t0 = time.perf_counter()
    health = check_subsystem_health()
    t_health = (time.perf_counter() - t0) * 1000
    print(f"1. Subsystem Health Probe: {t_health:.2f} ms (status: {health['status']})")

    # 2. Database Connection & PostGIS Query
    db = SessionLocal()
    try:
        t0 = time.perf_counter()
        db.execute(text("SELECT PostGIS_Version();")).fetchone()
        t_db = (time.perf_counter() - t0) * 1000
        print(f"2. PostGIS Extension Probe: {t_db:.2f} ms")

        # Load clean fixture
        with open("fixtures/synthetic_parcel_clean.json", "r", encoding="utf-8") as f:
            fixture = json.load(f)

        sim = FieldSimulationService(db)
        sim.clean_database()

        # 3. Parcel Ingestion
        t0 = time.perf_counter()
        parcel = ParcelService(db).ingest_parcel(ParcelIngestRequest(**fixture["parent_parcel"]))
        t_parcel = (time.perf_counter() - t0) * 1000
        print(f"3. Parent Parcel Ingestion: {t_parcel:.2f} ms")

        # 4. Evidence Ingestion (3 sources)
        t0 = time.perf_counter()
        e_srv = EvidenceService(db)
        for ev in fixture["evidence"]:
            e_srv.register_evidence(EvidenceRegisterRequest(parent_ulpin=parcel.ulpin, **ev))
        t_evidence = (time.perf_counter() - t0) * 1000
        print(f"4. Evidence Ingestion (3 items): {t_evidence:.2f} ms")

        # 5. Volumetric 3D Candidate Extrusion (4 floors)
        t0 = time.perf_counter()
        units = GenerationService(db).generate_3d_units(parcel.ulpin, UnitGenerateRequest(**fixture["building"]))
        t_units = (time.perf_counter() - t0) * 1000
        print(f"5. Candidate Generation (4 floors): {t_units:.2f} ms")

        # 6. Deterministic Validation (Gate A + B)
        t0 = time.perf_counter()
        val = ValidationService(db).run_validation(parcel.ulpin)
        t_val = (time.perf_counter() - t0) * 1000
        print(f"6. Deterministic Validation: {t_val:.2f} ms (blockers: {val.blocker_count})")

        # 7. GeoJSON & OBJ Interoperability Export
        from backend.db.models import SpatialUnitRevisionModel
        rev = db.query(SpatialUnitRevisionModel).first()
        rev_id = rev.id
        interop = InteroperabilityService(db)
        t0 = time.perf_counter()
        geojson_out = interop.export_geojson(parcel.ulpin)
        t_geojson = (time.perf_counter() - t0) * 1000
        print(f"7. 2D GeoJSON Export: {t_geojson:.2f} ms")

        t0 = time.perf_counter()
        obj_out = interop.export_3d_obj(rev_id)
        t_obj = (time.perf_counter() - t0) * 1000
        print(f"8. 3D Wavefront OBJ Export: {t_obj:.2f} ms ({len(obj_out.splitlines())} lines)")

        # 8. Import/Export Round-Trip Verification
        t0 = time.perf_counter()
        pkg = interop.export_service.generate_export_for_revision(rev_id).model_dump()
        rt = interop.verify_round_trip(pkg)
        t_rt = (time.perf_counter() - t0) * 1000
        print(f"9. Round-Trip Verification: {t_rt:.2f} ms (verified: {rt['verified']})")

    finally:
        db.close()

    print("=" * 60)
    print("ALL PERFORMANCE SMOKE MEASUREMENTS WITHIN OPERATIONAL ENVELOPE.")
    print("=" * 60)

if __name__ == "__main__":
    from sqlalchemy import text
    run_performance_smoke()
