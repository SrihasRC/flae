export type ArbitrationRelationship =
  | "CORROBORATED"
  | "CONTRADICTED"
  | "RECONCILED"
  | "UNRELATED";

export interface EvidenceComparison {
  fact_a_quote: string;
  fact_a_page: number;
  fact_b_quote: string;
  fact_b_page: number;
}

export interface ArbitrationRead {
  arbitration_id: string;
  fact_a_id: string;
  fact_b_id: string;
  workspace_id: string;
  relationship: ArbitrationRelationship;
  divergence_factor?: string | null;
  confidence_score: number;
  reasoning_trace: string;
  evidence_comparison: EvidenceComparison;
  created_at: string;
}

export interface ArbitrationListResponse {
  arbitrations: ArbitrationRead[];
  total: number;
}

export interface CaseExplorerResponse {
  case_1_corroborated: ArbitrationRead[];
  case_2_contradicted: ArbitrationRead[];
  case_3_reconciled: ArbitrationRead[];
}

export interface ContextEnvelope {
  temporal_period?: string | null;
  period_type?: string | null;
  entity_scope?: string | null;
  geography?: string | null;
  accounting_methodology?: string | null;
  additional_qualifiers?: string | null;
}

export interface Evidence {
  verbatim_quote: string;
  page_number: number;
  section_title?: string | null;
}

export interface FactRead {
  fact_id: string;
  document_id: string;
  workspace_id: string;
  subject: string;
  attribute: string;
  value_raw: string;
  value_numeric?: number | null;
  unit?: string | null;
  context_envelope: ContextEnvelope;
  evidence: Evidence;
  created_at: string;
}

export interface FactListResponse {
  facts: FactRead[];
  total: number;
}

export interface Workspace {
  id: string;
  name: string;
  description?: string | null;
  created_at: string;
  document_count: number;
  fact_count?: number;
}

export interface WorkspaceListResponse {
  workspaces: Workspace[];
}

export interface WorkspaceCreate {
  name: string;
  description?: string;
}

export type DocumentStatus = "pending" | "processing" | "complete" | "failed";

export interface DocumentRead {
  id: string;
  filename: string;
  workspace_id: string;
  page_count: number;
  status: DocumentStatus;
  uploaded_at: string;
}

export interface DocumentListResponse {
  documents: DocumentRead[];
}

export interface IngestionJobStatus {
  document_id: string;
  status: DocumentStatus;
  facts_extracted: number;
  error?: string | null;
}

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  database: string;
  vector_store: string;
}
