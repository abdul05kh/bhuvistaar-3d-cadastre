import React from 'react';
import { PlayCircle, CheckCircle, ArrowRight, RotateCcw, AlertTriangle } from 'lucide-react';

interface DemoScenarioBarProps {
  currentStep: number;
  onNextStep: () => void;
  onPrevStep: () => void;
  onResetDemo: () => void;
  onSelectScenario?: (key: string) => void;
  isLoading: boolean;
}

const DEMO_STEPS = [
  {
    step: 1,
    title: 'AI Synthesis & Defect Ingestion',
    desc: 'Parent ULPIN 12345678901234 loaded in UTM 43N with AI proposals. L01 ceiling (106.50m) collides with L02 floor (106.00m).',
    actionText: 'Inspect Floor L01 & Anomaly',
  },
  {
    step: 2,
    title: 'Deterministic VRT-003 Blocker Detected',
    desc: 'Notice L01 ceiling at 106.50m and L02 floor at 106.00m (0.50m collision). AI flagged anomaly; validator emits VRT-003 BLOCKER.',
    actionText: 'Attempt Approval (Gate C)',
  },
  {
    step: 3,
    title: 'Gate C Rejects Premature Approval',
    desc: 'Approval is strictly blocked by the backend because unresolved BLOCKER issues exist. AI uncertainty cannot bypass Gate C.',
    actionText: 'Open Correction Modal',
  },
  {
    step: 4,
    title: 'Apply Non-Destructive Correction',
    desc: 'Adjust Level L01 ceiling from 106.50m down to 106.00m. Revision 1 remains intact in PostgreSQL; Revision 2 is created.',
    actionText: 'Observe Revision 2 & Revalidation',
  },
  {
    step: 5,
    title: 'Revalidation & Lineage Verification',
    desc: 'Revision 2 has 0 blockers. A new deterministic Prototype VUID was generated. Historical Revision 1 is fully recoverable.',
    actionText: 'Record Human Review (ACCEPT)',
  },
  {
    step: 6,
    title: 'Gate C Approval & Trace Origin Export',
    desc: 'With 0 blockers and human ACCEPT review, Gate C permits prototype workflow approval. Lineage graph and export are complete.',
    actionText: 'Inspect Export JSON',
  },
];

export const DemoScenarioBar: React.FC<DemoScenarioBarProps> = ({
  currentStep,
  onNextStep,
  onPrevStep,
  onResetDemo,
  onSelectScenario,
  isLoading,
}) => {
  const stepInfo = DEMO_STEPS[Math.min(currentStep - 1, DEMO_STEPS.length - 1)];

  return (
    <div
      style={{
        backgroundColor: '#0c1a30',
        borderBottom: '1px solid var(--color-primary)',
        padding: '6px 18px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        zIndex: 15,
        gap: '12px'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flex: 1 }}>
        <div className="badge badge-info" style={{ fontWeight: 700, whiteSpace: 'nowrap' }}>
          JUDGE DEMO: STEP {currentStep} OF {DEMO_STEPS.length}
        </div>
        <div>
          <span style={{ fontWeight: 600, color: 'var(--text-main)', fontSize: '12px' }}>
            {stepInfo.title}:{' '}
          </span>
          <span style={{ color: 'var(--text-secondary)', fontSize: '11px' }}>
            {stepInfo.desc}
          </span>
        </div>
      </div>

      {/* Quick Scenario Preset Selector */}
      {onSelectScenario && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', fontFamily: 'monospace' }}>
            Field Simulation:
          </span>
          <select
            onChange={(e) => onSelectScenario(e.target.value)}
            defaultValue="defect"
            style={{
              backgroundColor: '#111827',
              border: '1px solid #374151',
              color: '#38bdf8',
              fontSize: '11px',
              padding: '3px 8px',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: 600
            }}
            title="Execute Controlled Field Simulation Scenario"
          >
            <option value="defect">1. VRT-003 Overlap (Flagship)</option>
            <option value="clean">2. Clean 4-Floor Baseline</option>
            <option value="out_of_parcel">3. TOP-001 Boundary Breach</option>
            <option value="conflicting_evidence">4. Conflicting Evidence</option>
            <option value="missing_evidence">5. Missing Evidence</option>
            <option value="ai_unavailable">6. Offline / AI Unavailable</option>
            <option value="stale_evidence">7. Stale Evidence Detection</option>
            <option value="stale_validation">8. Stale Validation Protection</option>
            <option value="review_rejection">9. Reviewer Rejection</option>
            <option value="golden_workflow">10. Full Golden Workflow</option>
            <option value="failure_recovery">11. Interrupted Upload Recovery</option>
          </select>
        </div>
      )}


      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        {currentStep > 1 && (
          <button className="btn btn-sm" onClick={onPrevStep} disabled={isLoading}>
            Back
          </button>
        )}
        {currentStep < DEMO_STEPS.length ? (
          <button className="btn btn-sm btn-primary" onClick={onNextStep} disabled={isLoading}>
            {stepInfo.actionText}
            <ArrowRight size={12} />
          </button>
        ) : (
          <button className="btn btn-sm btn-success" onClick={onResetDemo} disabled={isLoading}>
            <RotateCcw size={12} />
            Replay Demo Workflow
          </button>
        )}
      </div>
    </div>
  );
};
