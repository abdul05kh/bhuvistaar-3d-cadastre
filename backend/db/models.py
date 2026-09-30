import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Numeric,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    JSON,
    Integer,
    Table
)
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from backend.db.session import Base
from backend.config import settings


unit_evidence_links = Table(
    "unit_evidence_links",
    Base.metadata,
    Column("unit_id", UUID(as_uuid=True), ForeignKey("spatial_units.id", ondelete="CASCADE"), primary_key=True),
    Column("evidence_id", String(64), ForeignKey("evidence_sources.id", ondelete="CASCADE"), primary_key=True)
)


class ParentParcelModel(Base):
    __tablename__ = "parent_parcels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ulpin = Column(String(14), unique=True, nullable=False, index=True)
    crs = Column(String(32), nullable=False)
    storage_srid = Column(Integer, nullable=False, default=settings.CANONICAL_STORAGE_SRID)
    geometry = Column(Geometry(geometry_type="POLYGON", srid=settings.CANONICAL_STORAGE_SRID), nullable=False)
    area_sqm = Column(Numeric(12, 3), nullable=False)
    status = Column(String(32), nullable=False, default="DRAFT")
    metadata_json = Column("metadata", JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))


class EvidenceSourceModel(Base):
    __tablename__ = "evidence_sources"

    id = Column(String(64), primary_key=True)
    parent_ulpin = Column(String(14), ForeignKey("parent_parcels.ulpin", ondelete="CASCADE"), nullable=False, index=True)
    evidence_type = Column(String(64), nullable=False)
    provider = Column(String(128), nullable=False)
    source_reference = Column(String(255), nullable=False)
    checksum = Column(String(64), nullable=False)
    crs = Column(String(32), nullable=True)
    acquisition_time = Column(DateTime(timezone=True), nullable=True)
    processing_version = Column(String(32), nullable=False, default="1.0.0")
    metadata_json = Column("metadata", JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))


class SpatialUnitModel(Base):
    __tablename__ = "spatial_units"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prototype_vuid = Column(String(64), unique=True, nullable=False, index=True)
    parent_parcel_id = Column(UUID(as_uuid=True), ForeignKey("parent_parcels.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_ulpin = Column(String(14), nullable=False, index=True)
    semantic_type = Column(String(64), nullable=False)
    level_code = Column(String(16), nullable=False, index=True)
    z_min = Column(Numeric(8, 3), nullable=False)
    z_max = Column(Numeric(8, 3), nullable=False)
    footprint_area_sqm = Column(Numeric(12, 3), nullable=False)
    volume_cbm = Column(Numeric(14, 3), nullable=False)
    centroid_x = Column(Numeric(12, 3), nullable=False)
    centroid_y = Column(Numeric(12, 3), nullable=False)
    centroid_z = Column(Numeric(8, 3), nullable=False)
    footprint_geom = Column(Geometry(geometry_type="POLYGON", srid=settings.CANONICAL_STORAGE_SRID), nullable=False)
    polyhedron_wkt = Column(Text, nullable=True)
    confidence = Column(String(32), nullable=False, default="VERIFIED")
    generation_method = Column(String(64), nullable=False, default="PRISMATIC_EXTRUSION")
    vuid_algorithm_version = Column(String(16), nullable=False, default="v1")
    vuid_full_hash = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False, default="GENERATED")
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))


class ValidationIssueModel(Base):
    __tablename__ = "validation_issues"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    rule_code = Column(String(32), nullable=False)
    severity = Column(String(16), nullable=False, index=True)
    object_type = Column(String(32), nullable=False)
    object_id = Column(String(64), nullable=False, index=True)
    passed = Column(Boolean, nullable=False)
    message = Column(Text, nullable=False)
    measured_value = Column(JSON, nullable=True)
    threshold = Column(JSON, nullable=True)
    suggested_action = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
