import React from 'react';
import { Layers, Box, AlertTriangle, CheckCircle } from 'lucide-react';
import { ParentParcel, SpatialUnit } from '../../types';

interface UnitTreeProps {
  parcel: ParentParcel | null;
  units: SpatialUnit[];
  selectedUnitId: string | null;
  onSelectUnit: (unitId: string) => void;
  hasOverlapDefect: boolean;
}

export const UnitTree: React.FC<UnitTreeProps> = ({
  parcel,
  units,
  selectedUnitId,
  onSelectUnit,
  hasOverlapDefect,
}) => {
  return (
    <div className="panel" style={{ width: '280px', height: '100%' }}>
      <div className="panel-header">
        <span>Cadastral Hierarchy</span>
        <span className="badge badge-info">{units.length} Units</span>
      </div>

      <div className="panel-body">
        {/* Parent Parcel Node */}
        {parcel && (
          <div
            className="card"
            style={{
              borderColor: 'var(--border-subtle)',
              borderLeft: '3px solid #eab308',
              marginBottom: '12px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <Layers size={14} style={{ color: '#eab308' }} />
              <span style={{ fontWeight: 600, color: 'var(--text-main)', fontSize: '12px' }}>
                Parent Parcel
              </span>
            </div>
            <div className="code-token" style={{ color: 'var(--text-secondary)', marginBottom: '4px' }}>
              {parcel.ulpin}
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
              Area: {parcel.area_sqm.toFixed(1)} m² | EPSG:{parcel.storage_srid}
            </div>
          </div>
        )}

        {/* Spatial Units List */}
        <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px', textTransform: 'uppercase' }}>
          3D Spatial Units (Floors)
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          {units.map((u) => {
            const isSelected = u.id === selectedUnitId;
            const isConflicting = hasOverlapDefect && (u.level_code === 'L01' || u.level_code === 'L02');

            return (
              <div
                key={u.id}
                className={`card ${isSelected ? 'card-selected' : ''}`}
                style={{
                  cursor: 'pointer',
                  borderLeft: isConflicting
                    ? '3px solid var(--color-blocker)'
                    : isSelected
                    ? '3px solid var(--color-primary)'
                    : '1px solid var(--border-subtle)',
                }}
                onClick={() => onSelectUnit(u.id)}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Box size={13} style={{ color: isConflicting ? 'var(--color-blocker)' : 'var(--color-primary)' }} />
                    <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>
                      Level {u.level_code}
                    </span>
                  </div>

                  {isConflicting ? (
                    <span className="badge badge-blocker" style={{ fontSize: '10px' }}>
                      <AlertTriangle size={10} />
                      CONFLICT
                    </span>
                  ) : u.status === 'APPROVED' ? (
                    <span className="badge badge-success" style={{ fontSize: '10px' }}>
                      <CheckCircle size={10} />
                      APPROVED
                    </span>
                  ) : (
                    <span className="badge badge-info" style={{ fontSize: '10px' }}>
                      REV {u.revision_number || 1}
                    </span>
                  )}
                </div>

                <div className="code-token" style={{ color: 'var(--text-secondary)', fontSize: '10px', marginBottom: '4px' }}>
                  {u.prototype_vuid}
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-muted)' }}>
                  <span>Z: [{u.z_min.toFixed(2)}m → {u.z_max.toFixed(2)}m]</span>
                  <span>{u.volume_cbm.toFixed(0)} m³</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
