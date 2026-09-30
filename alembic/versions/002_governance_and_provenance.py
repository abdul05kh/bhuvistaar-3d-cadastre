"""002_governance_and_provenance

Revision ID: 002_governance_and_provenance
Revises: 001_initial_spatial_schema
Create Date: 2026-09-30 08:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import geoalchemy2

revision: str = '002_governance_and_provenance'
down_revision: Union[str, None] = '001_initial_spatial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add checksum_algorithm to evidence_sources
    op.add_column(
        'evidence_sources',
        sa.Column('checksum_algorithm', sa.String(32), nullable=False, server_default='SHA-256')
    )

    # 2. Add active_revision_id to spatial_units
    op.add_column(
        'spatial_units',
        sa.Column('active_revision_id', postgresql.UUID(as_uuid=True), nullable=True)
    )

    # 3. Create spatial_unit_revisions
    op.create_table(
        'spatial_unit_revisions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('unit_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('spatial_units.id', ondelete='CASCADE'), nullable=False),
        sa.Column('revision_number', sa.Integer(), nullable=False),
        sa.Column('prototype_vuid', sa.String(64), nullable=False),
        sa.Column('parent_ulpin', sa.String(14), nullable=False),
        sa.Column('semantic_type', sa.String(64), nullable=False),
        sa.Column('level_code', sa.String(16), nullable=False),
        sa.Column('z_min', sa.Numeric(8, 3), nullable=False),
        sa.Column('z_max', sa.Numeric(8, 3), nullable=False),
        sa.Column('footprint_area_sqm', sa.Numeric(12, 3), nullable=False),
        sa.Column('volume_cbm', sa.Numeric(14, 3), nullable=False),
        sa.Column('centroid_x', sa.Numeric(12, 3), nullable=False),
        sa.Column('centroid_y', sa.Numeric(12, 3), nullable=False),
        sa.Column('centroid_z', sa.Numeric(8, 3), nullable=False),
        sa.Column('footprint_geom', geoalchemy2.types.Geometry(geometry_type='POLYGON', srid=32643), nullable=False),
        sa.Column('polyhedron_wkt', sa.Text(), nullable=True),
        sa.Column('vuid_full_hash', sa.String(64), nullable=False),
        sa.Column('predecessor_revision_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('spatial_unit_revisions.id', ondelete='SET NULL'), nullable=True),
        sa.Column('status', sa.String(32), nullable=False, server_default='GENERATED'),
        sa.Column('created_by', sa.String(128), nullable=False, server_default='SYSTEM'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('idx_revisions_unit_id', 'spatial_unit_revisions', ['unit_id'])
    op.create_index('idx_revisions_vuid', 'spatial_unit_revisions', ['prototype_vuid'])
    op.create_index('idx_revisions_parent_ulpin', 'spatial_unit_revisions', ['parent_ulpin'])

    # 4. Create provenance_records
    op.create_table(
        'provenance_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('revision_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('spatial_unit_revisions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('parent_ulpin', sa.String(14), nullable=False),
        sa.Column('generation_method', sa.String(64), nullable=False, server_default='PRISMATIC_EXTRUSION'),
        sa.Column('generation_method_version', sa.String(32), nullable=False, server_default='1.0.0'),
        sa.Column('vuid_algorithm_version', sa.String(16), nullable=False, server_default='v1'),
        sa.Column('predecessor_vuid', sa.String(64), nullable=True),
        sa.Column('evidence_sources', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('idx_provenance_revision_id', 'provenance_records', ['revision_id'])
    op.create_index('idx_provenance_parent_ulpin', 'provenance_records', ['parent_ulpin'])

    # 5. Create validation_runs
    op.create_table(
        'validation_runs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('parent_ulpin', sa.String(14), nullable=False),
        sa.Column('unit_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('spatial_units.id', ondelete='SET NULL'), nullable=True),
        sa.Column('revision_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('spatial_unit_revisions.id', ondelete='SET NULL'), nullable=True),
        sa.Column('gate', sa.String(16), nullable=False, server_default='GATE_A'),
        sa.Column('validator_version', sa.String(32), nullable=False, server_default='1.0.0'),
        sa.Column('rules_evaluated', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('passed_rules', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('failed_rules', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('blocker_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('warning_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('can_approve', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('idx_validation_runs_parent_ulpin', 'validation_runs', ['parent_ulpin'])

    # 6. Create review_decisions
    op.create_table(
        'review_decisions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('revision_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('spatial_unit_revisions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('reviewer_id', sa.String(128), nullable=False),
        sa.Column('actor_context', sa.String(64), nullable=False, server_default='SIMULATED_PROTOTYPE'),
        sa.Column('decision', sa.String(32), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('referenced_validation_run_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('validation_runs.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('idx_reviews_revision_id', 'review_decisions', ['revision_id'])

    # 7. Create approval_decisions
    op.create_table(
        'approval_decisions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('revision_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('spatial_unit_revisions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('approver_id', sa.String(128), nullable=False),
        sa.Column('actor_context', sa.String(64), nullable=False, server_default='SIMULATED_PROTOTYPE'),
        sa.Column('status', sa.String(32), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('referenced_validation_run_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('validation_runs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('referenced_review_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('review_decisions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('idx_approvals_revision_id', 'approval_decisions', ['revision_id'])

    # 8. Create audit_events
    op.create_table(
        'audit_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('actor_id', sa.String(128), nullable=False),
        sa.Column('authorization_mode', sa.String(64), nullable=False, server_default='SIMULATED_PROTOTYPE'),
        sa.Column('action', sa.String(64), nullable=False),
        sa.Column('entity_type', sa.String(64), nullable=False),
        sa.Column('entity_id', sa.String(128), nullable=False),
        sa.Column('revision_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('previous_state', sa.String(32), nullable=True),
        sa.Column('new_state', sa.String(32), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('correlation_id', sa.String(64), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=False, server_default='{}')
    )
    op.create_index('idx_audit_events_action', 'audit_events', ['action'])
    op.create_index('idx_audit_events_entity', 'audit_events', ['entity_type', 'entity_id'])
    op.create_index('idx_audit_events_revision_id', 'audit_events', ['revision_id'])

    # 9. Create export_records
    op.create_table(
        'export_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('revision_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('spatial_unit_revisions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('export_format', sa.String(16), nullable=False, server_default='JSON'),
        sa.Column('checksum', sa.String(64), nullable=False),
        sa.Column('exported_by', sa.String(128), nullable=False),
        sa.Column('content', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('idx_export_records_revision_id', 'export_records', ['revision_id'])


def downgrade() -> None:
    op.drop_table('export_records')
    op.drop_table('audit_events')
    op.drop_table('approval_decisions')
    op.drop_table('review_decisions')
    op.drop_table('validation_runs')
    op.drop_table('provenance_records')
    op.drop_table('spatial_unit_revisions')
    op.drop_column('spatial_units', 'active_revision_id')
    op.drop_column('evidence_sources', 'checksum_algorithm')
