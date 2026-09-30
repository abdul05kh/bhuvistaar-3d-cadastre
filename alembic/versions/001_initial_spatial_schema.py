"""001_initial_spatial_schema

Revision ID: 001_initial_spatial_schema
Revises: 
Create Date: 2026-09-30 08:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import geoalchemy2

revision: str = '001_initial_spatial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 0. Ensure PostGIS extension exists
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")

    # 1. parent_parcels
    op.create_table(
        'parent_parcels',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('ulpin', sa.String(14), nullable=False, unique=True),
        sa.Column('crs', sa.String(32), nullable=False),
        sa.Column('storage_srid', sa.Integer(), nullable=False, server_default='32643'),
        sa.Column('geometry', geoalchemy2.types.Geometry(geometry_type='POLYGON', srid=32643), nullable=False),
        sa.Column('area_sqm', sa.Numeric(12, 3), nullable=False),
        sa.Column('status', sa.String(32), nullable=False, server_default='DRAFT'),
        sa.Column('metadata', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('idx_parent_parcels_ulpin', 'parent_parcels', ['ulpin'])

    # 2. evidence_sources
    op.create_table(
        'evidence_sources',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('parent_ulpin', sa.String(14), sa.ForeignKey('parent_parcels.ulpin', ondelete='CASCADE'), nullable=False),
        sa.Column('evidence_type', sa.String(64), nullable=False),
        sa.Column('provider', sa.String(128), nullable=False),
        sa.Column('source_reference', sa.String(255), nullable=False),
        sa.Column('checksum', sa.String(64), nullable=False),
        sa.Column('crs', sa.String(32), nullable=True),
        sa.Column('acquisition_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('processing_version', sa.String(32), nullable=False, server_default='1.0.0'),
        sa.Column('metadata', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('idx_evidence_sources_parent_ulpin', 'evidence_sources', ['parent_ulpin'])

    # 3. spatial_units
    op.create_table(
        'spatial_units',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('prototype_vuid', sa.String(64), nullable=False, unique=True),
        sa.Column('parent_parcel_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('parent_parcels.id', ondelete='CASCADE'), nullable=False),
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
        sa.Column('confidence', sa.String(32), nullable=False, server_default='VERIFIED'),
        sa.Column('generation_method', sa.String(64), nullable=False, server_default='PRISMATIC_EXTRUSION'),
        sa.Column('vuid_algorithm_version', sa.String(16), nullable=False, server_default='v1'),
        sa.Column('vuid_full_hash', sa.String(64), nullable=False),
        sa.Column('status', sa.String(32), nullable=False, server_default='GENERATED'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('idx_spatial_units_vuid', 'spatial_units', ['prototype_vuid'])
    op.create_index('idx_spatial_units_parent_id', 'spatial_units', ['parent_parcel_id'])
    op.create_index('idx_spatial_units_parent_ulpin', 'spatial_units', ['parent_ulpin'])

    # 4. unit_evidence_links
    op.create_table(
        'unit_evidence_links',
        sa.Column('unit_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('spatial_units.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('evidence_id', sa.String(64), sa.ForeignKey('evidence_sources.id', ondelete='CASCADE'), primary_key=True)
    )

    # 5. validation_issues
    op.create_table(
        'validation_issues',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('run_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rule_code', sa.String(32), nullable=False),
        sa.Column('severity', sa.String(16), nullable=False),
        sa.Column('object_type', sa.String(32), nullable=False),
        sa.Column('object_id', sa.String(64), nullable=False),
        sa.Column('passed', sa.Boolean(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('measured_value', sa.JSON(), nullable=True),
        sa.Column('threshold', sa.JSON(), nullable=True),
        sa.Column('suggested_action', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('idx_validation_issues_run_id', 'validation_issues', ['run_id'])
    op.create_index('idx_validation_issues_object_id', 'validation_issues', ['object_id'])


def downgrade() -> None:
    op.drop_table('validation_issues')
    op.drop_table('unit_evidence_links')
    op.drop_table('spatial_units')
    op.drop_table('evidence_sources')
    op.drop_table('parent_parcels')
