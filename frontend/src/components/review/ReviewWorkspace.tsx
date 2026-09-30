import React, { useState } from 'react';
import { CheckCircle, AlertTriangle, ShieldCheck, XCircle, FileCheck, ThumbsUp, ThumbsDown, Edit3 } from 'lucide-react';
import { SpatialUnit, ValidationSummary } from '../../types';

interface ReviewWorkspaceProps {
  unit: SpatialUnit | null;
  validationSummary: ValidationSummary | null;
  onAcceptReview: (revisionId: string, reason: string) => void;
  onRequestCorrection: (unit: SpatialUnit) => void;
  onRejectReview: (revisionId: string, reason: string) => void;
  onApproveRevision: (revisionId: string, reason: string) => void;
  hasActiveReviewDecision: boolean;
  reviewDecisionType?: string | null;
  isApproved: boolean;
  isLoading: boolean;
}

export const ReviewWorkspace: React.FC<ReviewWorkspaceProps> = ({
  unit,
  validationSummary,
  onAcceptReview,
  onRequestCorrection,
  onRejectReview,
  onApproveRevision,
  hasActiveReviewDecision,
  reviewDecisionType,
  isApproved,
  isLoading,
}) => {
  const [reviewReason, setReviewReason] = useState('Reviewed against architectural plan. Elevations verified.');
  const [approvalReason, setApprovalReason] = useState('Candidate satisfies all Gate A, B, and C requirements. Approved as Prototype 3D Spatial Unit.');

  if (!unit || !unit.active_revision_id) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-muted)' }}>
        Select a spatial unit to inspect its human review status and approval eligibility.
      </div>
    );
  }

  const blockerCount = validationSummary?.blocker_count ?? 0;
  const noBlockers = blockerCount === 0;
  const reviewAccepted = reviewDecisionType === 'ACCEPT';
  const isGateCEligible = noBlockers && reviewAccepted && !isApproved;

  return (
    <div style={{ padding: '16px', overflowY: 'auto', height: '100%' }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        {/* Left Column: Human Review Actions */}
        <div>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontWeight: 600, fontSize: '13px', color: 'var(--text-main)' }}>
              Step 1: Human Review Decision
            </span>
            <span className="badge badge-prototype">SIM-OFFICER-001</span>
          </div>

          <div className="card" style={{ padding: '14px', marginBottom: '12px' }}>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '8px' }}>
              Unit: <strong>Level {unit.level_code}</strong> | Revision: <strong>{unit.revision_number || 1}</strong>
            </div>

            <div style={{ marginBottom: '10px' }}>
              <label style={{ fontSize: '11px', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>
                Review Justification / Comment:
              </label>
              <textarea
                value={reviewReason}
                onChange={(e) => setReviewReason(e.target.value)}
                rows={2}
                disabled={isApproved || isLoading}
                style={{
                  width: '100%',
                  backgroundColor: 'var(--bg-app)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '4px',
                  color: 'var(--text-main)',
                  padding: '6px 8px',
                  fontSize: '11px',
                  fontFamily: 'inherit',
                  resize: 'none',
                }}
              />
            </div>

            {/* Decision Buttons */}
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                className={`btn btn-sm ${reviewAccepted ? 'btn-success' : 'btn-primary'}`}
                style={{ flex: 1 }}
                onClick={() => onAcceptReview(unit.active_revision_id!, reviewReason)}
                disabled={!noBlockers || isApproved || isLoading}
                title={!noBlockers ? 'Cannot accept while BLOCKER issues exist' : 'Accept candidate for approval'}
              >
                <ThumbsUp size={13} />
                Accept
              </button>

              <button
                className="btn btn-sm btn-warning"
                style={{ flex: 1 }}
                onClick={() => onRequestCorrection(unit)}
                disabled={isApproved || isLoading}
                title="Open correction dialog to spawn a new non-destructive revision"
              >
                <Edit3 size={13} />
                Request Correction
              </button>

              <button
                className="btn btn-sm btn-danger"
                style={{ flex: 1 }}
                onClick={() => onRejectReview(unit.active_revision_id!, reviewReason)}
                disabled={isApproved || isLoading}
              >
                <ThumbsDown size={13} />
                Reject
              </button>
            </div>

            {reviewDecisionType && (
              <div style={{ marginTop: '10px', fontSize: '11px', color: 'var(--text-secondary)' }}>
                Recorded Review Decision: <span className="badge badge-info">{reviewDecisionType}</span>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Gate C Adjudication */}
        <div>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontWeight: 600, fontSize: '13px', color: 'var(--text-main)' }}>
              Step 2: Gate C Approval Preconditions
            </span>
            <span className={`badge ${isApproved ? 'badge-success' : isGateCEligible ? 'badge-info' : 'badge-blocker'}`}>
              {isApproved ? 'APPROVED' : isGateCEligible ? 'GATE C PASSED' : 'APPROVAL BLOCKED'}
            </span>
          </div>

          <div className="card" style={{ padding: '14px' }}>
            {/* Checklist */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '14px', fontSize: '11px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircle size={14} style={{ color: 'var(--color-success)' }} />
                <span>1. Required provenance & evidence integrity verified</span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                {noBlockers ? (
                  <CheckCircle size={14} style={{ color: 'var(--color-success)' }} />
                ) : (
                  <XCircle size={14} style={{ color: 'var(--color-blocker)' }} />
                )}
                <span style={{ color: noBlockers ? 'inherit' : 'var(--color-blocker)' }}>
                  2. Latest validation run has 0 BLOCKERS ({blockerCount} found)
                </span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                {hasActiveReviewDecision ? (
                  <CheckCircle size={14} style={{ color: 'var(--color-success)' }} />
                ) : (
                  <XCircle size={14} style={{ color: 'var(--color-warning)' }} />
                )}
                <span>3. Human review decision recorded</span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                {reviewAccepted ? (
                  <CheckCircle size={14} style={{ color: 'var(--color-success)' }} />
                ) : (
                  <XCircle size={14} style={{ color: 'var(--color-warning)' }} />
                )}
                <span style={{ color: reviewAccepted ? 'inherit' : 'var(--color-warning)' }}>
                  4. Review decision = ACCEPT
                </span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircle size={14} style={{ color: 'var(--color-success)' }} />
                <span>5. Actor authorization mode = SIMULATED_PROTOTYPE</span>
              </div>
            </div>

            {/* Approval Button */}
            {isApproved ? (
              <div
                style={{
                  backgroundColor: 'var(--color-success-bg)',
                  border: '1px solid var(--color-success-border)',
                  color: 'var(--color-success)',
                  padding: '10px 14px',
                  borderRadius: '6px',
                  textAlign: 'center',
                  fontWeight: 600,
                  fontSize: '12px',
                }}
              >
                PROTOTYPE WORKFLOW APPROVED (IMMUTABLE)
              </div>
            ) : (
              <div>
                <button
                  className="btn btn-success"
                  style={{ width: '100%', padding: '8px' }}
                  onClick={() => onApproveRevision(unit.active_revision_id!, approvalReason)}
                  disabled={!isGateCEligible || isLoading}
                >
                  <FileCheck size={14} />
                  Approve (Prototype Workflow)
                </button>
                {!isGateCEligible && (
                  <div style={{ fontSize: '10px', color: 'var(--color-blocker)', marginTop: '6px', textAlign: 'center' }}>
                    * Approval strictly prohibited until all Gate C conditions pass.
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
