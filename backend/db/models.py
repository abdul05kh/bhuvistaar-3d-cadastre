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
    checksum_algorithm = Column(String(32), nullable=False, default="SHA-256")
    crs = Column(String(32), nullable=True)
    acquisition_time = Column(DateTime(timezone=True), nullable=True)
    processing_version = Column(String(32), nullable=False, default="1.0.0")
    metadata_json = Column("metadata", JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))


class SpatialUnitModel(Base):
    __tablename__ = "spatial_units"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    active_revision_id = Column(UUID(as_uuid=True), nullable=True)
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


class SpatialUnitRevisionModel(Base):
    __tablename__ = "spatial_unit_revisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    unit_id = Column(UUID(as_uuid=True), ForeignKey("spatial_units.id", ondelete="CASCADE"), nullable=False, index=True)
    revision_number = Column(Integer, nullable=False)
    prototype_vuid = Column(String(64), nullable=False, index=True)
    parent_ulpin = Column(String(14), nullable=False, index=True)
    semantic_type = Column(String(64), nullable=False)
    level_code = Column(String(16), nullable=False)
    z_min = Column(Numeric(8, 3), nullable=False)
    z_max = Column(Numeric(8, 3), nullable=False)
    footprint_area_sqm = Column(Numeric(12, 3), nullable=False)
    volume_cbm = Column(Numeric(14, 3), nullable=False)
    centroid_x = Column(Numeric(12, 3), nullable=False)
    centroid_y = Column(Numeric(12, 3), nullable=False)
    centroid_z = Column(Numeric(8, 3), nullable=False)
    footprint_geom = Column(Geometry(geometry_type="POLYGON", srid=settings.CANONICAL_STORAGE_SRID), nullable=False)
    polyhedron_wkt = Column(Text, nullable=True)
    vuid_full_hash = Column(String(64), nullable=False)
    predecessor_revision_id = Column(UUID(as_uuid=True), ForeignKey("spatial_unit_revisions.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(32), nullable=False, default="GENERATED")
    created_by = Column(String(128), nullable=False, default="SYSTEM")
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))


class ProvenanceRecordModel(Base):
    __tablename__ = "provenance_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    revision_id = Column(UUID(as_uuid=True), ForeignKey("spatial_unit_revisions.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_ulpin = Column(String(14), nullable=False, index=True)
    generation_method = Column(String(64), nullable=False, default="PRISMATIC_EXTRUSION")
    generation_method_version = Column(String(32), nullable=False, default="1.0.0")
    vuid_algorithm_version = Column(String(16), nullable=False, default="v1")
    predecessor_vuid = Column(String(64), nullable=True)
    evidence_sources_json = Column("evidence_sources", JSON, nullable=False, default=list)
    is_verified = Column(Boolean, nullable=False, default=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))


class ValidationRunModel(Base):
    __tablename__ = "validation_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_ulpin = Column(String(14), nullable=False, index=True)
    unit_id = Column(UUID(as_uuid=True), ForeignKey("spatial_units.id", ondelete="SET NULL"), nullable=True)
    revision_id = Column(UUID(as_uuid=True), ForeignKey("spatial_unit_revisions.id", ondelete="SET NULL"), nullable=True)
    gate = Column(String(16), nullable=False, default="GATE_A")
    validator_version = Column(String(32), nullable=False, default="1.0.0")
    rules_evaluated = Column(Integer, nullable=False, default=0)
    passed_rules = Column(Integer, nullable=False, default=0)
    failed_rules = Column(Integer, nullable=False, default=0)
    blocker_count = Column(Integer, nullable=False, default=0)
    error_count = Column(Integer, nullable=False, default=0)
    warning_count = Column(Integer, nullable=False, default=0)
    can_approve = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))


class ValidationIssueModel(Base):
    __tablename__ = "validation_issues"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=True), ForeignKey("validation_runs.id", ondelete="CASCADE"), nullable=False, index=True)
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


class ReviewDecisionModel(Base):
    __tablename__ = "review_decisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    revision_id = Column(UUID(as_uuid=True), ForeignKey("spatial_unit_revisions.id", ondelete="CASCADE"), nullable=False, index=True)
    reviewer_id = Column(String(128), nullable=False)
    actor_context = Column(String(64), nullable=False, default="SIMULATED_PROTOTYPE")
    decision = Column(String(32), nullable=False)
    reason = Column(Text, nullable=False)
    referenced_validation_run_id = Column(UUID(as_uuid=True), ForeignKey("validation_runs.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))


class ApprovalDecisionModel(Base):
    __tablename__ = "approval_decisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    revision_id = Column(UUID(as_uuid=True), ForeignKey("spatial_unit_revisions.id", ondelete="CASCADE"), nullable=False, index=True)
    approver_id = Column(String(128), nullable=False)
    actor_context = Column(String(64), nullable=False, default="SIMULATED_PROTOTYPE")
    status = Column(String(32), nullable=False)
    reason = Column(Text, nullable=False)
    referenced_validation_run_id = Column(UUID(as_uuid=True), ForeignKey("validation_runs.id", ondelete="CASCADE"), nullable=False)
    referenced_review_id = Column(UUID(as_uuid=True), ForeignKey("review_decisions.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))


class AuditEventModel(Base):
    __tablename__ = "audit_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    actor_id = Column(String(128), nullable=False)
    authorization_mode = Column(String(64), nullable=False, default="SIMULATED_PROTOTYPE")
    action = Column(String(64), nullable=False, index=True)
    entity_type = Column(String(64), nullable=False, index=True)
    entity_id = Column(String(128), nullable=False, index=True)
    revision_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    previous_state = Column(String(32), nullable=True)
    new_state = Column(String(32), nullable=True)
    reason = Column(Text, nullable=True)
    correlation_id = Column(String(64), nullable=True)
    metadata_json = Column("metadata", JSON, nullable=False, default=dict)


class ExportRecordModel(Base):
    __tablename__ = "export_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    revision_id = Column(UUID(as_uuid=True), ForeignKey("spatial_unit_revisions.id", ondelete="CASCADE"), nullable=False, index=True)
    export_format = Column(String(16), nullable=False, default="JSON")
    checksum = Column(String(64), nullable=False)
    exported_by = Column(String(128), nullable=False)
    content_json = Column("content", JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))


# ==============================================================================
# SLICE 3 — AI INTELLIGENCE LAYER MODELS
# ==============================================================================

class AIModelRegistryModel(Base):
    __tablename__ = "ai_model_registry"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(128), nullable=False)
    version = Column(String(32), nullable=False)
    task = Column(String(128), nullable=False)
    status = Column(String(32), nullable=False, default="PROTOTYPE")
    description = Column(Text, nullable=False)
    metadata_json = Column("metadata", JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))


class EvidenceObservationModel(Base):
    __tablename__ = "ai_observations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evidence_id = Column(String(64), ForeignKey("evidence_sources.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_ulpin = Column(String(14), ForeignKey("parent_parcels.ulpin", ondelete="CASCADE"), nullable=False, index=True)
    observation_type = Column(String(64), nullable=False, index=True)
    semantic_level = Column(String(32), nullable=True)
    z_min = Column(Numeric(8, 3), nullable=True)
    z_max = Column(Numeric(8, 3), nullable=True)
    confidence = Column(Numeric(5, 4), nullable=False, default=0.9000)
    source_reference = Column(String(255), nullable=False)
    extraction_method = Column(String(64), nullable=False)
    extraction_version = Column(String(32), nullable=False, default="1.0.0")
    model_name = Column(String(128), nullable=False)
    model_version = Column(String(32), nullable=False)
    geometry_geojson = Column("geometry_geojson", JSON, nullable=True)
    input_checksum = Column(String(64), nullable=False)
    metadata_json = Column("metadata", JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))


class AICandidateModel(Base):
    __tablename__ = "ai_candidates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(String(64), unique=True, nullable=False, index=True)
    parent_ulpin = Column(String(14), ForeignKey("parent_parcels.ulpin", ondelete="CASCADE"), nullable=False, index=True)
    level_code = Column(String(32), nullable=False, index=True)
    semantic_type = Column(String(64), nullable=False)
    z_min = Column(Numeric(8, 3), nullable=False)
    z_max = Column(Numeric(8, 3), nullable=False)
    confidence = Column(Numeric(5, 4), nullable=False)
    confidence_band = Column(String(16), nullable=False)
    status = Column(String(32), nullable=False, default="AI_CANDIDATE", index=True)
    source_evidence_ids = Column("source_evidence_ids", JSON, nullable=False, default=list)
    reason_codes = Column("reason_codes", JSON, nullable=False, default=list)
    footprint_geojson = Column("footprint_geojson", JSON, nullable=False)
    footprint_area_sqm = Column(Numeric(12, 3), nullable=False)
    volume_cbm = Column(Numeric(14, 3), nullable=False)
    centroid_x = Column(Numeric(12, 3), nullable=False)
    centroid_y = Column(Numeric(12, 3), nullable=False)
    centroid_z = Column(Numeric(8, 3), nullable=False)
    model_name = Column(String(128), nullable=False)
    model_version = Column(String(32), nullable=False)
    governed_unit_id = Column(UUID(as_uuid=True), ForeignKey("spatial_units.id", ondelete="SET NULL"), nullable=True)
    governed_revision_id = Column(UUID(as_uuid=True), ForeignKey("spatial_unit_revisions.id", ondelete="SET NULL"), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    reviewed_by = Column(String(128), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))


class AIAnomalyModel(Base):
    __tablename__ = "ai_anomalies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    anomaly_id = Column(String(64), unique=True, nullable=False, index=True)
    parent_ulpin = Column(String(14), ForeignKey("parent_parcels.ulpin", ondelete="CASCADE"), nullable=False, index=True)
    anomaly_type = Column(String(64), nullable=False, index=True)
    severity = Column(String(16), nullable=False, index=True)
    affected_units = Column("affected_units", JSON, nullable=False, default=list)
    evidence_ids = Column("evidence_ids", JSON, nullable=False, default=list)
    confidence = Column(Numeric(5, 4), nullable=False, default=0.9000)
    reason_codes = Column("reason_codes", JSON, nullable=False, default=list)
    recommended_action = Column(Text, nullable=False)
    model_name = Column(String(128), nullable=False)
    model_version = Column(String(32), nullable=False)
    resolved = Column(Boolean, nullable=False, default=False)
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))


# ==============================================================================
# SLICE 4 — VALIDATION INTELLIGENCE, EXPLAINABILITY & REPRODUCIBILITY MODELS
# ==============================================================================

class ValidationDisagreementModel(Base):
    __tablename__ = "validation_disagreements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    disagreement_id = Column(String(64), unique=True, nullable=False, index=True)
    parent_ulpin = Column(String(14), ForeignKey("parent_parcels.ulpin", ondelete="CASCADE"), nullable=False, index=True)
    candidate_id = Column(String(64), nullable=True, index=True)
    disagreement_type = Column(String(64), nullable=False, index=True)
    severity = Column(String(16), nullable=False, index=True)
    ai_confidence = Column(Numeric(5, 4), nullable=False)
    validation_status = Column(String(32), nullable=False)
    human_decision = Column(String(32), nullable=True)
    rule_codes = Column("rule_codes", JSON, nullable=False, default=list)
    explanation = Column(Text, nullable=False)
    measured_values = Column("measured_values", JSON, nullable=True)
    thresholds = Column("thresholds", JSON, nullable=True)
    model_name = Column(String(128), nullable=False)
    model_version = Column(String(32), nullable=False)
    ruleset_version = Column(String(32), nullable=False, default="1.0.0")
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))


class ReproducibilitySnapshotModel(Base):
    __tablename__ = "reproducibility_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    snapshot_id = Column(String(64), unique=True, nullable=False, index=True)
    parent_ulpin = Column(String(14), ForeignKey("parent_parcels.ulpin", ondelete="CASCADE"), nullable=False, index=True)
    target_type = Column(String(32), nullable=False)
    target_id = Column(String(64), nullable=False, index=True)
    revision_id = Column(UUID(as_uuid=True), nullable=True)
    reproducibility_status = Column(String(32), nullable=False)
    input_evidence_hashes = Column("input_evidence_hashes", JSON, nullable=False, default=list)
    geometry_geojson = Column("geometry_geojson", JSON, nullable=False)
    crs = Column(String(32), nullable=False)
    generation_method = Column(String(64), nullable=False)
    model_name = Column(String(128), nullable=False)
    model_version = Column(String(32), nullable=False)
    model_config_hash = Column(String(64), nullable=False)
    validation_ruleset_version = Column(String(32), nullable=False, default="1.0.0")
    software_commit = Column(String(64), nullable=False)
    snapshot_hash = Column(String(64), nullable=False)
    metadata_json = Column("metadata", JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))


class EvaluationRunModel(Base):
    __tablename__ = "evaluation_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(String(64), unique=True, nullable=False, index=True)
    scenario_name = Column(String(64), nullable=False)
    dataset_name = Column(String(64), nullable=False)
    dataset_version = Column(String(32), nullable=False)
    is_synthetic = Column(Boolean, nullable=False, default=True)
    model_name = Column(String(128), nullable=False)
    model_version = Column(String(32), nullable=False)
    ruleset_version = Column(String(32), nullable=False, default="1.0.0")
    total_cases = Column(Integer, nullable=False)
    metrics_json = Column("metrics", JSON, nullable=False, default=dict)
    disagreements_count = Column(Integer, nullable=False, default=0)
    execution_time_ms = Column(Numeric(10, 2), nullable=False)
    status = Column(String(32), nullable=False, default="COMPLETED")
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))



