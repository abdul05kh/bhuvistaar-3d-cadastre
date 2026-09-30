import React from 'react';
import { Shield, AlertCircle, CheckCircle, RotateCcw, PlayCircle } from 'lucide-react';
import { UnitStatus } from '../../types';

interface AppHeaderProps {
  ulpin: string;
  status: UnitStatus | string;
  blockerCount: number;
  onResetDemo: () => void;
  onToggleDemoGuide: () => void;
  isDemoGuideOpen: boolean;
  isLoading: boolean;
}

export const AppHeader: React.FC<AppHeaderProps> = ({
  ulpin,
  status,
  blockerCount,
  onResetDemo,
  onToggleDemoGuide,
  isDemoGuideOpen,
  isLoading,
}) => {
  const isApproved = status === 'APPROVED';
  const isBlocked = blockerCount > 0;

  return (
    <header style={{
      height: '56px',
      backgroundColor: 'var(--bg-panel)',
      borderBottom: '1px solid var(--border-subtle)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 18px',
      zIndex: 20
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        <div style={{
          width: '32px',
          height: '32px',
          borderRadius: '6px',
          backgroundColor: 'var(--color-primary)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#ffffff',
          fontWeight: 700,
          fontSize: '14px',
          letterSpacing: '0.05em'
        }}>
          BV
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontWeight: 700, fontSize: '15px', letterSpacing: '0.02em', color: '#ffffff' }}>
              BHUVISTAAR
            </span>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 500 }}>
              | 3D Cadastral Intelligence & Governance
            </span>
            <span className="badge badge-prototype">
              PROTOTYPE
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '11px', color: 'var(--text-secondary)' }}>
            <span>Authoritative Persistence: PostgreSQL 16 + PostGIS 3.4</span>
            <span>*</span>
            <span>SRID: EPSG:32643 (UTM 43N)</span>
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        {/* Parent Parcel Indicator */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '4px 10px',
          backgroundColor: 'var(--bg-card)',
          borderRadius: '5px',
          border: '1px solid var(--border-subtle)',
        }}>
          <span style={{ color: 'var(--text-muted)', fontSize: '11px' }}>Parent ULPIN:</span>
          <span className="code-token" style={{ color: 'var(--text-main)', fontWeight: 600 }}>
            {ulpin || 'None'}
          </span>
        </div>

        {/* Blocker Counter */}
        {isBlocked ? (
          <span className="badge badge-blocker">
            <AlertCircle size={13} />
            {blockerCount} BLOCKER{blockerCount > 1 ? 'S' : ''}
          </span>
        ) : (
          <span className="badge badge-success">
            <CheckCircle size={13} />
            0 BLOCKERS
          </span>
        )}

        {/* Workflow State Badge */}
        <span className={`badge ${isApproved ? 'badge-success' : isBlocked ? 'badge-blocker' : 'badge-warning'}`}>
          STATE: {status}
        </span>

        {/* Simulated Actor Badge */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '5px',
          padding: '3px 8px',
          borderRadius: '4px',
          backgroundColor: 'rgba(51, 65, 85, 0.4)',
          border: '1px solid rgba(51, 65, 85, 0.6)',
          fontSize: '11px',
          color: 'var(--text-secondary)'
        }} title="Simulated prototype actor context (No fake officer identities)">
          <Shield size={12} style={{ color: 'var(--color-primary)' }} />
          <span>SIMULATED_PROTOTYPE</span>
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            className={`btn btn-sm ${isDemoGuideOpen ? 'btn-primary' : ''}`}
            onClick={onToggleDemoGuide}
            title="Step-by-step SIH Judge Walkthrough"
          >
            <PlayCircle size={13} />
            Judge Guide
          </button>
          <button
            className="btn btn-sm btn-danger"
            onClick={onResetDemo}
            disabled={isLoading}
            title="Reset DB to defect scenario (VRT-003 0.50m overlap)"
          >
            <RotateCcw size={13} className={isLoading ? 'animate-spin' : ''} />
            Reset Demo
          </button>
        </div>
      </div>
    </header>
  );
};
