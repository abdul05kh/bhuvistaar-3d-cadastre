"""003_ai_intelligence_layer

Revision ID: 003_ai_intelligence_layer
Revises: 002_governance_and_provenance
Create Date: 2026-09-30 09:35:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '003_ai_intelligence_layer'
down_revision: Union[str, None] = '002_governance_and_provenance'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. AI Model Registry Table
    op.create_table(
        'ai_model_registry',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('model_id', sa.String(64), nullable=False),
        sa.Column('name', sa.String(128), nullable=False),
        sa.Column('version', sa.String(32), nullable=False),
        sa.Column('task', sa.String(128), nullable=False),
        sa.Column('status', sa.String(32), nullable=False, server_default='PROTOTYPE'),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )
    op.create_index('ix_ai_model_registry_model_id', 'ai_model_registry', ['model_id'], unique=True)

    # 2. AI Observations Table (Layer A)
    op.create_table(
        'ai_observations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('evidence_id', sa.String(64), sa.ForeignKey('evidence_sources.id', ondelete='CASCADE'), nullable=False),
        sa.Column('parent_ulpin', sa.String(14), sa.ForeignKey('parent_parcels.ulpin', ondelete='CASCADE'), nullable=False),
        sa.Column('observation_type', sa.String(64), nullable=False),
        sa.Column('semantic_level', sa.String(32), nullable=True),
        sa.Column('z_min', sa.Numeric(8, 3), nullable=True),
        sa.Column('z_max', sa.Numeric(8, 3), nullable=True),
        sa.Column('confidence', sa.Numeric(5, 4), nullable=False, server_default='0.9000'),
        sa.Column('source_reference', sa.String(255), nullable=False),
        sa.Column('extraction_method', sa.String(64), nullable=False),
        sa.Column('extraction_version', sa.String(32), nullable=False, server_default='1.0.0'),
        sa.Column('model_name', sa.String(128), nullable=False),
        sa.Column('model_version', sa.String(32), nullable=False),
        sa.Column('geometry_geojson', sa.JSON(), nullable=True),
        sa.Column('input_checksum', sa.String(64), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )
    op.create_index('ix_ai_observations_evidence_id', 'ai_observations', ['evidence_id'])
    op.create_index('ix_ai_observations_parent_ulpin', 'ai_observations', ['parent_ulpin'])
    op.create_index('ix_ai_observations_type', 'ai_observations', ['observation_type'])

    # 3. AI Candidates Table (Layer B)
    op.create_table(
        'ai_candidates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('candidate_id', sa.String(64), nullable=False),
        sa.Column('parent_ulpin', sa.String(14), sa.ForeignKey('parent_parcels.ulpin', ondelete='CASCADE'), nullable=False),
        sa.Column('level_code', sa.String(32), nullable=False),
        sa.Column('semantic_type', sa.String(64), nullable=False),
        sa.Column('z_min', sa.Numeric(8, 3), nullable=False),
        sa.Column('z_max', sa.Numeric(8, 3), nullable=False),
        sa.Column('confidence', sa.Numeric(5, 4), nullable=False),
        sa.Column('confidence_band', sa.String(16), nullable=False),
        sa.Column('status', sa.String(32), nullable=False, server_default='AI_CANDIDATE'),
        sa.Column('source_evidence_ids', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('reason_codes', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('footprint_geojson', sa.JSON(), nullable=False),
        sa.Column('footprint_area_sqm', sa.Numeric(12, 3), nullable=False),
        sa.Column('volume_cbm', sa.Numeric(14, 3), nullable=False),
        sa.Column('centroid_x', sa.Numeric(12, 3), nullable=False),
        sa.Column('centroid_y', sa.Numeric(12, 3), nullable=False),
        sa.Column('centroid_z', sa.Numeric(8, 3), nullable=False),
        sa.Column('model_name', sa.String(128), nullable=False),
        sa.Column('model_version', sa.String(32), nullable=False),
        sa.Column('governed_unit_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('spatial_units.id', ondelete='SET NULL'), nullable=True),
        sa.Column('governed_revision_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('spatial_unit_revisions.id', ondelete='SET NULL'), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('reviewed_by', sa.String(128), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )
    op.create_index('ix_ai_candidates_candidate_id', 'ai_candidates', ['candidate_id'], unique=True)
    op.create_index('ix_ai_candidates_parent_ulpin', 'ai_candidates', ['parent_ulpin'])
    op.create_index('ix_ai_candidates_level_code', 'ai_candidates', ['level_code'])
    op.create_index('ix_ai_candidates_status', 'ai_candidates', ['status'])

    # 4. AI Anomalies Table (Layer C)
    op.create_table(
        'ai_anomalies',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('anomaly_id', sa.String(64), nullable=False),
        sa.Column('parent_ulpin', sa.String(14), sa.ForeignKey('parent_parcels.ulpin', ondelete='CASCADE'), nullable=False),
        sa.Column('anomaly_type', sa.String(64), nullable=False),
        sa.Column('severity', sa.String(16), nullable=False),
        sa.Column('affected_units', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('evidence_ids', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('confidence', sa.Numeric(5, 4), nullable=False, server_default='0.9000'),
        sa.Column('reason_codes', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('recommended_action', sa.Text(), nullable=False),
        sa.Column('model_name', sa.String(128), nullable=False),
        sa.Column('model_version', sa.String(32), nullable=False),
        sa.Column('resolved', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )
    op.create_index('ix_ai_anomalies_anomaly_id', 'ai_anomalies', ['anomaly_id'], unique=True)
    op.create_index('ix_ai_anomalies_parent_ulpin', 'ai_anomalies', ['parent_ulpin'])
    op.create_index('ix_ai_anomalies_type', 'ai_anomalies', ['anomaly_type'])
    op.create_index('ix_ai_anomalies_severity', 'ai_anomalies', ['severity'])


def downgrade() -> None:
    op.drop_table('ai_anomalies')
    op.drop_table('ai_candidates')
    op.drop_table('ai_observations')
    op.drop_table('ai_model_registry')
