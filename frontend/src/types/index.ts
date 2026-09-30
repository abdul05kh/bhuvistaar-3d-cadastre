export type SemanticType = 'PARCEL' | 'BUILDING' | 'FLOOR' | 'ROOM' | 'AIR_SPACE' | 'UTILITY';

export type UnitStatus =
  | 'DRAFT'
  | 'GENERATED'
  | 'VALIDATED'
  | 'UNDER_REVIEW'
  | 'CORRECTED'
  | 'REVALIDATED'
  | 'APPROVED'
  | 'REJECTED';

export type Severity = 'BLOCKER' | 'ERROR' | 'WARNING' | 'INFO';

export interface GeoJSONPolygon {
  type: 'Polygon';
  coordinates: number[][][];
}

export interface ParentParcel {
  id: string;
  ulpin: string;
  crs: string;
  storage_srid: number;
  area_sqm: number;
  status: string;
  geometry: GeoJSONPolygon;
  metadata: Record<string, any>;
  created_at: string;
}

export interface SpatialUnit {
  id: string;
  prototype_vuid: string;
  parent_ulpin: string;
  semantic_type: SemanticType;
  level_code: string;
  z_min: float;
  z_max: float;
  height_m: float;
  footprint_area_sqm: float;
  volume_cbm: float;
  centroid_x: float;
  centroid_y: float;
  centroid_z: float;
  confidence: string;
  generation_method: string;
  vuid_algorithm_version: string;
  vuid_full_hash: string;
  source_ids: string[];
  status: UnitStatus;
  footprint_geom: GeoJSONPolygon;
  polyhedron_wkt?: string | null;
  active_revision_id?: string | null;
  revision_number?: number;
  created_at: string;
}

export type float = number;

export interface ValidationIssue {
  id: string;
  run_id: string;
  rule_code: string;
  severity: Severity;
  object_type: string;
  object_id: string;
  passed: boolean;
  message: string;
  measured_value?: Record<string, any> | null;
  threshold?: Record<string, any> | null;
  suggested_action?: string | null;
  created_at: string;
}

export interface ValidationSummary {
  run_id: string;
  ulpin: string;
  timestamp: string;
  rules_evaluated: number;
  passed_rules: number;
  failed_rules: number;
  blocker_count: number;
  error_count: number;
  warning_count: number;
  can_approve: boolean;
  issues: ValidationIssue[];
}

export interface EvidenceSource {
  id: string;
  parent_ulpin: string;
  evidence_type: string;
  provider: string;
  source_reference: string;
  checksum: string;
  crs?: string | null;
  acquisition_time?: string | null;
  processing_version: string;
  metadata: Record<string, any>;
  created_at: string;
}

export interface SpatialUnitRevision {
  id: string;
  revision_number: number;
  prototype_vuid: string;
  level_code: string;
  z_min: number;
  z_max: number;
  status: UnitStatus;
  predecessor_revision_id?: string | null;
  created_by: string;
  created_at: string;
}

export interface ReviewDecision {
  id: string;
  revision_id: string;
  reviewer_id: string;
  decision: 'ACCEPT' | 'REQUEST_CORRECTION' | 'REJECT';
  reason: string;
  actor_context: string;
  referenced_validation_run_id?: string | null;
  created_at: string;
}

export interface ApprovalDecision {
  id: string;
  revision_id: string;
  approver_id: string;
  status: 'APPROVED' | 'REJECTED';
  reason: string;
  referenced_validation_run_id: string;
  referenced_review_id: string;
}

export interface AuditEvent {
  id: string;
  timestamp: string;
  actor_id: string;
  authorization_mode: string;
  action: string;
  entity_type: string;
  entity_id: string;
  revision_id?: string | null;
  previous_state?: string | null;
  new_state?: string | null;
  reason?: string | null;
  correlation_id?: string | null;
  metadata?: Record<string, any>;
}

export interface StructuredExport {
  export_metadata: {
    schema_version: string;
    exported_at: string;
    exported_by: string;
    authorization_mode: string;
    disclaimer: string;
  };
  parcel: {
    ulpin: string;
    crs: string;
    storage_srid: number;
    area_sqm: number;
    geometry: GeoJSONPolygon;
  };
  spatial_unit: {
    unit_id: string;
    level_code: string;
    semantic_type: string;
  };
  spatial_unit_revision: {
    revision_id: string;
    revision_number: number;
    predecessor_revision_id?: string | null;
    status: string;
    created_by: string;
    created_at: string;
  };
  vuid: {
    prototype_vuid: string;
    vuid_full_hash: string;
    vuid_display_token: string;
    vuid_algorithm_version: string;
    prototype_disclaimer: string;
  };
  geometry: {
    footprint: GeoJSONPolygon;
    polyhedron_wkt?: string | null;
  };
  elevation: {
    z_min: number;
    z_max: number;
    height_m: number;
    footprint_area_sqm: number;
    volume_cbm: number;
    centroid: { x: number; y: number; z: number };
  };
  evidence: Array<{
    id: string;
    evidence_type: string;
    provider: string;
    source_reference: string;
    checksum: string;
    checksum_algorithm: string;
    checksum_valid: boolean;
  }>;
  provenance: {
    is_verified: boolean;
    generation_method: string;
    generation_method_version: string;
    vuid_algorithm_version: string;
    predecessor_vuid?: string | null;
  };
  validation: {
    status: string;
    run_id: string;
    validator_version: string;
    rules_evaluated: number;
    blocker_count: number;
    warning_count: number;
    issues: any[];
  };
  review: {
    review_id?: string;
    reviewer_id: string;
    decision: string;
    reason: string;
    timestamp?: string;
  };
  approval: {
    approval_id?: string;
    status: string;
    approver_id: string;
    reason: string;
  };
  audit_summary: {
    total_events: number;
    events: Array<{
      action: string;
      actor_id: string;
      timestamp: string;
      previous_state?: string | null;
      new_state?: string | null;
    }>;
  };
}

// ==============================================================================
// SLICE 3 — AI INTELLIGENCE TYPES
// ==============================================================================

export type CandidateStatus = 'AI_CANDIDATE' | 'ACCEPTED' | 'REJECTED' | 'CORRECTED';

export interface AICandidate {
  candidate_id: string;
  parent_ulpin: string;
  level_code: string;
  semantic_type: string;
  z_min: number;
  z_max: number;
  confidence: number;
  confidence_band: 'HIGH' | 'MEDIUM' | 'LOW';
  status: CandidateStatus;
  source_evidence_ids: string[];
  reason_codes: string[];
  footprint_geojson: GeoJSONPolygon;
  footprint_area_sqm: number;
  volume_cbm: number;
  centroid: [number, number, number];
  model: {
    name: string;
    version: string;
  };
  governed_unit_id?: string | null;
  governed_revision_id?: string | null;
  rejection_reason?: string | null;
  reviewed_by?: string | null;
  reviewed_at?: string | null;
  created_at?: string | null;
}

export interface AIAnomaly {
  anomaly_id: string;
  parent_ulpin: string;
  anomaly_type: string;
  severity: Severity;
  affected_units: string[];
  evidence_ids: string[];
  confidence: number;
  reason_codes: string[];
  recommended_action: string;
  model: {
    name: string;
    version: string;
  };
  resolved: boolean;
  created_at?: string | null;
}

export interface AIAssistanceSummary {
  parent_ulpin: string;
  total_candidates: number;
  high_confidence_count: number;
  medium_confidence_count: number;
  low_confidence_count: number;
  anomalies_count: number;
  blocker_count: number;
  evidence_conflicts_count: number;
  review_required_count: number;
  model_name: string;
  model_version: string;
  inference_timestamp: string;
  operational_disclaimer: string;
}

export interface ReviewerQueueItem {
  priority: number;
  item_type: 'BLOCKER' | 'ANOMALY' | 'CANDIDATE_REVIEW';
  identifier: string;
  title: string;
  severity: Severity;
  confidence?: number | null;
  reason: string;
  recommended_action: string;
  affected_level?: string | null;
}

export interface ReviewerQueueResponse {
  parent_ulpin: string;
  total_items: number;
  items: ReviewerQueueItem[];
}

export interface FactBasedExplanation {
  target_id: string;
  target_type: string;
  summary: string;
  evidence_basis: string[];
  geometric_facts: string[];
  validation_status: string;
  governance_status: string;
  disclaimer: string;
}

export interface TraceOriginNode {
  step: number;
  stage: string;
  title: string;
  identifier: string;
  status: string;
  timestamp?: string | null;
  actor: string;
  details: Record<string, any>;
}

export interface TraceOriginResponse {
  target_identifier: string;
  parent_ulpin: string;
  lineage_path: TraceOriginNode[];
  is_authoritative: boolean;
  provenance_hash?: string | null;
}

export interface ModelCard {
  model_id: string;
  name: string;
  version: string;
  task: string;
  status: string;
  description: string;
  architecture: string;
  inputs: string[];
  outputs: string[];
  training_data_disclosure: string;
  known_limitations: string[];
  metrics: Record<string, any>;
  intended_use: string;
  prohibited_use: string;
  license: string;
  disclaimer: string;
}

// Slice 4 Validation Intelligence & Reproducibility Types
export interface DisagreementRecord {
  disagreement_id: string;
  parent_ulpin: string;
  candidate_id?: string | null;
  level_code?: string | null;
  disagreement_type: string;
  severity: string;
  ai_confidence: number;
  validation_status: string;
  human_decision?: string | null;
  rule_codes: string[];
  explanation: string;
  measured_values?: Record<string, any> | null;
  thresholds?: Record<string, any> | null;
  model: { name: string; version: string };
  ruleset_version: string;
  created_at?: string | null;
}

export interface DisagreementListResponse {
  parent_ulpin: string;
  total_disagreements: number;
  blocker_count: number;
  warning_count: number;
  consistent_count: number;
  disagreements: DisagreementRecord[];
}

export interface ReproducibilitySnapshot {
  snapshot_id: string;
  parent_ulpin: string;
  target_type: string;
  target_id: string;
  revision_id?: string | null;
  reproducibility_status: 'REPRODUCIBLE' | 'PARTIALLY_REPRODUCIBLE' | 'NOT_REPRODUCIBLE';
  input_evidence_hashes: string[];
  geometry_geojson: Record<string, any>;
  crs: string;
  generation_method: string;
  model: { name: string; version: string };
  model_config_hash: string;
  validation_ruleset_version: string;
  software_commit: string;
  snapshot_hash: string;
  can_reproduce: boolean;
  verification_report: Record<string, any>;
  created_at?: string | null;
}

export interface ModelComparisonMetric {
  metric_name: string;
  model_a_value: any;
  model_b_value: any;
  delta: any;
  observation: string;
}

export interface ModelComparisonResponse {
  parent_ulpin: string;
  model_a: Record<string, any>;
  model_b: Record<string, any>;
  metrics: ModelComparisonMetric[];
  summary_notes: string;
  limitations_disclaimer: string;
}

export interface ValidationExplanationItem {
  rule_code: string;
  rule_family: string;
  rule_version: string;
  ruleset_version: string;
  severity: string;
  lower_unit?: string;
  upper_unit?: string;
  measured_values?: Record<string, any>;
  thresholds?: Record<string, any>;
  detailed_explanation: string;
  suggested_action: string;
  governance_implication: string;
}

export interface ValidationExplanationResponse {
  run_id: string;
  parent_ulpin: string;
  validator_version: string;
  ruleset_version: string;
  rules_evaluated: number;
  blocker_count: number;
  can_approve: boolean;
  explanations: ValidationExplanationItem[];
}


