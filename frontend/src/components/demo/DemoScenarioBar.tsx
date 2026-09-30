import React, { useState } from 'react';
import {
  PlayCircle,
  CheckCircle,
  ArrowRight,
  RotateCcw,
  AlertTriangle,
  HelpCircle,
  Activity,
  Layers,
  ChevronDown,
  ChevronUp,
  Eye,
  Info
} from 'lucide-react';

export interface DemoStepInfo {
  step: number;
  time: string;
  title: string;
  seeing: string;
  matters: string;
  actionText: string;
}

export const GOLDEN_DEMO_STEPS: DemoStepInfo[] = [
  {
    step: 1,
    time: "0:00",
    title: "Parent Parcel & ULPIN Context",
    seeing: "Parent parcel ULPIN 12345678901234 loaded in UTM 43N (EPSG:32643) with 2D ground boundary (40m x 30m).",
    matters: "2D parcel remains the immutable statutory anchor. Vertical units must stay strictly bound to this ground root.",
    actionText: "Inspect Attached Evidence"
  },
  {
    step: 2,
    time: "0:20",
    title: "Evidence Ingestion & SHA-256 Checksum",
    seeing: "Total Station Survey (total_station_survey_01.geojson) with SHA-256 integrity hash verification.",
    matters: "Unbroken provenance: no spatial unit may be generated without cryptographic linkage to underlying evidence.",
    actionText: "Generate AI Proposals"
  },
  {
    step: 3,
    time: "0:40",
    title: "AI Candidate Proposal (Non-Authoritative)",
    seeing: "4 proposed floor levels from Prismatic Extrusion model with confidence scores (0.88 - 0.94).",
    matters: "AI IS NOT THE AUTHORITY: Proposals are strictly advisory candidates and cannot enter legal records autonomously.",
    actionText: "Run Spatial Validation"
  },
  {
    step: 4,
    time: "1:00",
    title: "3D Extrusion & Prototype VUID",
    seeing: "Volumetric spatial prisms extruded in 3D WebGL viewer with deterministic prototype VUIDs.",
    matters: "Representation-invariant identity derived from canonical WKB hash. Prototype VUID is not an official 3D ULPIN.",
    actionText: "Detect Geometric Blocker"
  },
  {
    step: 5,
    time: "1:20",
    title: "Deterministic Validation (VRT-003 Blocker)",
    seeing: "Validator detects 0.50m collision between Level L01 (ceil 106.50m) and Level L02 (floor 106.00m).",
    matters: "Mathematical spatial rules are immovable: overlapping rights are strictly prohibited by Gate A validation.",
    actionText: "Inspect Fact Breakdown"
  },
  {
    step: 6,
    time: "1:40",
    title: "Fact-Grounded Explainability & Disagreement",
    seeing: "Exact geometric breakdown (-0.50m vertical gap vs -0.001m tolerance) logged as Disagreement Case A.",
    matters: "Zero hallucination: explainability uses recorded z-values and thresholds, not LLM guesses.",
    actionText: "Open Correction Modal"
  },
  {
    step: 7,
    time: "2:00",
    title: "Human Review & Non-Destructive Correction",
    seeing: "Reviewer corrects Level L01 ceiling from 106.50m down to 106.00m, spawning Revision 2.",
    matters: "Historical integrity: defective Revision 1 is preserved intact in PostgreSQL for future legal audit.",
    actionText: "Observe Revalidation"
  },
  {
    step: 8,
    time: "2:20",
    title: "Revalidation & VUID Regeneration",
    seeing: "Revision 2 passes with 0 blockers. A new deterministic VUID (ending in -FL01) is assigned.",
    matters: "Whenever geometry mutates, validation must be re-run; stale validations cannot approve.",
    actionText: "Submit Officer ACCEPT"
  },
  {
    step: 9,
    time: "2:40",
    title: "Human Officer Sign-Off & Gate C Adjudication",
    seeing: "Officer signs review decision (ACCEPT). Gate C verifies 0 blockers, verified provenance, and human review.",
    matters: "Statutory governance: approval is granted only by authorized officers under prototype simulation.",
    actionText: "Inspect Interoperable Export"
  },
  {
    step: 10,
    time: "3:00",
    title: "Audit Trail, Reproducibility & Export",
    seeing: "Immutable audit event logged; structured JSON v1.0.0, 2D GeoJSON, and 3D Wavefront OBJ exports ready.",
    matters: "Full cycle completed: reproducible, auditable, and interoperability-ready 3D cadastral intelligence.",
    actionText: "Replay Golden Workflow"
  }
];

interface DemoScenarioBarProps {
  currentStep: number;
  onNextStep: () => void;
  onPrevStep: () => void;
  onResetDemo: () => void;
  onSelectScenario?: (key: string) => void;
  onOpenJudgeFAQ: () => void;
  onOpenOverview: () => void;
  isLoading: boolean;
}

export const DemoScenarioBar: React.FC<DemoScenarioBarProps> = ({
  currentStep,
  onNextStep,
  onPrevStep,
  onResetDemo,
  onSelectScenario,
  onOpenJudgeFAQ,
  onOpenOverview,
  isLoading,
}) => {
  const [showPresenterOverlay, setShowPresenterOverlay] = useState(false);
  const stepIdx = Math.min(Math.max(currentStep - 1, 0), GOLDEN_DEMO_STEPS.length - 1);
  const stepInfo = GOLDEN_DEMO_STEPS[stepIdx];

  return (
    <div
      style={{
        backgroundColor: '#0c1a30',
        borderBottom: '1px solid var(--color-primary)',
        padding: '6px 18px',
        display: 'flex',
        flexDirection: 'column',
        gap: '6px',
        zIndex: 15
      }}
    >
      {/* Top Bar Controls */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flex: 1 }}>
          <div className="badge badge-info" style={{ fontWeight: 700, whiteSpace: 'nowrap', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span>JUDGE DEMO</span>
            <span style={{ opacity: 0.8 }}>|</span>
            <span>STEP {stepInfo.step}/10</span>
            <span style={{ fontSize: '10px', color: '#93c5fd' }}>({stepInfo.time})</span>
          </div>

          <div>
            <span style={{ fontWeight: 700, color: 'var(--text-main)', fontSize: '12px' }}>
              {stepInfo.title}:{' '}
            </span>
            <span style={{ color: 'var(--text-secondary)', fontSize: '11px' }}>
              {stepInfo.seeing}
            </span>
          </div>
        </div>

        {/* Action Buttons & Scenario Picker */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {/* 30s Overview */}
          <button
            className="btn btn-sm"
            onClick={onOpenOverview}
            style={{ backgroundColor: '#1e293b', color: '#38bdf8', border: '1px solid #38bdf8', fontSize: '11px', padding: '3px 8px' }}
            title="30-Second Executive Understanding Card"
          >
            <Activity size={12} />
            30s Tour
          </button>

          {/* Judge FAQ */}
          <button
            className="btn btn-sm"
            onClick={onOpenJudgeFAQ}
            style={{ backgroundColor: '#1e293b', color: '#f59e0b', border: '1px solid #f59e0b', fontSize: '11px', padding: '3px 8px' }}
            title="Why 3D? Why VUID? Why AI? - Judge FAQ"
          >
            <HelpCircle size={12} />
            Why? FAQ
          </button>

          {/* Presenter Notes Toggle */}
          <button
            className="btn btn-sm"
            onClick={() => setShowPresenterOverlay(!showPresenterOverlay)}
            style={{ backgroundColor: showPresenterOverlay ? '#0284c7' : '#1e293b', color: '#ffffff', fontSize: '11px', padding: '3px 8px' }}
            title="Toggle Presenter Cue Card"
          >
            <Info size={12} />
            Presenter Cue
          </button>

          {/* Field Simulation Selector */}
          {onSelectScenario && (
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
          )}

          {/* Navigation Controls */}
          {currentStep > 1 && (
            <button className="btn btn-sm" onClick={onPrevStep} disabled={isLoading}>
              Back
            </button>
          )}
          {currentStep < GOLDEN_DEMO_STEPS.length ? (
            <button className="btn btn-sm btn-primary" onClick={onNextStep} disabled={isLoading}>
              {stepInfo.actionText}
              <ArrowRight size={12} />
            </button>
          ) : (
            <button className="btn btn-sm btn-success" onClick={onResetDemo} disabled={isLoading}>
              <RotateCcw size={12} />
              Replay Golden Demo
            </button>
          )}
        </div>
      </div>

      {/* Presenter Cue Card Overlay */}
      {showPresenterOverlay && (
        <div style={{
          backgroundColor: '#07101e',
          border: '1px solid #1e3a5f',
          borderRadius: '6px',
          padding: '10px 14px',
          display: 'grid',
          gridTemplateColumns: '1fr 1.5fr 1fr',
          gap: '16px',
          fontSize: '11px'
        }}>
          <div>
            <span style={{ color: '#38bdf8', fontWeight: 700, textTransform: 'uppercase', display: 'block' }}>
              WHAT YOU ARE SEEING:
            </span>
            <span style={{ color: '#e2e8f0' }}>{stepInfo.seeing}</span>
          </div>
          <div>
            <span style={{ color: '#f59e0b', fontWeight: 700, textTransform: 'uppercase', display: 'block' }}>
              WHY IT MATTERS TO JUDGES:
            </span>
            <span style={{ color: '#cbd5e1' }}>{stepInfo.matters}</span>
          </div>
          <div>
            <span style={{ color: '#10b981', fontWeight: 700, textTransform: 'uppercase', display: 'block' }}>
              RECOMMENDED NEXT ACTION:
            </span>
            <span style={{ color: '#a7f3d0', fontWeight: 600 }}>Click "{stepInfo.actionText}"</span>
          </div>
        </div>
      )}
    </div>
  );
};
