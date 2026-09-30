import React, { useState, useEffect } from 'react';
import {
  ParentParcel,
  SpatialUnit,
  EvidenceSource,
  ValidationSummary,
  SpatialUnitRevision,
  AuditEvent,
  StructuredExport,
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
import { CheckCircle2, AlertTriangle, Shield, Layers, FileText, CheckSquare, GitCompare, History, Download } from 'lucide-react';

const DEFAULT_ULPIN = '12345678901234';

type BottomTab = 'validation' | 'evidence' | 'review' | 'revisions' | 'audit' | 'export';

export const App: React.FC = () => {
  const [parcel, setParcel] = useState<ParentParcel | null>(null);
  const [units, setUnits] = useState<SpatialUnit[]>([]);
  const [evidenceList, setEvidenceList] = useState<EvidenceSource[]>([]);
  const [validationSummary, setValidationSummary] = useState<ValidationSummary | null>(null);
  const [selectedUnitId, setSelectedUnitId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<BottomTab>('validation');

  // Governance State
  const [revisions, setRevisions] = useState<SpatialUnitRevision[]>([]);
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);
  const [exportData, setExportData] = useState<StructuredExport | null>(null);
  const [reviewDecisionType, setReviewDecisionType] = useState<string | null>(null);

  // Modals & UI Controls
  const [isCorrectionModalOpen, setIsCorrectionModalOpen] = useState(false);
  const [isDemoGuideOpen, setIsDemoGuideOpen] = useState(true);
  const [demoStep, setDemoStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [toastMessage, setToastMessage] = useState<{ text: string; type: 'success' | 'error' | 'info' } | null>(null);

  const showToast = (text: string, type: 'success' | 'error' | 'info' = 'info') => {
    setToastMessage({ text, type });
    setTimeout(() => setToastMessage(null), 4000);
  };

  // Initial Data Load
  const loadWorkspaceData = async (ulpin: string = DEFAULT_ULPIN) => {
    setIsLoading(true);
    try {
      const [parcelData, unitsData, evidenceData, valData, recentAudits] = await Promise.all([
        api.getParcel(ulpin),
        api.getParcelUnits(ulpin),
        api.getParcelEvidence(ulpin),
        api.getValidation(ulpin),
        api.getRecentAudits(40),
      ]);

      setParcel(parcelData);
      setUnits(unitsData);
      setEvidenceList(evidenceData);
      setValidationSummary(valData);
      setAuditEvents(recentAudits);

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
      await loadWorkspaceData(DEFAULT_ULPIN);
      setReviewDecisionType(null);
      setExportData(null);
      setActiveTab('validation');
      setDemoStep(1);
      showToast('Demo reset successfully to initial defect state (VRT-003 blocker active).', 'success');
    } catch (err: any) {
      showToast(`Reset Failed: ${err.message}`, 'error');
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

      // Reload full state to reflect new revision and revalidation
      await loadWorkspaceData(DEFAULT_ULPIN);

      // Select L01 and switch to revisions comparison tab
      const updatedL01 = units.find((u) => u.level_code === 'L01');
      if (updatedL01) {
        const revs = await api.getUnitRevisions(updatedL01.prototype_vuid);
        setRevisions(revs);
      }
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
      const res = await api.submitReview(revisionId, 'ACCEPT', reason);
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

      // Fetch structured export
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

  // Judge Demo Guide Stepper
  const handleNextDemoStep = async () => {
    if (demoStep === 1) {
      // Step 1 -> 2: Select L01 and switch to Validation tab
      const l01 = units.find((u) => u.level_code === 'L01');
      if (l01) setSelectedUnitId(l01.id);
      setActiveTab('validation');
      setDemoStep(2);
    } else if (demoStep === 2) {
      // Step 2 -> 3: Attempt premature approval (shows Gate C refusal)
      setActiveTab('review');
      setDemoStep(3);
    } else if (demoStep === 3) {
      // Step 3 -> 4: Open correction modal
      setIsCorrectionModalOpen(true);
      setDemoStep(4);
    } else if (demoStep === 4) {
      // Step 4 -> 5: Open Revisions tab
      setActiveTab('revisions');
      setDemoStep(5);
    } else if (demoStep === 5) {
      // Step 5 -> 6: Open Review tab
      setActiveTab('review');
      setDemoStep(6);
    } else if (demoStep === 6) {
      // Step 6: Open Export tab
      if (selectedUnit?.active_revision_id) {
        const exp = await api.getExportForRevision(selectedUnit.active_revision_id);
        setExportData(exp);
      }
      setActiveTab('export');
    }
  };

  const handlePrevDemoStep = () => {
    if (demoStep > 1) setDemoStep(demoStep - 1);
  };

  return (
    <div className="app-container">
      {/* Toast Notification */}
      {toastMessage && (
        <div
          style={{
            position: 'fixed',
            top: '68px',
            right: '20px',
            zIndex: 9999,
            padding: '10px 16px',
            borderRadius: '6px',
            fontSize: '12px',
            fontWeight: 500,
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            backgroundColor:
              toastMessage.type === 'error'
                ? 'var(--color-blocker)'
                : toastMessage.type === 'success'
                ? 'var(--color-success)'
                : 'var(--color-primary)',
            color: '#ffffff',
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.4)',
          }}
        >
          {toastMessage.text}
        </div>
      )}

      {/* Top Header */}
      <AppHeader
        ulpin={parcel?.ulpin || ''}
        status={selectedUnit?.status || 'GENERATED'}
        blockerCount={blockerCount}
        onResetDemo={handleResetDemo}
        onToggleDemoGuide={() => setIsDemoGuideOpen(!isDemoGuideOpen)}
        isDemoGuideOpen={isDemoGuideOpen}
        isLoading={isLoading}
      />

      {/* Judge Walkthrough Controller Banner */}
      {isDemoGuideOpen && (
        <DemoScenarioBar
          currentStep={demoStep}
          onNextStep={handleNextDemoStep}
          onPrevStep={handlePrevDemoStep}
          onResetDemo={handleResetDemo}
          isLoading={isLoading}
        />
      )}

      {/* Main Workspace (3-column layout) */}
      <div className="main-workspace">
        {/* Left Column: Cadastral Hierarchy */}
        <UnitTree
          parcel={parcel}
          units={units}
          selectedUnitId={selectedUnitId}
          onSelectUnit={(id) => {
            setSelectedUnitId(id);
          }}
          hasOverlapDefect={hasOverlapDefect}
        />

        {/* Center Column: 3D Viewport + Bottom Tabs */}
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
          {/* Top 62%: Three.js 3D Cadastral Engine */}
          <div style={{ flex: '1 1 62%', minHeight: 0, position: 'relative' }}>
            <Cadastral3DViewer
              parcel={parcel}
              units={units}
              selectedUnitId={selectedUnitId}
              onSelectUnit={setSelectedUnitId}
              hasOverlapDefect={hasOverlapDefect}
              overlapElevationRange={{ min: 106.0, max: 106.5 }}
            />
          </div>

          {/* Bottom 38%: Governance & Output Workspace */}
          <div
            style={{
              flex: '0 0 38%',
              backgroundColor: 'var(--bg-panel)',
              borderTop: '1px solid var(--border-subtle)',
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden',
            }}
          >
            {/* Tab Navigation Header */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                backgroundColor: 'rgba(14, 23, 38, 0.95)',
                borderBottom: '1px solid var(--border-subtle)',
                padding: '0 12px',
                gap: '4px',
              }}
            >
              <button
                className={`btn btn-sm ${activeTab === 'validation' ? 'btn-primary' : ''}`}
                style={{ borderRadius: '4px 4px 0 0', borderBottom: 'none' }}
                onClick={() => setActiveTab('validation')}
              >
                <AlertTriangle size={12} />
                Validation Issues ({blockerCount})
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
                Human Review & Gate C
              </button>

              <button
                className={`btn btn-sm ${activeTab === 'revisions' ? 'btn-primary' : ''}`}
                style={{ borderRadius: '4px 4px 0 0', borderBottom: 'none' }}
                onClick={() => setActiveTab('revisions')}
              >
                <GitCompare size={12} />
                Revision Comparison ({revisions.length})
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
                Structured Export
              </button>
            </div>

            {/* Tab Body */}
            <div style={{ flex: 1, minHeight: 0, overflow: 'hidden' }}>
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
    </div>
  );
};

export default App;
