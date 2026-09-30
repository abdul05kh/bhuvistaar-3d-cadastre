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
};
