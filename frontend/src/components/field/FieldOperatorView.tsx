import React from 'react';
import { Smartphone, CheckCircle, AlertTriangle, Wifi, WifiOff, FileText, Layers, Send } from 'lucide-react';
import { SpatialUnit, EvidenceSource, ValidationIssue } from '../../types';

interface FieldOperatorViewProps {
  ulpin: string;
  units: SpatialUnit[];
  evidence: EvidenceSource[];
  issues: ValidationIssue[];
  isOnline: boolean;
  onSelectUnit: (unit: SpatialUnit) => void;
  onRequestCorrection: () => void;
}


export const FieldOperatorView: React.FC<FieldOperatorViewProps> = ({
  ulpin,
  units,
  evidence,
  issues,
  isOnline,
  onSelectUnit,
  onRequestCorrection
}) => {
  const blockers = issues.filter(i => i.severity === 'BLOCKER');

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: '14px',
      padding: '16px',
      backgroundColor: '#090d16',
      height: '100%',
      overflowY: 'auto'
    }}>
      {/* Banner */}
      <div style={{
        padding: '12px 16px',
        backgroundColor: '#1e293b',
        border: '1px solid #334155',
        borderRadius: '8px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Smartphone size={20} style={{ color: '#38bdf8' }} />
          <div>
            <div style={{ fontSize: '14px', fontWeight: 700, color: '#f8fafc' }}>
              Field Surveyor Mobile Console
            </div>
            <div style={{ fontSize: '11px', color: '#94a3b8' }}>
              Simplified On-Site 3D Cadastral Inspection Mode
            </div>
          </div>
        </div>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          padding: '4px 10px',
          borderRadius: '5px',
          backgroundColor: isOnline ? 'rgba(34, 197, 94, 0.15)' : 'rgba(239, 68, 68, 0.15)',
          color: isOnline ? '#4ade80' : '#f87171',
          fontSize: '11px',
          fontWeight: 600
        }}>
          {isOnline ? <Wifi size={14} /> : <WifiOff size={14} />}
          <span>{isOnline ? 'SERVER SYNCED' : 'OFFLINE / CACHED'}</span>
        </div>
      </div>

      {/* Parcel Card */}
      <div style={{
        padding: '14px',
        backgroundColor: '#111827',
        border: '1px solid #1f2937',
        borderRadius: '8px'
      }}>
        <div style={{ fontSize: '11px', textTransform: 'uppercase', color: '#9ca3af', fontWeight: 600 }}>
          Assigned Cadastral Parcel
        </div>
        <div style={{ fontSize: '18px', fontWeight: 700, color: '#f9fafb', fontFamily: 'monospace', marginTop: '2px' }}>
          {ulpin}
        </div>
        <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>
          CRS: EPSG:32643 (UTM 43N) • Projected Coordinate System
        </div>
      </div>

      {/* Field Inspection Summary Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
        <div style={{ padding: '10px', backgroundColor: '#1e293b', borderRadius: '6px', border: '1px solid #334155' }}>
          <div style={{ fontSize: '10px', color: '#94a3b8', textTransform: 'uppercase' }}>Registered Evidence</div>
          <div style={{ fontSize: '16px', fontWeight: 700, color: '#38bdf8' }}>{evidence.length} Sources</div>
        </div>
        <div style={{ padding: '10px', backgroundColor: '#1e293b', borderRadius: '6px', border: '1px solid #334155' }}>
          <div style={{ fontSize: '10px', color: '#94a3b8', textTransform: 'uppercase' }}>3D Floor Units</div>
          <div style={{ fontSize: '16px', fontWeight: 700, color: '#38bdf8' }}>{units.length} Levels</div>
        </div>
        <div style={{ padding: '10px', backgroundColor: '#1e293b', borderRadius: '6px', border: '1px solid #334155' }}>
          <div style={{ fontSize: '10px', color: '#94a3b8', textTransform: 'uppercase' }}>Field Issues</div>
          <div style={{ fontSize: '16px', fontWeight: 700, color: blockers.length > 0 ? '#f87171' : '#4ade80' }}>
            {blockers.length} Blockers
          </div>
        </div>
      </div>

      {/* Floor Units Quick-Inspector */}
      <div style={{
        padding: '14px',
        backgroundColor: '#111827',
        border: '1px solid #1f2937',
        borderRadius: '8px'
      }}>
        <div style={{ fontSize: '12px', fontWeight: 700, color: '#f3f4f6', marginBottom: '8px' }}>
          Floor Elevation Inspection
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          {units.map((u) => {
            const hasIssue = blockers.some(b => b.object_id === u.prototype_vuid);
            return (
              <div
                key={u.id}
                onClick={() => onSelectUnit(u)}
                style={{
                  padding: '8px 12px',
                  backgroundColor: '#1f2937',
                  borderRadius: '5px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  cursor: 'pointer',
                  borderLeft: `3px solid ${hasIssue ? '#ef4444' : '#22c55e'}`
                }}
              >
                <div>
                  <span style={{ fontWeight: 700, color: '#f9fafb', fontSize: '12px' }}>{u.level_code}</span>
                  <span style={{ fontSize: '11px', color: '#9ca3af', marginLeft: '8px' }}>
                    {u.z_min.toFixed(2)}m to {u.z_max.toFixed(2)}m (H: {(u.z_max - u.z_min).toFixed(2)}m)
                  </span>
                </div>
                <span style={{
                  fontSize: '10px',
                  fontWeight: 700,
                  padding: '2px 6px',
                  borderRadius: '4px',
                  backgroundColor: hasIssue ? 'rgba(239, 68, 68, 0.2)' : 'rgba(34, 197, 94, 0.2)',
                  color: hasIssue ? '#f87171' : '#4ade80'
                }}>
                  {hasIssue ? 'OVERLAP BLOCKER' : 'VALID'}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', gap: '10px', marginTop: 'auto' }}>
        <button
          className="btn btn-warning"
          style={{ flex: 1, padding: '10px' }}
          onClick={onRequestCorrection}
        >
          <AlertTriangle size={14} />
          Flag Measurement Discrepancy
        </button>
      </div>
    </div>
  );
};
