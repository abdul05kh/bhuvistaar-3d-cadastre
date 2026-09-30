import React from 'react';
import { Box, Shield, Edit3, History, Download, AlertTriangle, Hash, HelpCircle } from 'lucide-react';
import { SpatialUnit } from '../../types';

interface UnitInspectorProps {
  unit: SpatialUnit | null;
  onRequestCorrection: (unit: SpatialUnit) => void;
  onViewRevisions: (unit: SpatialUnit) => void;
  onExport: (revisionId: string) => void;
  onOpenReproducibility?: (targetId: string) => void;
  onExplainValidation?: () => void;
  isConflicting: boolean;
}

export const UnitInspector: React.FC<UnitInspectorProps> = ({
  unit,
  onRequestCorrection,
  onViewRevisions,
  onExport,
  onOpenReproducibility,
  onExplainValidation,
  isConflicting,
}) => {
  if (!unit) {
    return (
      <div className="panel panel-right" style={{ width: '340px', height: '100%' }}>
        <div className="panel-header">Spatial Unit Inspector</div>
        <div className="panel-body" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
          Select a spatial unit from the 3D scene or hierarchy tree.
        </div>
      </div>
    );
  }

  return (
    <div className="panel panel-right" style={{ width: '340px', height: '100%' }}>
      <div className="panel-header">
        <span>Spatial Unit Inspector</span>
        <span className="badge badge-info">Level {unit.level_code}</span>
      </div>

      <div className="panel-body" style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
        {/* Prototype VUID Card */}
        <div className="card" style={{ backgroundColor: 'var(--bg-app)', border: '1px solid var(--border-strong)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
            <span style={{ fontSize: '11px', color: 'var(--text-secondary)', fontWeight: 600 }}>
              PROTOTYPE VUID
            </span>
            <span className="badge badge-prototype">v1 Algorithm</span>
          </div>

          <div
            className="code-token"
            style={{
              fontSize: '12px',
              fontWeight: 700,
              color: 'var(--color-primary)',
              wordBreak: 'break-all',
              marginBottom: '6px',
            }}
          >
            {unit.prototype_vuid}
          </div>

          <div
            style={{
              fontSize: '10px',
              color: '#f59e0b',
              backgroundColor: 'rgba(245, 158, 11, 0.08)',
              padding: '4px 6px',
              borderRadius: '4px',
              border: '1px solid rgba(245, 158, 11, 0.2)',
            }}
          >
            * Prototype identifier — not an official 3D ULPIN.
          </div>
        </div>

        {/* Conflict Warning */}
        {isConflicting && (
          <div
            className="card card-danger"
            style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}
          >
            <AlertTriangle size={18} style={{ color: 'var(--color-blocker)', flexShrink: 0, marginTop: '2px' }} />
            <div>
              <div style={{ fontWeight: 600, color: 'var(--color-blocker)', fontSize: '12px' }}>
                Approval Blocked (VRT-003)
              </div>
              <div style={{ fontSize: '11px', color: 'var(--text-main)', marginTop: '2px' }}>
                Ceiling elevation overlaps with upper level stratum. Non-destructive correction required.
              </div>
            </div>
          </div>
        )}

        {/* Spatial & Elevation Metrics */}
        <div>
          <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '8px', textTransform: 'uppercase' }}>
            Elevation & Geometry
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
            <div className="card" style={{ padding: '8px' }}>
              <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>Z Minimum</span>
              <div className="code-token" style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-main)' }}>
                {unit.z_min.toFixed(3)} m
              </div>
            </div>

            <div className="card" style={{ padding: '8px', borderColor: isConflicting ? 'var(--color-blocker)' : 'var(--border-subtle)' }}>
              <span style={{ fontSize: '10px', color: isConflicting ? 'var(--color-blocker)' : 'var(--text-muted)' }}>
                Z Maximum (Ceiling)
              </span>
              <div className="code-token" style={{ fontSize: '13px', fontWeight: 600, color: isConflicting ? 'var(--color-blocker)' : 'var(--text-main)' }}>
                {unit.z_max.toFixed(3)} m
              </div>
            </div>

            <div className="card" style={{ padding: '8px' }}>
              <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>Floor Height</span>
              <div className="code-token" style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-main)' }}>
                {unit.height_m.toFixed(3)} m
              </div>
            </div>

            <div className="card" style={{ padding: '8px' }}>
              <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>Volume Extrusion</span>
              <div className="code-token" style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-main)' }}>
                {unit.volume_cbm.toFixed(1)} m³
              </div>
            </div>
          </div>

          <div className="card" style={{ marginTop: '8px', padding: '8px', display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-secondary)' }}>Footprint Area</span>
            <span className="code-token" style={{ fontWeight: 600 }}>{unit.footprint_area_sqm.toFixed(1)} m²</span>
          </div>

          <div className="card" style={{ padding: '8px', display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-secondary)' }}>Centroid (X, Y, Z)</span>
            <span className="code-token" style={{ fontSize: '10px' }}>
              {unit.centroid_x.toFixed(1)}, {unit.centroid_y.toFixed(1)}, {unit.centroid_z.toFixed(2)}
            </span>
          </div>
        </div>

        {/* Governance & Lineage */}
        <div>
          <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '8px', textTransform: 'uppercase' }}>
            Governance & Lineage
          </div>

          <div className="card" style={{ padding: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ color: 'var(--text-secondary)' }}>Current Revision</span>
            <span className="badge badge-info">Revision {unit.revision_number || 1}</span>
          </div>

          <div className="card" style={{ padding: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ color: 'var(--text-secondary)' }}>Workflow Status</span>
            <span className={`badge ${unit.status === 'APPROVED' ? 'badge-success' : 'badge-warning'}`}>
              {unit.status}
            </span>
          </div>
        </div>

        {/* Action Controls */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: 'auto' }}>
          <button
            className="btn btn-warning"
            style={{ width: '100%' }}
            onClick={() => onRequestCorrection(unit)}
          >
            <Edit3 size={14} />
            Request / Submit Correction
          </button>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
            <button
              className="btn btn-sm"
              onClick={() => onViewRevisions(unit)}
            >
              <History size={13} />
              Revisions
            </button>
            <button
              className="btn btn-sm"
              onClick={() => unit.active_revision_id && onExport(unit.active_revision_id)}
              disabled={!unit.active_revision_id}
            >
              <Download size={13} />
              Export JSON
            </button>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
            {onOpenReproducibility && (
              <button
                className="btn btn-sm"
                style={{ fontSize: '0.7rem' }}
                onClick={() => onOpenReproducibility(unit.prototype_vuid)}
                title="View cryptographic reproducibility snapshot"
              >
                <Hash size={12} />
                Snapshot
              </button>
            )}
            {onExplainValidation && (
              <button
                className="btn btn-sm"
                style={{ fontSize: '0.7rem' }}
                onClick={onExplainValidation}
                title="Explain validation rule outcomes"
              >
                <HelpCircle size={12} />
                Validation
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
