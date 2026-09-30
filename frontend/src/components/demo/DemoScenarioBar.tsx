import React from 'react';
import { PlayCircle, CheckCircle, ArrowRight, RotateCcw, AlertTriangle } from 'lucide-react';

interface DemoScenarioBarProps {
  currentStep: number;
  onNextStep: () => void;
  onPrevStep: () => void;
  onResetDemo: () => void;
  isLoading: boolean;
}

const DEMO_STEPS = [
  {
    step: 1,
    title: 'Synthetic Defect Domain Ingested',
    desc: 'Parent ULPIN 12345678901234 loaded in UTM 43N with 4 candidate 3D spatial units (B1, G, L01, L02).',
    actionText: 'Inspect Floor L01',
  },
  {
    step: 2,
    title: 'VRT-003 Blocker Detected',
    desc: 'Notice L01 ceiling at 106.50m and L02 floor at 106.00m (0.50m vertical collision). Red translucent box visualizes overlap.',
    actionText: 'Attempt Approval (Gate C)',
  },
  {
    step: 3,
    title: 'Gate C Rejects Premature Approval',
    desc: 'Approval is strictly blocked by the backend because unresolved BLOCKER issues exist. Backend enforces spatial integrity.',
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
    title: 'Gate C Approval & Audit Export',
    desc: 'With 0 blockers and human ACCEPT review, Gate C permits prototype workflow approval. Audit ledger and JSON export are complete.',
    actionText: 'Inspect Export JSON',
  },
];

export const DemoScenarioBar: React.FC<DemoScenarioBarProps> = ({
  currentStep,
  onNextStep,
  onPrevStep,
  onResetDemo,
  isLoading,
}) => {
  const stepInfo = DEMO_STEPS[Math.min(currentStep - 1, DEMO_STEPS.length - 1)];

  return (
    <div
      style={{
        backgroundColor: '#0c1a30',
        borderBottom: '1px solid var(--color-primary)',
        padding: '8px 18px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        zIndex: 15,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div className="badge badge-info" style={{ fontWeight: 700 }}>
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
