import React, { useState, useEffect } from 'react';
import {
  ParentParcel,
  SpatialUnit,
  EvidenceSource,
  ValidationSummary,
  SpatialUnitRevision,
  AuditEvent,
  StructuredExport,
  AICandidate,
  AIAnomaly,
  AIAssistanceSummary,
  ReviewerQueueItem,
  DisagreementRecord
} from './types';
import { api } from './api/client';
import { AppHeader } from './components/layout/AppHeader';
import { DemoScenarioBar } from './components/demo/DemoScenarioBar';
import { UnitTree } from './components/tree/UnitTree';
import { Cadastral3DViewer } from './components/viewer/Cadastral3DViewer';
import { UnitInspector } from './components/inspector/UnitInspector';
import { ValidationCenter } from './components/validation/ValidationCenter';
import { EvidencePanel } from './components/evidence/EvidencePanel';
import { ReviewWorkspace } from './components/review/ReviewWorkspace';
import { RevisionComparison } from './components/revision/RevisionComparison';
import { AuditTimeline } from './components/audit/AuditTimeline';
import { ExportCenter } from './components/export/ExportCenter';
import { CorrectionModal } from './components/correction/CorrectionModal';

// Slice 3 AI Components
import { AISuggestionsPanel } from './components/ai/AISuggestionsPanel';
import { AnomalyCenter } from './components/ai/AnomalyCenter';
import { ReviewerQueuePanel } from './components/ai/ReviewerQueuePanel';
import { TraceOriginModal } from './components/ai/TraceOriginModal';
import { ModelEvaluationModal } from './components/ai/ModelEvaluationModal';
import { AcceptCandidateModal } from './components/ai/AcceptCandidateModal';
import { RejectCandidateModal } from './components/ai/RejectCandidateModal';
import { ExplainModal } from './components/ai/ExplainModal';

// Slice 4 Validation Intelligence & Reproducibility Components
import { DisagreementTracker } from './components/ai/DisagreementTracker';
import { ReproducibilityModal } from './components/ai/ReproducibilityModal';
import { ValidationExplanationModal } from './components/ai/ValidationExplanationModal';
import { ModelComparisonModal } from './components/ai/ModelComparisonModal';
import { SideBySideEvidenceViewer } from './components/ai/SideBySideEvidenceViewer';

// Slice 5 Operational & Deployment Components
import { SystemReadinessModal } from './components/system/SystemReadinessModal';
import { InteroperabilityExportModal } from './components/export/InteroperabilityExportModal';
import { FieldOperatorView } from './components/field/FieldOperatorView';
import { OperationalRole } from './types';

// Slice 6 Judge Experience Modals
import { JudgeExplanationModal } from './components/system/JudgeExplanationModal';
import { SystemOverviewModal } from './components/system/SystemOverviewModal';

import {
  AlertTriangle,
  FileText,
  CheckSquare,
  GitCompare,
  History,
  Download,
  Brain,
  ShieldAlert,
  ListOrdered,
  Sparkles,
  ArrowRightLeft,
  Columns,
  Hash,
  Smartphone,
  Server
} from 'lucide-react';


const DEFAULT_ULPIN = '12345678901234';

type BottomTab =
  | 'validation'
  | 'disagreements'
  | 'triad-view'
  | 'ai-candidates'
  | 'anomalies'
  | 'queue'
  | 'evidence'
  | 'review'
  | 'revisions'
  | 'audit'
  | 'export'
  | 'field-operator';

export const App: React.FC = () => {
  const [parcel, setParcel] = useState<ParentParcel | null>(null);
  const [units, setUnits] = useState<SpatialUnit[]>([]);
  const [evidenceList, setEvidenceList] = useState<EvidenceSource[]>([]);
  const [validationSummary, setValidationSummary] = useState<ValidationSummary | null>(null);
  const [selectedUnitId, setSelectedUnitId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<BottomTab>('ai-candidates');

  // Governance State
  const [revisions, setRevisions] = useState<SpatialUnitRevision[]>([]);
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);
  const [exportData, setExportData] = useState<StructuredExport | null>(null);
  const [reviewDecisionType, setReviewDecisionType] = useState<string | null>(null);

  // Slice 5 State
  const [activeRole, setActiveRole] = useState<OperationalRole>('ADMIN');
  const [isSystemReadinessOpen, setIsSystemReadinessOpen] = useState(false);
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  // Slice 3 AI State
  const [aiCandidates, setAiCandidates] = useState<AICandidate[]>([]);
  const [aiAnomalies, setAiAnomalies] = useState<AIAnomaly[]>([]);
  const [aiSummary, setAiSummary] = useState<AIAssistanceSummary | null>(null);
  const [reviewerQueue, setReviewerQueue] = useState<ReviewerQueueItem[]>([]);
  const [selectedCandidateId, setSelectedCandidateId] = useState<string | null>(null);

  // Slice 4 Disagreement & Reproducibility State
  const [disagreements, setDisagreements] = useState<DisagreementRecord[]>([]);
  const [isReproducibilityModalOpen, setIsReproducibilityModalOpen] = useState(false);
  const [reproducibilityTargetId, setReproducibilityTargetId] = useState<string>(DEFAULT_ULPIN);
  const [isValidationExplainModalOpen, setIsValidationExplainModalOpen] = useState(false);
  const [explainRunId, setExplainRunId] = useState<string>('');
  const [isModelComparisonModalOpen, setIsModelComparisonModalOpen] = useState(false);


  // Modals & Dialogs
  const [isCorrectionModalOpen, setIsCorrectionModalOpen] = useState(false);
  const [isDemoGuideOpen, setIsDemoGuideOpen] = useState(true);
  const [isJudgeFAQOpen, setIsJudgeFAQOpen] = useState(false);
  const [isOverviewOpen, setIsOverviewOpen] = useState(false);
  const [demoStep, setDemoStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [toastMessage, setToastMessage] = useState<{ text: string; type: 'success' | 'error' | 'info' } | null>(null);

  // AI Modals
  const [isTraceOriginOpen, setIsTraceOriginOpen] = useState(false);
  const [traceTargetId, setTraceTargetId] = useState<string>(DEFAULT_ULPIN);
  const [isModelModalOpen, setIsModelModalOpen] = useState(false);
  const [candidateToAccept, setCandidateToAccept] = useState<AICandidate | null>(null);
  const [candidateToReject, setCandidateToReject] = useState<AICandidate | null>(null);
  const [candidateToExplain, setCandidateToExplain] = useState<string | null>(null);

  const showToast = (text: string, type: 'success' | 'error' | 'info' = 'info') => {
    setToastMessage({ text, type });
    setTimeout(() => setToastMessage(null), 4000);
  };

  // Initial & Refresh Data Load
  const loadWorkspaceData = async (ulpin: string = DEFAULT_ULPIN) => {
    setIsLoading(true);
    try {
      const [
        parcelData,
        unitsData,
        evidenceData,
        valData,
        recentAudits,
        candidatesData,
        anomaliesData,
        summaryData,
        queueData,
        disagreementsData
      ] = await Promise.all([
        api.getParcel(ulpin),
        api.getParcelUnits(ulpin),
        api.getParcelEvidence(ulpin),
        api.getValidation(ulpin),
        api.getRecentAudits(40),
        api.getAiCandidates(ulpin).catch(() => ({ candidates: [] })),
        api.getAiAnomalies(ulpin).catch(() => ({ anomalies: [] })),
        api.getAiSummary(ulpin).catch(() => null),
        api.getReviewerQueue(ulpin).catch(() => ({ items: [] })),
        api.getValidationDisagreements(ulpin).catch(() => ({ disagreements: [] })),
      ]);

      setParcel(parcelData);
      setUnits(unitsData);
      setEvidenceList(evidenceData);
      setValidationSummary(valData);
      setAuditEvents(recentAudits);

      setAiCandidates(candidatesData.candidates || []);
      setAiAnomalies(anomaliesData.anomalies || []);
      setAiSummary(summaryData);
      setReviewerQueue(queueData.items || []);
      setDisagreements(disagreementsData.disagreements || []);

      if (candidatesData.candidates && candidatesData.candidates.length > 0 && !selectedCandidateId) {
        setSelectedCandidateId(candidatesData.candidates[0].candidate_id);
      }

      // Default select L01 (the candidate with the defect)
      const l01 = unitsData.find((u) => u.level_code === 'L01');
      const selected = l01 || unitsData[0];
      if (selected) {
        setSelectedUnitId(selected.id);
        const revs = await api.getUnitRevisions(selected.prototype_vuid);
        setRevisions(revs);
      }
    } catch (err: any) {
      showToast(`Load Error: ${err.message}`, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadWorkspaceData();
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);


  // Update Revisions and Export when selected unit changes
  useEffect(() => {
    const selected = units.find((u) => u.id === selectedUnitId);
    if (selected) {
      api.getUnitRevisions(selected.prototype_vuid).then(setRevisions).catch(console.error);
      if (selected.active_revision_id) {
        api.getAuditForRevision(selected.active_revision_id).then(setAuditEvents).catch(console.error);
      }
    }
  }, [selectedUnitId, units]);

  const selectedUnit = units.find((u) => u.id === selectedUnitId) || null;
  const blockerCount = validationSummary?.blocker_count ?? 0;
  const hasOverlapDefect = blockerCount > 0;
  const isApproved = selectedUnit?.status === 'APPROVED';

  // Demo Reset Handler
  const handleResetDemo = async () => {
    setIsLoading(true);
    try {
      await api.resetDemo('defect');
      // Also run AI inference on the reset parcel
      await api.runAiInference(DEFAULT_ULPIN);
      await loadWorkspaceData(DEFAULT_ULPIN);
      setReviewDecisionType(null);
      setExportData(null);
      setActiveTab('ai-candidates');
      setDemoStep(1);
      showToast('Demo reset successfully: AI proposals synthesized with VRT-003 overlap blocker.', 'success');
    } catch (err: any) {
      showToast(`Reset Failed: ${err.message}`, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  // AI Pipeline Execution Handler
  const handleRunInference = async () => {
    setIsLoading(true);
    try {
      const res = await api.runAiInference(DEFAULT_ULPIN);
      setAiCandidates(res.candidates || []);
      setAiAnomalies(res.anomalies || []);
      setAiSummary(res.summary);
      const queue = await api.getReviewerQueue(DEFAULT_ULPIN);
      setReviewerQueue(queue.items || []);
      setActiveTab('ai-candidates');
      showToast(`AI inference complete: Generated ${res.candidates?.length || 0} proposals and detected ${res.anomalies?.length || 0} anomalies.`, 'success');
    } catch (err: any) {
      showToast(`AI Inference Error: ${err.message}`, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  // AI Candidate Accept Handler
  const handleAcceptCandidateConfirm = async (
    candidateId: string,
    reviewerId: string,
    justification: string
  ) => {
    setIsLoading(true);
    try {
      const res = await api.acceptCandidate(candidateId, reviewerId, justification);
      showToast(`Proposal accepted! Promoted to governed unit with VUID ${res.prototype_vuid}`, 'success');
      await loadWorkspaceData(DEFAULT_ULPIN);
      setSelectedUnitId(res.spatial_unit_id);
      setActiveTab('validation');
    } catch (err: any) {
      showToast(`Acceptance Failed: ${err.message}`, 'error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // AI Candidate Reject Handler
  const handleRejectCandidateConfirm = async (
    candidateId: string,
    reviewerId: string,
    justification: string
  ) => {
    setIsLoading(true);
    try {
      await api.rejectCandidate(candidateId, reviewerId, justification);
      showToast('Proposal rejected and permanently recorded in audit history.', 'info');
      await loadWorkspaceData(DEFAULT_ULPIN);
    } catch (err: any) {
      showToast(`Rejection Failed: ${err.message}`, 'error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // Submit Correction Handler
  const handleSubmitCorrection = async (
    revisionId: string,
    zMin: number,
    zMax: number,
    reason: string
  ) => {
    setIsLoading(true);
    try {
      const res = await api.submitCorrection(revisionId, zMin, zMax, reason);
      showToast(`Correction applied! Created Revision ${res.status} with VUID ${res.prototype_vuid}`, 'success');
      setIsCorrectionModalOpen(false);

      await loadWorkspaceData(DEFAULT_ULPIN);
      setActiveTab('revisions');
      setDemoStep(5);
    } catch (err: any) {
      showToast(`Correction Failed: ${err.message}`, 'error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // Human Review Handlers
  const handleAcceptReview = async (revisionId: string, reason: string) => {
    setIsLoading(true);
    try {
      await api.submitReview(revisionId, 'ACCEPT', reason);
      setReviewDecisionType('ACCEPT');
      showToast('Review decision ACCEPT recorded. Gate C approval is now eligible.', 'success');
      await loadWorkspaceData(DEFAULT_ULPIN);
      setDemoStep(6);
    } catch (err: any) {
      showToast(`Review Rejected: ${err.message}`, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRejectReview = async (revisionId: string, reason: string) => {
    setIsLoading(true);
    try {
      await api.submitReview(revisionId, 'REJECT', reason);
      setReviewDecisionType('REJECT');
      showToast('Review decision REJECT recorded.', 'info');
      await loadWorkspaceData(DEFAULT_ULPIN);
    } catch (err: any) {
      showToast(`Review Failed: ${err.message}`, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  // Gate C Approval Handler
  const handleApproveRevision = async (revisionId: string, reason: string) => {
    setIsLoading(true);
    try {
      const res = await api.submitApproval(revisionId, reason);
      showToast(`Prototype Workflow Approved! Approved VUID: ${res.id}`, 'success');
      await loadWorkspaceData(DEFAULT_ULPIN);

      const exp = await api.getExportForRevision(revisionId);
      setExportData(exp);
      setActiveTab('export');
      setDemoStep(6);
    } catch (err: any) {
      showToast(`Approval Prohibited: ${err.message}`, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  // Export Refresh Handler
  const handleRefreshExport = async () => {
    if (!selectedUnit?.active_revision_id) return;
    setIsLoading(true);
    try {
      const exp = await api.getExportForRevision(selectedUnit.active_revision_id);
      setExportData(exp);
      showToast('Structured export refreshed from backend.', 'info');
    } catch (err: any) {
      showToast(`Export Error: ${err.message}`, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  // Scenario Loader
  const handleSelectScenario = async (scenarioKey: string) => {
    setIsLoading(true);
    try {
      await api.executeScenario(scenarioKey);
      await loadWorkspaceData(DEFAULT_ULPIN);
      if (scenarioKey === 'conflicting_evidence') {
        setActiveTab('evidence');
      } else if (scenarioKey === 'ai_unavailable') {
        setActiveTab('validation');
      } else if (scenarioKey === 'stale_evidence' || scenarioKey === 'stale_validation') {
        setActiveTab('review');
      } else if (scenarioKey === 'review_rejection') {
        setActiveTab('review');
      } else {
        setActiveTab('ai-candidates');
      }
      showToast(`Field Simulation Loaded: ${scenarioKey.toUpperCase().replace('_', ' ')}`, 'success');
    } catch (err: any) {
      showToast(`Scenario load error: ${err.message}`, 'error');
    } finally {
      setIsLoading(false);
    }
  };


  // Judge Demo Guide Stepper
  const handleNextDemoStep = async () => {
    if (demoStep === 1) {
      const l01 = units.find((u) => u.level_code === 'L01');
      if (l01) setSelectedUnitId(l01.id);
      setActiveTab('validation');
      setDemoStep(2);
    } else if (demoStep === 2) {
      setActiveTab('review');
      setDemoStep(3);
    } else if (demoStep === 3) {
      setIsCorrectionModalOpen(true);
      setDemoStep(4);
    } else if (demoStep === 4) {
      setActiveTab('revisions');
      setDemoStep(5);
    } else if (demoStep === 5) {
      setActiveTab('review');
      setDemoStep(6);
    } else if (demoStep === 6) {
      if (selectedUnit?.active_revision_id) {
        const exp = await api.getExportForRevision(selectedUnit.active_revision_id);
        setExportData(exp);
      }
      setActiveTab('export');
    }
  };

  const handlePrevDemoStep = () => {
    setDemoStep((prev) => Math.max(1, prev - 1));
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', width: '100vw', overflow: 'hidden' }}>
      {/* Toast Notification */}
      {toastMessage && (
        <div
          style={{
            position: 'fixed',
            top: '64px',
            right: '24px',
            zIndex: 100,
            padding: '10px 16px',
            borderRadius: '6px',
            backgroundColor:
              toastMessage.type === 'success'
                ? 'var(--color-success)'
                : toastMessage.type === 'error'
                ? 'var(--color-blocker)'
                : 'var(--color-primary)',
            color: '#ffffff',
            fontSize: '12px',
            fontWeight: 500,
            boxShadow: '0 8px 24px rgba(0,0,0,0.4)',
            maxWidth: '480px',
          }}
        >
          {toastMessage.text}
        </div>
      )}

      {/* Module A: App Header */}
      <AppHeader
        ulpin={parcel?.ulpin || ''}
        status={selectedUnit?.status || 'GENERATED'}
        blockerCount={blockerCount}
        candidateCount={aiCandidates.length}
        anomalyCount={aiAnomalies.length}
        disagreementCount={disagreements.length}
        activeRole={activeRole}
        onChangeRole={setActiveRole}
        onResetDemo={handleResetDemo}
        onToggleDemoGuide={() => setIsDemoGuideOpen(!isDemoGuideOpen)}
        onOpenTraceOrigin={() => {
          setTraceTargetId(selectedCandidateId || selectedUnit?.prototype_vuid || DEFAULT_ULPIN);
          setIsTraceOriginOpen(true);
        }}
        onOpenModelCards={() => setIsModelModalOpen(true)}
        onOpenCompareModels={() => setIsModelComparisonModalOpen(true)}
        onOpenSystemReadiness={() => setIsSystemReadinessOpen(true)}
        onOpenExportModal={() => {
          if (!exportData && selectedUnit?.active_revision_id) {
            api.getExportForRevision(selectedUnit.active_revision_id).then(exp => {
              setExportData(exp);
              setIsExportModalOpen(true);
            }).catch(() => setIsExportModalOpen(true));
          } else {
            setIsExportModalOpen(true);
          }
        }}
        isDemoGuideOpen={isDemoGuideOpen}
        isLoading={isLoading}
      />

      {/* Offline Alert Banner */}
      {!isOnline && (
        <div style={{
          backgroundColor: '#991b1b',
          color: '#fecaca',
          padding: '6px 16px',
          fontSize: '11px',
          fontWeight: 700,
          textAlign: 'center',
          borderBottom: '1px solid #dc2626'
        }}>
          CONNECTION LOST — DISPLAYING LAST VERIFIED LOCAL STATE. NO FABRICATED UPDATES.
        </div>
      )}


      {/* Module K: Demo Scenario Bar */}
      {isDemoGuideOpen && (
        <DemoScenarioBar
          currentStep={demoStep}
          onNextStep={handleNextDemoStep}
          onPrevStep={handlePrevDemoStep}
          onResetDemo={handleResetDemo}
          onSelectScenario={handleSelectScenario}
          onOpenJudgeFAQ={() => setIsJudgeFAQOpen(true)}
          onOpenOverview={() => setIsOverviewOpen(true)}
          isLoading={isLoading}
        />
      )}

      {/* Main Workspace Layout (3-Column / Resizable) */}
      <div style={{ display: 'flex', flex: 1, minHeight: 0, overflow: 'hidden' }}>
        {/* Left Column: Parcel & Unit Tree Hierarchy */}
        <UnitTree
          parcel={parcel}
          units={units}
          selectedUnitId={selectedUnitId}
          onSelectUnit={(id) => {
            setSelectedUnitId(id);
            const match = units.find((u) => u.id === id);
            if (match) {
              const candMatch = aiCandidates.find((c) => c.level_code === match.level_code);
              if (candMatch) setSelectedCandidateId(candMatch.candidate_id);
            }
          }}
          hasOverlapDefect={hasOverlapDefect}
        />

        {/* Center Column: 3D Cadastral Viewer (Top) + Interactive Intelligence Panels (Bottom) */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0, borderRight: '1px solid var(--border-subtle)' }}>
          {/* Module B: 3D Cadastral Viewer */}
          <div style={{ height: '48%', position: 'relative', borderBottom: '1px solid var(--border-subtle)' }}>
            <Cadastral3DViewer
              parcel={parcel}
              units={units}
              aiCandidates={aiCandidates}
              selectedUnitId={selectedUnitId}
              selectedCandidateId={selectedCandidateId}
              onSelectUnit={(id) => setSelectedUnitId(id)}
              onSelectCandidate={(candId) => {
                setSelectedCandidateId(candId);
                const matchCand = aiCandidates.find((c) => c.candidate_id === candId);
                if (matchCand) {
                  const matchUnit = units.find((u) => u.level_code === matchCand.level_code);
                  if (matchUnit) setSelectedUnitId(matchUnit.id);
                }
              }}
              hasOverlapDefect={hasOverlapDefect}
              overlapElevationRange={{ min: 106.0, max: 106.5 }}
            />
          </div>

          {/* Bottom Tabs Panel */}
          <div style={{ height: '52%', display: 'flex', flexDirection: 'column', minHeight: 0, backgroundColor: 'var(--bg-main)' }}>
            {/* Tab Navigation Header */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                backgroundColor: 'rgba(14, 23, 38, 0.95)',
                borderBottom: '1px solid var(--border-subtle)',
                padding: '0 12px',
                gap: '4px',
                overflowX: 'auto',
                position: 'relative',
                zIndex: 10,
                flexShrink: 0,
              }}
            >
              <button
                className={`btn btn-sm ${activeTab === 'ai-candidates' ? 'btn-primary' : ''}`}
                style={{ borderRadius: '4px 4px 0 0', borderBottom: 'none' }}
                onClick={() => setActiveTab('ai-candidates')}
              >
                <Brain size={12} className="text-cyan-400" />
                AI Proposals ({aiCandidates.length})
              </button>

              <button
                className={`btn btn-sm ${activeTab === 'anomalies' ? 'btn-primary' : ''}`}
                style={{ borderRadius: '4px 4px 0 0', borderBottom: 'none' }}
                onClick={() => setActiveTab('anomalies')}
              >
                <ShieldAlert size={12} className={aiAnomalies.length > 0 ? 'text-red-400' : 'text-slate-400'} />
                Anomalies ({aiAnomalies.length})
              </button>

              <button
                className={`btn btn-sm ${activeTab === 'queue' ? 'btn-primary' : ''}`}
                style={{ borderRadius: '4px 4px 0 0', borderBottom: 'none' }}
                onClick={() => setActiveTab('queue')}
              >
                <ListOrdered size={12} />
                Reviewer Queue ({reviewerQueue.length})
              </button>

              <button
                className={`btn btn-sm ${activeTab === 'validation' ? 'btn-primary' : ''}`}
                style={{ borderRadius: '4px 4px 0 0', borderBottom: 'none' }}
                onClick={() => setActiveTab('validation')}
              >
                <AlertTriangle size={12} />
                Validation ({blockerCount} Blockers)
              </button>

              <button
                className={`btn btn-sm ${activeTab === 'disagreements' ? 'btn-primary' : ''}`}
                style={{ borderRadius: '4px 4px 0 0', borderBottom: 'none' }}
                onClick={() => setActiveTab('disagreements')}
              >
                <ShieldAlert size={12} className={disagreements.some(d => d.severity === 'BLOCKER') ? 'text-red-400' : 'text-slate-400'} />
                Disagreements ({disagreements.length})
              </button>

              <button
                className={`btn btn-sm ${activeTab === 'triad-view' ? 'btn-primary' : ''}`}
                style={{ borderRadius: '4px 4px 0 0', borderBottom: 'none' }}
                onClick={() => setActiveTab('triad-view')}
              >
                <Columns size={12} />
                Side-by-Side Triad
              </button>

              <button
                className={`btn btn-sm ${activeTab === 'evidence' ? 'btn-primary' : ''}`}
                style={{ borderRadius: '4px 4px 0 0', borderBottom: 'none' }}
                onClick={() => setActiveTab('evidence')}
              >
                <FileText size={12} />
                Evidence & Provenance ({evidenceList.length})
              </button>

              <button
                className={`btn btn-sm ${activeTab === 'review' ? 'btn-primary' : ''}`}
                style={{ borderRadius: '4px 4px 0 0', borderBottom: 'none' }}
                onClick={() => setActiveTab('review')}
              >
                <CheckSquare size={12} />
                Review & Gate C
              </button>

              <button
                className={`btn btn-sm ${activeTab === 'revisions' ? 'btn-primary' : ''}`}
                style={{ borderRadius: '4px 4px 0 0', borderBottom: 'none' }}
                onClick={() => setActiveTab('revisions')}
              >
                <GitCompare size={12} />
                Revisions ({revisions.length})
              </button>

              <button
                className={`btn btn-sm ${activeTab === 'audit' ? 'btn-primary' : ''}`}
                style={{ borderRadius: '4px 4px 0 0', borderBottom: 'none' }}
                onClick={() => setActiveTab('audit')}
              >
                <History size={12} />
                Audit Trail ({auditEvents.length})
              </button>

              <button
                className={`btn btn-sm ${activeTab === 'export' ? 'btn-primary' : ''}`}
                style={{ borderRadius: '4px 4px 0 0', borderBottom: 'none' }}
                onClick={() => {
                  setActiveTab('export');
                  if (!exportData && selectedUnit?.active_revision_id) {
                    handleRefreshExport();
                  }
                }}
              >
                <Download size={12} />
                Export
              </button>

              <button
                className={`btn btn-sm ${activeTab === 'field-operator' ? 'btn-primary' : ''}`}
                style={{ borderRadius: '4px 4px 0 0', borderBottom: 'none' }}
                onClick={() => setActiveTab('field-operator')}
              >
                <Smartphone size={12} className="text-emerald-400" />
                Field View
              </button>
            </div>


            {/* Tab Body */}
            <div style={{ flex: 1, minHeight: 0, overflowY: 'auto', padding: '12px' }}>
              {activeTab === 'ai-candidates' && (
                <AISuggestionsPanel
                  candidates={aiCandidates}
                  selectedCandidateId={selectedCandidateId}
                  onSelectCandidate={(candId) => {
                    setSelectedCandidateId(candId);
                    const match = units.find((u) => u.level_code === aiCandidates.find((c) => c.candidate_id === candId)?.level_code);
                    if (match) setSelectedUnitId(match.id);
                  }}
                  onAcceptCandidate={(cand) => setCandidateToAccept(cand)}
                  onRejectCandidate={(cand) => setCandidateToReject(cand)}
                  onExplainCandidate={(candId) => setCandidateToExplain(candId)}
                  onTraceLineage={(candId) => {
                    setTraceTargetId(candId);
                    setIsTraceOriginOpen(true);
                  }}
                  onRunInference={handleRunInference}
                  isLoading={isLoading}
                />
              )}

              {activeTab === 'anomalies' && (
                <AnomalyCenter
                  anomalies={aiAnomalies}
                  onInspectUnit={(levelCode) => {
                    const match = units.find((u) => u.level_code === levelCode);
                    if (match) setSelectedUnitId(match.id);
                  }}
                  onRequestCorrection={(levelCode) => {
                    const match = units.find((u) => u.level_code === levelCode);
                    if (match) {
                      setSelectedUnitId(match.id);
                      setIsCorrectionModalOpen(true);
                    }
                  }}
                />
              )}

              {activeTab === 'queue' && (
                <ReviewerQueuePanel
                  queueItems={reviewerQueue}
                  onSelectQueueItem={(item) => {
                    if (item.affected_level) {
                      const matchUnit = units.find((u) => u.level_code === item.affected_level);
                      if (matchUnit) setSelectedUnitId(matchUnit.id);
                      const matchCand = aiCandidates.find((c) => c.level_code === item.affected_level);
                      if (matchCand) setSelectedCandidateId(matchCand.candidate_id);
                    }
                    if (item.item_type === 'BLOCKER') {
                      setActiveTab('validation');
                    } else if (item.item_type === 'ANOMALY') {
                      setActiveTab('anomalies');
                    } else {
                      setActiveTab('ai-candidates');
                    }
                  }}
                />
              )}

              {activeTab === 'validation' && (
                <ValidationCenter
                  summary={validationSummary}
                  onInspectUnit={(levelCode) => {
                    const match = units.find((u) => u.level_code === levelCode);
                    if (match) setSelectedUnitId(match.id);
                  }}
                  onRequestCorrection={(levelCode) => {
                    const match = units.find((u) => u.level_code === levelCode);
                    if (match) {
                      setSelectedUnitId(match.id);
                      setIsCorrectionModalOpen(true);
                    }
                  }}
                />
              )}

              {activeTab === 'disagreements' && (
                <DisagreementTracker
                  disagreements={disagreements}
                  onSelectCandidate={(candId) => {
                    setSelectedCandidateId(candId);
                    const match = units.find((u) => u.level_code === aiCandidates.find((c) => c.candidate_id === candId)?.level_code);
                    if (match) setSelectedUnitId(match.id);
                  }}
                  onExplainCandidate={(candId) => setCandidateToExplain(candId)}
                />
              )}

              {activeTab === 'triad-view' && (
                <SideBySideEvidenceViewer
                  candidate={aiCandidates.find((c) => c.candidate_id === selectedCandidateId) || aiCandidates[0] || null}
                  evidenceList={evidenceList}
                  validationSummary={validationSummary}
                  onExplainCandidate={(candId) => setCandidateToExplain(candId)}
                  onOpenReproducibility={(candId) => {
                    setReproducibilityTargetId(candId);
                    setIsReproducibilityModalOpen(true);
                  }}
                />
              )}

              {activeTab === 'evidence' && <EvidencePanel evidenceList={evidenceList} />}

              {activeTab === 'review' && (
                <ReviewWorkspace
                  unit={selectedUnit}
                  validationSummary={validationSummary}
                  onAcceptReview={handleAcceptReview}
                  onRequestCorrection={(u) => {
                    setSelectedUnitId(u.id);
                    setIsCorrectionModalOpen(true);
                  }}
                  onRejectReview={handleRejectReview}
                  onApproveRevision={handleApproveRevision}
                  hasActiveReviewDecision={Boolean(reviewDecisionType)}
                  reviewDecisionType={reviewDecisionType}
                  isApproved={isApproved}
                  isLoading={isLoading}
                />
              )}

              {activeTab === 'revisions' && (
                <RevisionComparison
                  revisions={revisions}
                  currentVuid={selectedUnit?.prototype_vuid || ''}
                />
              )}

              {activeTab === 'audit' && <AuditTimeline events={auditEvents} />}

              {activeTab === 'export' && (
                <ExportCenter
                  exportData={exportData}
                  onRefreshExport={handleRefreshExport}
                  isLoading={isLoading}
                />
              )}

              {activeTab === 'field-operator' && (
                <FieldOperatorView
                  ulpin={parcel?.ulpin || DEFAULT_ULPIN}
                  units={units}
                  evidence={evidenceList}
                  issues={validationSummary?.issues || []}
                  isOnline={isOnline}
                  onSelectUnit={(u) => setSelectedUnitId(u.id)}
                  onRequestCorrection={() => setIsCorrectionModalOpen(true)}
                />
              )}
            </div>

          </div>
        </div>

        {/* Right Column: Spatial Unit Inspector */}
        <UnitInspector
          unit={selectedUnit}
          onRequestCorrection={(u) => {
            setSelectedUnitId(u.id);
            setIsCorrectionModalOpen(true);
          }}
          onViewRevisions={() => setActiveTab('revisions')}
          onExport={(revId) => {
            setActiveTab('export');
            handleRefreshExport();
          }}
          onOpenReproducibility={(targetId) => {
            setReproducibilityTargetId(targetId);
            setIsReproducibilityModalOpen(true);
          }}
          onExplainValidation={() => {
            setExplainRunId(validationSummary?.run_id || '');
            setIsValidationExplainModalOpen(true);
          }}
          isConflicting={hasOverlapDefect && selectedUnit?.level_code === 'L01'}
        />
      </div>

      {/* Non-Destructive Correction Modal */}
      {selectedUnit && (
        <CorrectionModal
          unit={selectedUnit}
          isOpen={isCorrectionModalOpen}
          onClose={() => setIsCorrectionModalOpen(false)}
          onSubmit={handleSubmitCorrection}
          isLoading={isLoading}
        />
      )}

      {/* Slice 3: Trace Origin Lineage Modal */}
      <TraceOriginModal
        identifier={traceTargetId}
        isOpen={isTraceOriginOpen}
        onClose={() => setIsTraceOriginOpen(false)}
      />

      {/* Slice 3: Model Evaluation & Benchmark Modal */}
      <ModelEvaluationModal
        isOpen={isModelModalOpen}
        onClose={() => setIsModelModalOpen(false)}
      />

      {/* Slice 3: Accept Candidate Modal */}
      <AcceptCandidateModal
        candidate={candidateToAccept}
        isOpen={Boolean(candidateToAccept)}
        onClose={() => setCandidateToAccept(null)}
        onConfirm={handleAcceptCandidateConfirm}
      />

      {/* Slice 3: Reject Candidate Modal */}
      <RejectCandidateModal
        candidate={candidateToReject}
        isOpen={Boolean(candidateToReject)}
        onClose={() => setCandidateToReject(null)}
        onConfirm={handleRejectCandidateConfirm}
      />

      {/* Slice 3: Explain Modal */}
      <ExplainModal
        candidateId={candidateToExplain}
        isOpen={Boolean(candidateToExplain)}
        onClose={() => setCandidateToExplain(null)}
      />

      {/* Slice 4: Reproducibility Snapshot Modal */}
      {isReproducibilityModalOpen && (
        <ReproducibilityModal
          targetId={reproducibilityTargetId}
          onClose={() => setIsReproducibilityModalOpen(false)}
        />
      )}

      {/* Slice 4: Validation Explanation Modal */}
      {isValidationExplainModalOpen && (
        <ValidationExplanationModal
          runId={explainRunId || validationSummary?.run_id || ''}
          onClose={() => setIsValidationExplainModalOpen(false)}
        />
      )}

      {/* Slice 4: Model Comparison Modal */}
      {isModelComparisonModalOpen && (
        <ModelComparisonModal
          parentUlpin={DEFAULT_ULPIN}
          onClose={() => setIsModelComparisonModalOpen(false)}
        />
      )}

      {/* Slice 5: System Readiness & Integrity Modal */}
      <SystemReadinessModal
        isOpen={isSystemReadinessOpen}
        onClose={() => setIsSystemReadinessOpen(false)}
      />

      {/* Slice 5: Interoperability Export Modal */}
      <InteroperabilityExportModal
        isOpen={isExportModalOpen}
        onClose={() => setIsExportModalOpen(false)}
        exportData={exportData}
        ulpin={parcel?.ulpin || DEFAULT_ULPIN}
        revisionId={selectedUnit?.active_revision_id || ''}
      />

      {/* Slice 6: Judge Technical FAQ Modal */}
      <JudgeExplanationModal
        isOpen={isJudgeFAQOpen}
        onClose={() => setIsJudgeFAQOpen(false)}
      />

      {/* Slice 6: 30-Second System Overview Modal */}
      <SystemOverviewModal
        isOpen={isOverviewOpen}
        onClose={() => setIsOverviewOpen(false)}
        parcel={parcel}
        units={units}
        validationSummary={validationSummary}
        onStartGoldenDemo={() => {
          setDemoStep(1);
          setIsDemoGuideOpen(true);
        }}
      />
    </div>
  );
};


export default App;
