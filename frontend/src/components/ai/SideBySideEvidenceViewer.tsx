import React from 'react';
import { AICandidate, EvidenceSource, ValidationSummary } from '../../types';
import { FileText, Layers, CheckCircle2, AlertTriangle, Eye, Hash, ShieldAlert } from 'lucide-react';

interface SideBySideEvidenceViewerProps {
  candidate: AICandidate | null;
  evidenceList: EvidenceSource[];
  validationSummary: ValidationSummary | null;
  onExplainCandidate?: (candidateId: string) => void;
  onOpenReproducibility?: (candidateId: string) => void;
}

export const SideBySideEvidenceViewer: React.FC<SideBySideEvidenceViewerProps> = ({
  candidate,
  evidenceList,
  validationSummary,
  onExplainCandidate,
  onOpenReproducibility,
}) => {
  if (!candidate) {
    return (
      <div style={{ padding: '32px', textAlign: 'center', color: 'var(--text-muted)' }}>
        Select a candidate spatial unit above to view side-by-side evidence linkage.
      </div>
    );
  }

  const linkedEvidence = evidenceList.filter((e) =>
    candidate.source_evidence_ids?.includes(e.id)
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      {/* Header Banner */}
      <div
        style={{
          padding: '10px 16px',
          borderBottom: '1px solid var(--border-subtle)',
          backgroundColor: 'rgba(15, 23, 42, 0.7)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Layers size={16} className="text-cyan-400" />
          <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)' }}>
            Side-by-Side Lineage Triad: Evidence ↔ Observation ↔ Validation
          </span>
          <span className="badge badge-info" style={{ fontSize: '0.7rem' }}>
            Level: {candidate.level_code}
          </span>
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          {onExplainCandidate && (
            <button
              className="btn btn-sm"
              style={{ fontSize: '0.72rem', padding: '3px 8px' }}
              onClick={() => onExplainCandidate(candidate.candidate_id)}
            >
              <Eye size={12} />
              Explain
            </button>
          )}
          {onOpenReproducibility && (
            <button
              className="btn btn-sm btn-primary"
              style={{ fontSize: '0.72rem', padding: '3px 8px' }}
              onClick={() => onOpenReproducibility(candidate.candidate_id)}
            >
              <Hash size={12} />
              Reproducibility Snapshot
            </button>
          )}
        </div>
      </div>

      {/* 3-Column Triad Body */}
      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1px', backgroundColor: 'var(--border-subtle)', overflow: 'hidden' }}>
        {/* Column 1: Source Evidence & Observations */}
        <div style={{ backgroundColor: 'var(--bg-main)', padding: '12px 14px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
            <FileText size={14} className="text-amber-400" />
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)' }}>
              1. INPUT EVIDENCE ({linkedEvidence.length})
            </span>
          </div>

          {linkedEvidence.length > 0 ? (
            linkedEvidence.map((ev) => (
              <div
                key={ev.id}
                style={{
                  backgroundColor: 'rgba(30, 41, 59, 0.5)',
                  padding: '10px',
                  borderRadius: '6px',
                  border: '1px solid var(--border-subtle)',
                  fontSize: '0.75rem',
                  lineHeight: 1.4,
                }}
              >
                <div style={{ fontWeight: 600, color: 'var(--text-main)' }}>{ev.id}</div>
                <div style={{ color: 'var(--text-muted)' }}>{ev.source_reference}</div>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>Type: {ev.evidence_type}</div>
                <div style={{ fontFamily: 'monospace', fontSize: '0.68rem', color: '#38bdf8', marginTop: '4px' }}>
                  SHA-256: {ev.checksum.slice(0, 20)}...
                </div>
              </div>
            ))
          ) : (
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Evidence IDs: {candidate.source_evidence_ids?.join(', ') || 'None linked'}
            </div>
          )}
        </div>

        {/* Column 2: Candidate 3D Geometry & Confidence */}
        <div style={{ backgroundColor: 'var(--bg-main)', padding: '12px 14px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
            <Layers size={14} className="text-cyan-400" />
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)' }}>
              2. PROPOSED SPATIAL CANDIDATE
            </span>
          </div>

          <div
            style={{
              backgroundColor: 'rgba(30, 41, 59, 0.5)',
              padding: '10px',
              borderRadius: '6px',
              border: '1px solid var(--border-subtle)',
              fontSize: '0.75rem',
              lineHeight: 1.5,
            }}
          >
            <div><strong>Candidate ID:</strong> <span style={{ fontFamily: 'monospace' }}>{candidate.candidate_id}</span></div>
            <div><strong>Status:</strong> <span className="badge badge-neutral" style={{ fontSize: '0.7rem' }}>{candidate.status}</span></div>
            <div><strong>Confidence:</strong> <span className={`badge ${candidate.confidence_band === 'HIGH' ? 'badge-success' : 'badge-warning'}`} style={{ fontSize: '0.7rem' }}>{candidate.confidence.toFixed(2)} ({candidate.confidence_band})</span></div>
            <div><strong>Vertical Extent:</strong> {candidate.z_min.toFixed(2)}m → {candidate.z_max.toFixed(2)}m (Δ {(candidate.z_max - candidate.z_min).toFixed(2)}m)</div>
            <div><strong>Footprint Area:</strong> {candidate.footprint_area_sqm.toFixed(1)} m²</div>
            <div><strong>Extruded Volume:</strong> {candidate.volume_cbm.toFixed(1)} m³</div>
            <div style={{ marginTop: '4px' }}>
              <span style={{ color: 'var(--text-muted)' }}>Reason Codes:</span>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginTop: '2px' }}>
                {candidate.reason_codes.map((rc) => (
                  <span key={rc} className="badge badge-neutral" style={{ fontSize: '0.65rem' }}>{rc}</span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Column 3: Deterministic Validation & Governance Outcome */}
        <div style={{ backgroundColor: 'var(--bg-main)', padding: '12px 14px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
            <ShieldAlert size={14} className="text-red-400" />
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)' }}>
              3. DETERMINISTIC VALIDATION & GOVERNANCE
            </span>
          </div>

          <div
            style={{
              backgroundColor: validationSummary && validationSummary.blocker_count > 0 ? 'rgba(239, 68, 68, 0.08)' : 'rgba(16, 185, 129, 0.08)',
              padding: '10px',
              borderRadius: '6px',
              border: `1px solid ${validationSummary && validationSummary.blocker_count > 0 ? 'rgba(239, 68, 68, 0.3)' : 'rgba(16, 185, 129, 0.3)'}`,
              fontSize: '0.75rem',
              lineHeight: 1.5,
            }}
          >
            <div><strong>Ruleset:</strong> Gate A/B v1.0.0</div>
            <div>
              <strong>Validation Outcome:</strong>{' '}
              {validationSummary && validationSummary.blocker_count > 0 ? (
                <span className="badge badge-error" style={{ fontSize: '0.7rem' }}>
                  BLOCKER ({validationSummary.blocker_count} detected)
                </span>
              ) : (
                <span className="badge badge-success" style={{ fontSize: '0.7rem' }}>
                  ALL PASS (0 Blockers)
                </span>
              )}
            </div>
            <div>
              <strong>Gate C Eligibility:</strong>{' '}
              {validationSummary?.can_approve ? (
                <span style={{ color: '#34d399', fontWeight: 600 }}>ELIGIBLE</span>
              ) : (
                <span style={{ color: '#f87171', fontWeight: 600 }}>APPROVAL BLOCKED</span>
              )}
            </div>
            <div style={{ marginTop: '6px', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
              <strong>Principle:</strong> AI proposals are strictly non-authoritative. Only clean deterministic validation allows human officer Gate C acceptance.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
