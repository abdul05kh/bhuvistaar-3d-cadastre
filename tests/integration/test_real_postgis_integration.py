import json
import pytest
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from backend.config import settings
from backend.services.parcel_service import ParcelService
from backend.services.evidence_service import EvidenceService
from backend.services.generation_service import GenerationService
from backend.services.validation_service import ValidationService
from backend.schemas.parcel_contracts import ParcelIngestRequest
from backend.schemas.evidence_contracts import EvidenceRegisterRequest
from backend.schemas.unit_contracts import UnitGenerateRequest
from backend.db.session import Base
from backend.db.models import ParentParcelModel, SpatialUnitModel, EvidenceSourceModel
from backend.exceptions import VUIDCollisionError


POSTGIS_TEST_URL = "postgresql+psycopg://postgres:postgrespassword@127.0.0.1:5432/bhuvistaar_cadastre"


def is_postgis_online():
    try:
        engine = create_engine(POSTGIS_TEST_URL, pool_pre_ping=True)
        with engine.connect() as conn:
            res = conn.execute(text("SELECT 1;")).scalar()
            return res == 1
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not is_postgis_online(),
    reason="Real PostgreSQL/PostGIS database is not accessible on localhost:5432"
)


@pytest.fixture(scope="module")
def real_db_session():
    engine = create_engine(POSTGIS_TEST_URL)
    # Enable PostGIS extension
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        conn.commit()

    # Create tables from SQLAlchemy Base metadata
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_audit1_postgis_extension_and_srid(real_db_session):
    # 1. Verify PostGIS version
    version_str = real_db_session.execute(text("SELECT PostGIS_Version();")).scalar()
    assert version_str is not None
    assert "3." in version_str

    # 2. Verify parent_parcels geometry SRID
    parcel_srid = real_db_session.execute(
        text("SELECT Find_SRID('public', 'parent_parcels', 'geometry');")
    ).scalar()
    assert parcel_srid == 32643

    # 3. Verify spatial_units footprint_geom SRID
    unit_srid = real_db_session.execute(
        text("SELECT Find_SRID('public', 'spatial_units', 'footprint_geom');")
    ).scalar()
    assert unit_srid == 32643


def test_audit1_real_postgis_clean_and_defect_pipeline(real_db_session):
    p_service = ParcelService(real_db_session)
    e_service = EvidenceService(real_db_session)
    g_service = GenerationService(real_db_session)
    v_service = ValidationService(real_db_session)

    with open("fixtures/synthetic_parcel_clean.json", "r", encoding="utf-8") as f:
        clean_data = json.load(f)

    # Clean prior data
    real_db_session.query(SpatialUnitModel).delete()
    real_db_session.query(EvidenceSourceModel).delete()
    real_db_session.query(ParentParcelModel).delete()
    real_db_session.commit()

    # Ingest clean parcel
    parcel = p_service.ingest_parcel(ParcelIngestRequest(**clean_data["parent_parcel"]))
    assert parcel.storage_srid == 32643

    # Verify geometry was saved in PostGIS with SRID 32643
    raw_srid = real_db_session.execute(
        text("SELECT ST_SRID(geometry) FROM parent_parcels WHERE ulpin = :ulpin;"),
        {"ulpin": parcel.ulpin}
    ).scalar()
    assert raw_srid == 32643

    # Register evidence
    for ev in clean_data["evidence"]:
        e_service.register_evidence(EvidenceRegisterRequest(parent_ulpin=parcel.ulpin, **ev))

    # Generate units
    units = g_service.generate_3d_units(parcel.ulpin, UnitGenerateRequest(**clean_data["building"]))
    assert len(units) == 4

    # Verify unit footprints stored with SRID 32643
    for u in units:
        u_srid = real_db_session.execute(
            text("SELECT ST_SRID(footprint_geom) FROM spatial_units WHERE prototype_vuid = :vuid;"),
            {"vuid": u.prototype_vuid}
        ).scalar()
        assert u_srid == 32643

    # Run validation on clean fixture
    summary_clean = v_service.run_validation(parcel.ulpin)
    assert summary_clean.blocker_count == 0
    assert summary_clean.can_approve is True

    # Now test defect fixture collision
    with open("fixtures/synthetic_parcel_defect.json", "r", encoding="utf-8") as f:
        defect_data = json.load(f)

    # Ingest defect units
    # Clear units to test defect
    real_db_session.query(SpatialUnitModel).delete()
    real_db_session.commit()

    defect_units = g_service.generate_3d_units(parcel.ulpin, UnitGenerateRequest(**defect_data["building"]))
    summary_defect = v_service.run_validation(parcel.ulpin)
    assert summary_defect.blocker_count == 1
    assert summary_defect.can_approve is False

    vrt_issue = [i for i in summary_defect.issues if i.rule_code == "VRT-003" and not i.passed][0]
    assert vrt_issue.measured_value["overlap_m"] == 0.5
