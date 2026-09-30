import {
  ParentParcel,
  SpatialUnit,
  EvidenceSource,
  ValidationSummary,
  SpatialUnitRevision,
  ReviewDecision,
  ApprovalDecision,
  AuditEvent,
  StructuredExport,
} from '../types';

const API_BASE = '/api/v1';

export class ApiError extends Error {
  statusCode: number;
  errorDetail?: any;

  constructor(message: string, statusCode: number, errorDetail?: any) {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
    this.errorDetail = errorDetail;
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorDetail = null;
    let errorMessage = `HTTP ${res.status}: ${res.statusText}`;
    try {
      const data = await res.json();
      errorDetail = data;
      if (data.error && data.error.message) {
        errorMessage = data.error.message;
      } else if (data.detail) {
        errorMessage = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
      }
    } catch {
      // Non-json response
    }
    throw new ApiError(errorMessage, res.status, errorDetail);
  }
  return res.json() as Promise<T>;
}

export const api = {
  // Parcels
  async getParcel(ulpin: string): Promise<ParentParcel> {
    const res = await fetch(`${API_BASE}/parcels/${ulpin}`);
    return handleResponse<ParentParcel>(res);
  },

  async getParcelUnits(ulpin: string): Promise<SpatialUnit[]> {
    const res = await fetch(`${API_BASE}/parcels/${ulpin}/units`);
    return handleResponse<SpatialUnit[]>(res);
  },

  async getParcelEvidence(ulpin: string): Promise<EvidenceSource[]> {
    const res = await fetch(`${API_BASE}/parcels/${ulpin}/evidence`);
    return handleResponse<EvidenceSource[]>(res);
  },

  // Validation
  async getValidation(ulpin: string): Promise<ValidationSummary> {
    const res = await fetch(`${API_BASE}/validation/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ulpin }),
    });
    return handleResponse<ValidationSummary>(res);
  },

  // Units & Revisions
  async getUnitByVuid(vuid: string): Promise<SpatialUnit> {
    const res = await fetch(`${API_BASE}/units/${vuid}`);
    return handleResponse<SpatialUnit>(res);
  },

  async getUnitRevisions(vuid: string): Promise<SpatialUnitRevision[]> {
    const res = await fetch(`${API_BASE}/units/${vuid}/revisions`);
    return handleResponse<SpatialUnitRevision[]>(res);
  },

  // Governance: Review
  async submitReview(
    revisionId: string,
    decision: 'ACCEPT' | 'REQUEST_CORRECTION' | 'REJECT',
    reason: string,
    reviewerId: string = 'REV-OFFICER-001'
  ): Promise<ReviewDecision> {
    const res = await fetch(`${API_BASE}/governance/review/${revisionId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        decision,
        reason,
        reviewer_id: reviewerId,
        actor_context: 'SIMULATED_PROTOTYPE',
      }),
    });
    return handleResponse<ReviewDecision>(res);
  },

  // Governance: Correction
  async submitCorrection(
    revisionId: string,
    z_min: number,
    z_max: number,
    reason: string,
    reviewerId: string = 'REV-OFFICER-001'
  ): Promise<{
    new_revision_id: string;
    predecessor_revision_id: string;
    prototype_vuid: string;
    vuid_full_hash: string;
    validation_run_id: string;
    blocker_count: number;
    can_approve: boolean;
    status: string;
    created_at: string;
  }> {
    const res = await fetch(`${API_BASE}/governance/correction/${revisionId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        reviewer_id: reviewerId,
        reason,
        z_min,
        z_max,
        actor_context: 'SIMULATED_PROTOTYPE',
      }),
    });
    return handleResponse<any>(res);
  },

  // Governance: Approval
  async submitApproval(
    revisionId: string,
    reason: string,
    approverId: string = 'SIM-APPROVER-001'
  ): Promise<ApprovalDecision> {
    const res = await fetch(`${API_BASE}/governance/approval/${revisionId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        approver_id: approverId,
        reason,
        actor_context: 'SIMULATED_PROTOTYPE',
      }),
    });
    return handleResponse<ApprovalDecision>(res);
  },

  // Governance: Rejection
  async submitRejection(
    revisionId: string,
    reason: string,
    approverId: string = 'SIM-APPROVER-001'
  ): Promise<ApprovalDecision> {
    const res = await fetch(`${API_BASE}/governance/rejection/${revisionId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        approver_id: approverId,
        reason,
        actor_context: 'SIMULATED_PROTOTYPE',
      }),
    });
    return handleResponse<ApprovalDecision>(res);
  },

  // Audit
  async getAuditForRevision(revisionId: string): Promise<AuditEvent[]> {
    const res = await fetch(`${API_BASE}/governance/audit/revision/${revisionId}`);
    return handleResponse<AuditEvent[]>(res);
  },

  async getRecentAudits(limit: number = 30): Promise<AuditEvent[]> {
    const res = await fetch(`${API_BASE}/governance/audit/recent?limit=${limit}`);
    return handleResponse<AuditEvent[]>(res);
  },

  // Export
  async getExportForRevision(revisionId: string, exportedBy: string = 'SIM-OFFICER-001'): Promise<StructuredExport> {
    const res = await fetch(`${API_BASE}/governance/export/revision/${revisionId}?exported_by=${exportedBy}`);
    return handleResponse<StructuredExport>(res);
  },

  // Demo Reset
  async resetDemo(scenario: 'defect' | 'clean' = 'defect'): Promise<any> {
    const res = await fetch(`${API_BASE}/demo/reset?scenario=${scenario}`, {
      method: 'POST',
    });
    return handleResponse<any>(res);
  },

  // ==============================================================================
  // SLICE 3 — AI INTELLIGENCE API METHODS
  // ==============================================================================

  async runAiInference(ulpin: string, actorId: string = 'surveyor_officer_01'): Promise<any> {
    const res = await fetch(`${API_BASE}/ai/infer/${ulpin}?actor_id=${actorId}`, {
      method: 'POST',
    });
    return handleResponse<any>(res);
  },

  async getAiCandidates(ulpin: string, status?: string, band?: string): Promise<{ parent_ulpin: string; count: number; candidates: any[] }> {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (band) params.append('confidence_band', band);
    const queryStr = params.toString() ? `?${params.toString()}` : '';
    const res = await fetch(`${API_BASE}/ai/candidates/${ulpin}${queryStr}`);
    return handleResponse<any>(res);
  },

  async getCandidateDetail(candidateId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/ai/candidates/detail/${candidateId}`);
    return handleResponse<any>(res);
  },

  async acceptCandidate(candidateId: string, reviewerId: string, justification: string): Promise<any> {
    const res = await fetch(`${API_BASE}/ai/candidates/${candidateId}/accept`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reviewer_id: reviewerId, justification }),
    });
    return handleResponse<any>(res);
  },

  async rejectCandidate(candidateId: string, reviewerId: string, justification: string): Promise<any> {
    const res = await fetch(`${API_BASE}/ai/candidates/${candidateId}/reject`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reviewer_id: reviewerId, justification }),
    });
    return handleResponse<any>(res);
  },

  async getAiAnomalies(ulpin: string): Promise<{ parent_ulpin: string; count: number; anomalies: any[] }> {
    const res = await fetch(`${API_BASE}/ai/anomalies/${ulpin}`);
    return handleResponse<any>(res);
  },

  async getAiSummary(ulpin: string): Promise<any> {
    const res = await fetch(`${API_BASE}/ai/summary/${ulpin}`);
    return handleResponse<any>(res);
  },

  async getReviewerQueue(ulpin: string): Promise<any> {
    const res = await fetch(`${API_BASE}/ai/queue/${ulpin}`);
    return handleResponse<any>(res);
  },

  async getFactExplanation(candidateId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/ai/explain/${candidateId}`);
    return handleResponse<any>(res);
  },

  async traceOrigin(identifier: string): Promise<any> {
    const res = await fetch(`${API_BASE}/ai/trace-origin/${identifier}`);
    return handleResponse<any>(res);
  },

  async getAiModels(): Promise<any> {
    const res = await fetch(`${API_BASE}/ai/models`);
    return handleResponse<any>(res);
  },

  async runAiEvaluation(): Promise<any> {
    const res = await fetch(`${API_BASE}/ai/evaluate`, {
      method: 'POST',
    });
    return handleResponse<any>(res);
  },

  async loadAiDemoScenario(scenarioKey: string): Promise<any> {
    const res = await fetch(`${API_BASE}/ai/scenarios/${scenarioKey}`, {
      method: 'POST',
    });
    return handleResponse<any>(res);
  },

  // ==============================================================================
  // SLICE 4 — VALIDATION INTELLIGENCE, EXPLAINABILITY & REPRODUCIBILITY METHODS
  // ==============================================================================

  async getValidationDisagreements(ulpin: string): Promise<any> {
    const res = await fetch(`${API_BASE}/ai/disagreements/${ulpin}`);
    return handleResponse<any>(res);
  },

  async explainValidationRun(runId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/ai/explain/validation/${runId}`);
    return handleResponse<any>(res);
  },

  async getReproducibilitySnapshot(targetId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/ai/reproducibility/${targetId}`);
    return handleResponse<any>(res);
  },

  async verifyReproducibility(targetId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/ai/reproducibility/verify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target_id: targetId, recompute_hash: true }),
    });
    return handleResponse<any>(res);
  },

  async compareModels(modelAId: string, modelBId: string, ulpin: string): Promise<any> {
    const res = await fetch(`${API_BASE}/ai/models/compare`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model_a_id: modelAId, model_b_id: modelBId, parent_ulpin: ulpin }),
    });
    return handleResponse<any>(res);
  },

  async getEvaluationHistory(): Promise<any> {
    const res = await fetch(`${API_BASE}/ai/evaluations/history`);
    return handleResponse<any>(res);
  },

  // ==============================================================================
  // SLICE 5 — OPERATIONAL DEPLOYMENT, INTEROPERABILITY & FIELD SIMULATION METHODS
  // ==============================================================================

  async getHealth(): Promise<any> {
    const res = await fetch('/health');
    return handleResponse<any>(res);
  },

  async getSystemReadiness(): Promise<any> {
    const res = await fetch(`${API_BASE}/system/readiness`);
    return handleResponse<any>(res);
  },

  async getSystemIntegrity(): Promise<any> {
    const res = await fetch(`${API_BASE}/system/integrity`);
    return handleResponse<any>(res);
  },

  async bootstrapSystem(): Promise<any> {
    const res = await fetch(`${API_BASE}/system/bootstrap`, {
      method: 'POST',
    });
    return handleResponse<any>(res);
  },

  async getObservabilityMetrics(): Promise<any> {
    const res = await fetch(`${API_BASE}/system/observability`);
    return handleResponse<any>(res);
  },

  async getScenarios(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/demo/scenarios`);
    return handleResponse<any[]>(res);
  },

  async executeScenario(scenarioId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/demo/scenarios/${scenarioId}/execute`, {
      method: 'POST',
    });
    return handleResponse<any>(res);
  },

  async getEvidenceConflicts(ulpin: string): Promise<any[]> {
    const res = await fetch(`${API_BASE}/evidence/conflicts/${ulpin}`);
    return handleResponse<any[]>(res);
  },

  async exportGeoJson(ulpin: string): Promise<any> {
    const res = await fetch(`${API_BASE}/export/geojson/${ulpin}`);
    return handleResponse<any>(res);
  },

  async verifyExportRoundtrip(payload: any): Promise<any> {
    const res = await fetch(`${API_BASE}/export/roundtrip/verify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<any>(res);
  },
};



