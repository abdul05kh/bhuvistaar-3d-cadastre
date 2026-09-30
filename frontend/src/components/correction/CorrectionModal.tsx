import React, { useState } from 'react';
import { X, Edit3, ArrowRight, ShieldAlert, Sparkles } from 'lucide-react';
import { SpatialUnit } from '../../types';

interface CorrectionModalProps {
  unit: SpatialUnit;
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (revisionId: string, z_min: number, z_max: number, reason: string) => Promise<void>;
  isLoading: boolean;
}

export const CorrectionModal: React.FC<CorrectionModalProps> = ({
  unit,
  isOpen,
  onClose,
  onSubmit,
  isLoading,
}) => {
  if (!isOpen) return null;

  const [zMin, setZMin] = useState<number>(unit.z_min);
  const [zMax, setZMax] = useState<number>(unit.z_max === 106.5 ? 106.0 : unit.z_max);
  const [reason, setReason] = useState<string>(
    'Adjusted ceiling elevation from 106.50m down to 106.00m to eliminate 0.50m vertical collision with Level L02 per architectural survey evidence.'
  );
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!unit.active_revision_id) {
      setError('Active revision ID missing on unit.');
      return;
    }
    if (zMax <= zMin) {
      setError('Z Max must be strictly greater than Z Min.');
      return;
    }
    if (!reason.trim()) {
      setError('A detailed correction reason is required for cadastral auditability.');
      return;
    }

    try {
      setError(null);
      await onSubmit(unit.active_revision_id, zMin, zMax, reason);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to apply correction.');
    }
  };

  const handleApplyRecommended = () => {
    setZMin(103.0);
    setZMax(106.0);
    setReason('Corrected vertical overlap: adjusted L01 ceiling from 106.50m down to 106.00m to eliminate 0.50m collision with L02.');
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Edit3 size={16} style={{ color: 'var(--color-warning)' }} />
            <span style={{ fontWeight: 600, fontSize: '13px', color: 'var(--text-main)' }}>
              Non-Destructive Spatial Correction
            </span>
            <span className="badge badge-info">Level {unit.level_code}</span>
          </div>
          <button className="btn btn-sm" onClick={onClose} style={{ padding: '4px' }}>
            <X size={14} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body" style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {/* Non-destructive guarantee notice */}
            <div
              style={{
                backgroundColor: 'rgba(59, 130, 246, 0.08)',
                border: '1px solid rgba(59, 130, 246, 0.25)',
                borderRadius: '6px',
                padding: '10px 12px',
                fontSize: '11px',
                color: 'var(--text-secondary)',
              }}
            >
              <strong style={{ color: 'var(--color-primary)' }}>Cadastral Audit Guarantee:</strong> Historical Revision {unit.revision_number || 1} will remain immutable. This operation will spawn a <strong>new Revision {((unit.revision_number || 1) + 1)}</strong> with predecessor pointers and recompute a new deterministic Prototype VUID.
            </div>

            {/* Recommended Fix Chip for L01 */}
            {unit.level_code === 'L01' && unit.z_max === 106.5 && (
              <div
                style={{
                  backgroundColor: 'rgba(245, 158, 11, 0.12)',
                  border: '1px dashed var(--color-warning)',
                  borderRadius: '6px',
                  padding: '8px 12px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                }}
              >
                <div style={{ fontSize: '11px', color: '#fbbf24' }}>
                  <Sparkles size={12} style={{ display: 'inline', marginRight: '4px' }} />
                  Recommended fix: Adjust ceiling to <strong>106.000m</strong> (resolves VRT-003 overlap with L02).
                </div>
                <button
                  type="button"
                  className="btn btn-sm btn-warning"
                  onClick={handleApplyRecommended}
                >
                  Apply 106.00m
                </button>
              </div>
            )}

            {/* Elevation Fields */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <div>
                <label style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>
                  Lower Elevation (Z Min in metres):
                </label>
                <input
                  type="number"
                  step="0.001"
                  value={zMin}
                  onChange={(e) => setZMin(parseFloat(e.target.value))}
                  disabled={isLoading}
                  style={{
                    width: '100%',
                    backgroundColor: 'var(--bg-card)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: '4px',
                    color: 'var(--text-main)',
                    padding: '8px 10px',
                    fontSize: '13px',
                    fontFamily: 'var(--font-mono)',
                  }}
                />
              </div>

              <div>
                <label style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>
                  Upper Elevation (Z Max in metres):
                </label>
                <input
                  type="number"
                  step="0.001"
                  value={zMax}
                  onChange={(e) => setZMax(parseFloat(e.target.value))}
                  disabled={isLoading}
                  style={{
                    width: '100%',
                    backgroundColor: 'var(--bg-card)',
                    border: '1px solid var(--color-primary)',
                    borderRadius: '4px',
                    color: 'var(--text-main)',
                    padding: '8px 10px',
                    fontSize: '13px',
                    fontFamily: 'var(--font-mono)',
                    fontWeight: 600,
                  }}
                />
              </div>
            </div>

            {/* Reason Field */}
            <div>
              <label style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>
                Officer Justification / Reason:
              </label>
              <textarea
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                rows={3}
                disabled={isLoading}
                style={{
                  width: '100%',
                  backgroundColor: 'var(--bg-card)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '4px',
                  color: 'var(--text-main)',
                  padding: '8px 10px',
                  fontSize: '11px',
                  fontFamily: 'inherit',
                  resize: 'none',
                }}
              />
            </div>

            {error && (
              <div style={{ color: 'var(--color-blocker)', fontSize: '11px' }}>
                {error}
              </div>
            )}
          </div>

          <div className="modal-footer">
            <button type="button" className="btn btn-sm" onClick={onClose} disabled={isLoading}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={isLoading}>
              {isLoading ? 'Creating Revision...' : 'Submit Non-Destructive Correction'}
              <ArrowRight size={13} />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
