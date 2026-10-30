export interface CaseSummary {
  case_id: str;
  status: str;
  current_stage: str;
  integrity_status: str;
  evidence_items_count: number;
  verified_findings_count: number;
  total_findings_count: number;
  updated_at: str;
}

export type str = string;

export interface EvidenceItem {
  evidence_id: string;
  original_filename: string;
  artifact_type: string;
  sha256_hash: string;
  size_bytes: number;
  is_read_only: boolean;
  provenance: string;
  source_path?: string;
}

export interface Hypothesis {
  hypothesis_id: string;
  title: string;
  description: string;
  entities: string[];
  confidence_score: number;
  status: 'OPEN' | 'TESTING' | 'CONFIRMED' | 'REFUTED' | 'INCONCLUSIVE';
  resolution_reason?: string;
  supporting_evidence?: any[];
  contradicting_evidence?: any[];
  expected_observations?: string[];
  falsification_tests?: string[];
  competing_hypotheses?: string[];
}

export interface ValidationCheck {
  claim_type: string;
  field_name?: string;
  claimed_value?: any;
  evidence_value?: any;
  matched: boolean;
  contradicted?: boolean;
  evidence_ref?: string;
  detail: string;
}

export interface Finding {
  finding_id: string;
  title: string;
  validation_status: 'VERIFIED' | 'PARTIALLY_VERIFIED' | 'UNVERIFIED' | 'CONTRADICTED' | 'BLOCKED';
  confidence: number;
  checks?: ValidationCheck[];
  corroborating_evidence_refs?: string[];
  contradicting_evidence_refs?: string[];
  rejection_reason?: string;
  claims?: Record<string, any>;
  validated_at?: string;
}

export interface AtomicClaim {
  claim_id: string;
  claim_type: string;
  subject: string;
  predicate: string;
  object: string;
  time_scope?: string;
  validation_rule_id?: string;
  status: string;
  confidence: number;
  explanation: string;
}

export interface GraphNode {
  id: string;
  label: string;
  type: string;
  evidence_ref?: string;
  [key: string]: any;
}

export interface GraphEdge {
  source: string;
  target: string;
  label: string;
  causality?: 'CAUSAL' | 'TEMPORAL' | 'EVIDENTIARY';
  confidence?: number;
  evidence_ref?: string;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface TimelineEvent {
  timestamp: string;
  event: string;
  pid?: number;
  status?: string;
  evidence_ref?: string;
  mitre_technique_id?: string;
  mitre_technique_name?: string;
}

export interface ChainRecord {
  event_index: number;
  timestamp: string;
  stage: string;
  actor: string;
  action: string;
  previous_event_hash: string;
  event_hash: string;
  details?: Record<string, any>;
}

export interface ChainOfCustody {
  case_id: string;
  total_events: number;
  head_hash: string;
  verified: boolean;
  verification_error?: string;
  signature?: {
    algorithm: string;
    signed_head_hash?: string;
    public_key_hex?: string;
    signature_hex?: string;
    signed_at: string;
  };
  records?: ChainRecord[];
}

export interface ModelObservatory {
  nebius_configured: boolean;
  status_label: string;
  base_url: string;
  models: {
    FAST: string;
    BALANCED: string;
    DEEP: string;
  };
  metrics: {
    total_requests: number;
    total_input_tokens: number;
    total_output_tokens: number;
    total_tokens: number;
    estimated_cost_usd: number;
    profile_distribution: Record<string, number>;
  };
  routing_decisions: Array<{
    task: string;
    model: string;
    profile: string;
    rationale: string;
    timestamp: number;
  }>;
}

export interface ConfigResponse {
  environment: string;
  demo_mode: boolean;
  nebius_configured: boolean;
  nebius_endpoint: string;
  fast_model: string;
  balanced_model: string;
  deep_model: string;
}

