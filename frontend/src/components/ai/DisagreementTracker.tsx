import React from 'react';
import { DisagreementRecord } from '../../types';
import { ShieldAlert, AlertTriangle, CheckCircle, UserX, Eye, ArrowRight } from 'lucide-react';

interface DisagreementTrackerProps {
  disagreements: DisagreementRecord[];
  onSelectCandidate?: (candidateId: string) => void;
  onExplainCandidate?: (candidateId: string) => void;
}

export const DisagreementTracker: React.FC<DisagreementTrackerProps> = ({
  disagreements,
  onSelectCandidate,
  onExplainCandidate,
}) => {
  const blockerCount = disagreements.filter((d) => d.severity === 'BLOCKER').length;
  const warningCount = disagreements.filter((d) => d.severity === 'WARNING').length;
  const consistentCount = disagreements.filter((d) => d.disagreement_type === 'CONSISTENT').length;

  const getTypeIcon = (type: string, severity: string) => {
    switch (type) {
      case 'AI_VALIDATION_DISAGREEMENT':
        return <ShieldAlert className="text-red-400" size={18} />;
      case 'HUMAN_OVERRIDE_OF_AI_PROPOSAL':
        return <UserX className="text-amber-400" size={18} />;
      case 'LOW_AI_CONFIDENCE_GEOMETRICALLY_VALID':
        return <AlertTriangle className="text-yellow-400" size={18} />;
      case 'CONSISTENT':
        return <CheckCircle className="text-emerald-400" size={18} />;
      default:
        return severity === 'BLOCKER' ? <ShieldAlert className="text-red-400" size={18} /> : <AlertTriangle className="text-amber-400" size={18} />;
    }
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'AI_VALIDATION_DISAGREEMENT':
        return 'CASE A: AI / Validation Disagreement';
      case 'HUMAN_OVERRIDE_OF_AI_PROPOSAL':
        return 'CASE D: Human Override of Proposal';
      case 'LOW_AI_CONFIDENCE_GEOMETRICALLY_VALID':
        return 'CASE B: Low AI Confidence / Geometrically Valid';
      case 'CONSISTENT':
        return 'CASE C: Consistent & Valid';
      default:
        return type.replace(/_/g, ' ');
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      {/* Header & Metrics Strip */}
      <div
        style={{
          padding: '12px 16px',
          borderBottom: '1px solid var(--border-subtle)',
          backgroundColor: 'rgba(15, 23, 42, 0.6)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '12px',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ShieldAlert size={16} className="text-red-400" />
            <h4 style={{ margin: 0, fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-main)' }}>
              AI vs Validation Disagreement Tracker (Slice 4)
            </h4>
          </div>
          <p style={{ margin: '2px 0 0 0', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Explicitly monitors tensions between AI model confidence, deterministic spatial rules, and human review decisions.
          </p>
        </div>

        {/* Counter Badges */}
        <div style={{ display: 'flex', gap: '8px' }}>
          <span className="badge badge-error" style={{ fontSize: '0.75rem', padding: '4px 8px' }}>
            {blockerCount} Blocker Disagreements
          </span>
          <span className="badge badge-warning" style={{ fontSize: '0.75rem', padding: '4px 8px' }}>
            {warningCount} Warnings / Overrides
          </span>
          <span className="badge badge-success" style={{ fontSize: '0.75rem', padding: '4px 8px' }}>
            {consistentCount} Consistent
          </span>
        </div>
      </div>

      {/* Disagreements List */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '12px 16px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {disagreements.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '32px 16px', color: 'var(--text-muted)' }}>
            <CheckCircle size={32} className="text-emerald-400" style={{ margin: '0 auto 8px auto', opacity: 0.8 }} />
            <p style={{ fontSize: '0.85rem', margin: 0 }}>No active disagreements detected.</p>
            <p style={{ fontSize: '0.75rem', margin: '4px 0 0 0' }}>AI proposals and deterministic validation rules are in complete alignment.</p>
          </div>
        ) : (
          disagreements.map((d) => (
            <div
              key={d.disagreement_id}
              style={{
                backgroundColor: d.severity === 'BLOCKER' ? 'rgba(239, 68, 68, 0.08)' : 'rgba(30, 41, 59, 0.7)',
                border: `1px solid ${d.severity === 'BLOCKER' ? 'rgba(239, 68, 68, 0.3)' : 'var(--border-subtle)'}`,
                borderRadius: '6px',
                padding: '12px 14px',
                display: 'flex',
                flexDirection: 'column',
                gap: '8px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  {getTypeIcon(d.disagreement_type, d.severity)}
                  <div>
                    <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-main)' }}>
                      {getTypeLabel(d.disagreement_type)}
                    </span>
                    <span style={{ marginLeft: '8px', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      Level: <strong style={{ color: 'var(--text-main)' }}>{d.level_code || 'N/A'}</strong>
                    </span>
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                  <span className={`badge ${d.severity === 'BLOCKER' ? 'badge-error' : d.severity === 'WARNING' ? 'badge-warning' : 'badge-neutral'}`} style={{ fontSize: '0.7rem' }}>
                    {d.severity}
                  </span>
                  <span className="badge badge-info" style={{ fontSize: '0.7rem' }}>
                    AI Conf: {d.ai_confidence.toFixed(2)}
                  </span>
                  <span className={`badge ${d.validation_status === 'BLOCKER' ? 'badge-error' : 'badge-success'}`} style={{ fontSize: '0.7rem' }}>
                    Val: {d.validation_status}
                  </span>
                </div>
              </div>

              {/* Explanation text */}
              <p style={{ margin: 0, fontSize: '0.78rem', color: 'var(--text-main)', lineHeight: 1.45 }}>
                {d.explanation}
              </p>

              {/* Violations & Details */}
              {d.rule_codes && d.rule_codes.length > 0 && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap', marginTop: '2px' }}>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Violated Rules:</span>
                  {d.rule_codes.map((rc) => (
                    <span key={rc} className="badge badge-error" style={{ fontSize: '0.7rem', padding: '2px 6px' }}>
                      {rc}
                    </span>
                  ))}
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginLeft: '6px' }}>
                    Ruleset: {d.ruleset_version}
                  </span>
                </div>
              )}

              {/* Actions */}
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px', marginTop: '4px' }}>
                {d.candidate_id && onExplainCandidate && (
                  <button
                    className="btn btn-sm"
                    style={{ fontSize: '0.72rem', padding: '3px 8px' }}
                    onClick={() => onExplainCandidate(d.candidate_id!)}
                  >
                    <Eye size={12} />
                    Explain Why
                  </button>
                )}
                {d.candidate_id && onSelectCandidate && (
                  <button
                    className="btn btn-sm btn-primary"
                    style={{ fontSize: '0.72rem', padding: '3px 8px' }}
                    onClick={() => onSelectCandidate(d.candidate_id!)}
                  >
                    Inspect in 3D
                    <ArrowRight size={12} />
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
