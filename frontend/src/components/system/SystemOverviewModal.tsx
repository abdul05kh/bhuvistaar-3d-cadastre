import React from 'react';
import { X, Layers, Shield, Cpu, CheckSquare, Eye, ArrowRight, Activity, Database, AlertTriangle } from 'lucide-react';
import { ParentParcel, SpatialUnit, ValidationSummary } from '../../types';

interface SystemOverviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  parcel: ParentParcel | null;
  units: SpatialUnit[];
  validationSummary: ValidationSummary | null;
  onStartGoldenDemo: () => void;
}

export const SystemOverviewModal: React.FC<SystemOverviewModalProps> = ({
  isOpen,
  onClose,
  parcel,
  units,
  validationSummary,
  onStartGoldenDemo,
}) => {
  if (!isOpen) return null;

  const blockerCount = validationSummary?.blocker_count ?? 0;
  const unitCount = units.length;
  const isBlocked = blockerCount > 0;

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      backgroundColor: 'rgba(5, 10, 20, 0.85)',
      backdropFilter: 'blur(6px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 100,
      padding: '20px'
    }}>
      <div style={{
        backgroundColor: '#0c1729',
        border: '1px solid #1e3a5f',
        borderRadius: '12px',
        width: '840px',
        maxWidth: '95vw',
        maxHeight: '90vh',
        display: 'flex',
        flexDirection: 'column',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.7)'
      }}>
        {/* Header */}
        <div style={{
          padding: '16px 24px',
          borderBottom: '1px solid #1e3a5f',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          backgroundColor: '#08101e'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Activity size={20} className="text-cyan-400" />
            <div>
              <h2 style={{ fontSize: '16px', fontWeight: 700, color: '#f8fafc', margin: 0 }}>
                BhuVistaar — 30-Second Executive Overview
              </h2>
              <p style={{ fontSize: '11px', color: '#94a3b8', margin: 0 }}>
                Machine-assisted 3D Cadastral Intelligence & Deterministic Validation Platform
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer', padding: '4px' }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Content Body */}
        <div style={{ padding: '24px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Core Trust Chain Cards */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(5, 1fr)',
            gap: '10px',
            textAlign: 'center'
          }}>
            <div style={{ backgroundColor: '#111f38', border: '1px solid #1e3a5f', borderRadius: '8px', padding: '12px 6px' }}>
              <div style={{ fontSize: '10px', fontWeight: 700, color: '#38bdf8', textTransform: 'uppercase' }}>1. INPUT</div>
              <div style={{ fontSize: '12px', fontWeight: 600, color: '#f8fafc', marginTop: '4px' }}>Parcel + Evidence</div>
              <div style={{ fontSize: '10px', color: '#94a3b8', marginTop: '2px' }}>ULPIN root & survey data</div>
            </div>
            <div style={{ backgroundColor: '#111f38', border: '1px solid #1e3a5f', borderRadius: '8px', padding: '12px 6px' }}>
              <div style={{ fontSize: '10px', fontWeight: 700, color: '#a855f7', textTransform: 'uppercase' }}>2. MACHINE ASSIST</div>
              <div style={{ fontSize: '12px', fontWeight: 600, color: '#f8fafc', marginTop: '4px' }}>3D Candidates</div>
              <div style={{ fontSize: '10px', color: '#94a3b8', marginTop: '2px' }}>Non-authoritative proposal</div>
            </div>
            <div style={{ backgroundColor: '#111f38', border: '1px solid #1e3a5f', borderRadius: '8px', padding: '12px 6px' }}>
              <div style={{ fontSize: '10px', fontWeight: 700, color: '#f59e0b', textTransform: 'uppercase' }}>3. VALIDATION</div>
              <div style={{ fontSize: '12px', fontWeight: 600, color: '#f8fafc', marginTop: '4px' }}>Gate A & Gate B</div>
              <div style={{ fontSize: '10px', color: '#94a3b8', marginTop: '2px' }}>VRT-003 overlap blocker</div>
            </div>
            <div style={{ backgroundColor: '#111f38', border: '1px solid #1e3a5f', borderRadius: '8px', padding: '12px 6px' }}>
              <div style={{ fontSize: '10px', fontWeight: 700, color: '#10b981', textTransform: 'uppercase' }}>4. GOVERNANCE</div>
              <div style={{ fontSize: '12px', fontWeight: 600, color: '#f8fafc', marginTop: '4px' }}>Human Review</div>
              <div style={{ fontSize: '10px', color: '#94a3b8', marginTop: '2px' }}>Correction $\to$ Revision 2</div>
            </div>
            <div style={{ backgroundColor: '#111f38', border: '1px solid #1e3a5f', borderRadius: '8px', padding: '12px 6px' }}>
              <div style={{ fontSize: '10px', fontWeight: 700, color: '#6366f1', textTransform: 'uppercase' }}>5. OUTPUT</div>
              <div style={{ fontSize: '12px', fontWeight: 600, color: '#f8fafc', marginTop: '4px' }}>Audited Export</div>
              <div style={{ fontSize: '10px', color: '#94a3b8', marginTop: '2px' }}>JSON, GeoJSON, 3D OBJ</div>
            </div>
          </div>

          {/* Current Property Snapshot */}
          <div style={{
            backgroundColor: '#0a1322',
            border: '1px solid #1e293b',
            borderRadius: '8px',
            padding: '16px'
          }}>
            <h3 style={{ fontSize: '13px', fontWeight: 700, color: '#e2e8f0', margin: '0 0 12px 0', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Current Parcel Snapshot
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '14px' }}>
              <div>
                <span style={{ fontSize: '10px', color: '#94a3b8', display: 'block' }}>Parent 2D ULPIN</span>
                <span style={{ fontSize: '13px', fontWeight: 700, color: '#38bdf8', fontFamily: 'monospace' }}>
                  {parcel?.ulpin ?? '12345678901234'}
                </span>
              </div>
              <div>
                <span style={{ fontSize: '10px', color: '#94a3b8', display: 'block' }}>3D Spatial Units</span>
                <span style={{ fontSize: '13px', fontWeight: 700, color: '#f8fafc' }}>
                  {unitCount} Units Active
                </span>
              </div>
              <div>
                <span style={{ fontSize: '10px', color: '#94a3b8', display: 'block' }}>Deterministic Blocker State</span>
                <span style={{
                  fontSize: '12px',
                  fontWeight: 700,
                  color: isBlocked ? '#f87171' : '#4ade80'
                }}>
                  {isBlocked ? `${blockerCount} BLOCKER (VRT-003)` : '0 BLOCKERS (CLEAN)'}
                </span>
              </div>
              <div>
                <span style={{ fontSize: '10px', color: '#94a3b8', display: 'block' }}>Persistence Layer</span>
                <span style={{ fontSize: '12px', fontWeight: 600, color: '#94a3b8' }}>
                  PostGIS 16 (SRID 32643)
                </span>
              </div>
            </div>
          </div>

          {/* Core Differentiator Callout */}
          <div style={{
            backgroundColor: 'rgba(56, 189, 248, 0.05)',
            borderLeft: '4px solid #38bdf8',
            padding: '12px 16px',
            borderRadius: '0 6px 6px 0'
          }}>
            <h4 style={{ margin: '0 0 4px 0', fontSize: '12px', fontWeight: 700, color: '#38bdf8' }}>
              The Core Architectural Differentiator: Governed Trust Chain
            </h4>
            <p style={{ margin: 0, fontSize: '11px', lineHeight: 1.5, color: '#cbd5e1' }}>
              Unlike black-box generative systems, BhuVistaar never allows AI output to directly become official cadastral record. 
              Every proposal is subject to deterministic mathematical validation (Gate A/B), logged in an append-only audit trail, and requires explicit human officer review before Gate C approval is permitted.
            </p>
          </div>
        </div>

        {/* Footer Actions */}
        <div style={{
          padding: '16px 24px',
          borderTop: '1px solid #1e3a5f',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          backgroundColor: '#08101e'
        }}>
          <span style={{ fontSize: '11px', color: '#64748b' }}>
            Prototype VUID — not an official 3D ULPIN. Controlled synthetic evaluation.
          </span>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button className="btn btn-sm" onClick={onClose}>
              Close
            </button>
            <button
              className="btn btn-sm btn-primary"
              onClick={() => {
                onClose();
                onStartGoldenDemo();
              }}
            >
              Start Golden Walkthrough <ArrowRight size={14} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
