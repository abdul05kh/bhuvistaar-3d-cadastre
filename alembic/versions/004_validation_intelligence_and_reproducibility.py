"""004_validation_intelligence_and_reproducibility

Revision ID: 004_validation_intelligence
Revises: 003_ai_intelligence_layer
Create Date: 2026-09-30 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '004_validation_intelligence'
down_revision: Union[str, None] = '003_ai_intelligence_layer'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Validation Disagreements Table
    op.create_table(
        'validation_disagreements',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('disagreement_id', sa.String(64), nullable=False),
        sa.Column('parent_ulpin', sa.String(14), sa.ForeignKey('parent_parcels.ulpin', ondelete='CASCADE'), nullable=False),
        sa.Column('candidate_id', sa.String(64), nullable=True),
        sa.Column('disagreement_type', sa.String(64), nullable=False),
        sa.Column('severity', sa.String(16), nullable=False),
        sa.Column('ai_confidence', sa.Numeric(5, 4), nullable=False),
        sa.Column('validation_status', sa.String(32), nullable=False),
        sa.Column('human_decision', sa.String(32), nullable=True),
        sa.Column('rule_codes', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('explanation', sa.Text(), nullable=False),
        sa.Column('measured_values', sa.JSON(), nullable=True),
        sa.Column('thresholds', sa.JSON(), nullable=True),
        sa.Column('model_name', sa.String(128), nullable=False),
        sa.Column('model_version', sa.String(32), nullable=False),
        sa.Column('ruleset_version', sa.String(32), nullable=False, server_default='1.0.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )
    op.create_index('ix_validation_disagreements_disagreement_id', 'validation_disagreements', ['disagreement_id'], unique=True)
    op.create_index('ix_validation_disagreements_parent_ulpin', 'validation_disagreements', ['parent_ulpin'])
    op.create_index('ix_validation_disagreements_candidate_id', 'validation_disagreements', ['candidate_id'])
    op.create_index('ix_validation_disagreements_type', 'validation_disagreements', ['disagreement_type'])
    op.create_index('ix_validation_disagreements_severity', 'validation_disagreements', ['severity'])

    # 2. Reproducibility Snapshots Table
    op.create_table(
        'reproducibility_snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('snapshot_id', sa.String(64), nullable=False),
        sa.Column('parent_ulpin', sa.String(14), sa.ForeignKey('parent_parcels.ulpin', ondelete='CASCADE'), nullable=False),
        sa.Column('target_type', sa.String(32), nullable=False),
        sa.Column('target_id', sa.String(64), nullable=False),
        sa.Column('revision_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reproducibility_status', sa.String(32), nullable=False),
        sa.Column('input_evidence_hashes', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('geometry_geojson', sa.JSON(), nullable=False),
        sa.Column('crs', sa.String(32), nullable=False),
        sa.Column('generation_method', sa.String(64), nullable=False),
        sa.Column('model_name', sa.String(128), nullable=False),
        sa.Column('model_version', sa.String(32), nullable=False),
        sa.Column('model_config_hash', sa.String(64), nullable=False),
        sa.Column('validation_ruleset_version', sa.String(32), nullable=False, server_default='1.0.0'),
        sa.Column('software_commit', sa.String(64), nullable=False),
        sa.Column('snapshot_hash', sa.String(64), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )
    op.create_index('ix_reproducibility_snapshots_snapshot_id', 'reproducibility_snapshots', ['snapshot_id'], unique=True)
    op.create_index('ix_reproducibility_snapshots_parent_ulpin', 'reproducibility_snapshots', ['parent_ulpin'])
    op.create_index('ix_reproducibility_snapshots_target_id', 'reproducibility_snapshots', ['target_id'])

    # 3. Evaluation Runs Table
    op.create_table(
        'evaluation_runs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('run_id', sa.String(64), nullable=False),
        sa.Column('scenario_name', sa.String(64), nullable=False),
        sa.Column('dataset_name', sa.String(64), nullable=False),
        sa.Column('dataset_version', sa.String(32), nullable=False),
        sa.Column('is_synthetic', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('model_name', sa.String(128), nullable=False),
        sa.Column('model_version', sa.String(32), nullable=False),
        sa.Column('ruleset_version', sa.String(32), nullable=False, server_default='1.0.0'),
        sa.Column('total_cases', sa.Integer(), nullable=False),
        sa.Column('metrics', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('disagreements_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('execution_time_ms', sa.Numeric(10, 2), nullable=False),
        sa.Column('status', sa.String(32), nullable=False, server_default='COMPLETED'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )
    op.create_index('ix_evaluation_runs_run_id', 'evaluation_runs', ['run_id'], unique=True)


def downgrade() -> None:
    op.drop_table('evaluation_runs')
    op.drop_table('reproducibility_snapshots')
    op.drop_table('validation_disagreements')
