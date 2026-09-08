import {
  ArbitrationListResponse,
  CaseExplorerResponse,
  DocumentListResponse,
  DocumentRead,
  FactListResponse,
  FactRead,
  HealthResponse,
  IngestionJobStatus,
  Workspace,
  WorkspaceCreate,
  WorkspaceListResponse,
} from "./types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  (typeof window !== "undefined" ? "" : "http://localhost:8000");

async function request<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers = new Headers(options?.headers || {});

  if (!headers.has("Content-Type") && !(options?.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorMessage = `API Error ${response.status}: ${response.statusText}`;
    try {
      const errorData = await response.json();
      if (errorData.detail) {
        errorMessage =
          typeof errorData.detail === "string"
            ? errorData.detail
            : JSON.stringify(errorData.detail);
      }
    } catch {
      // no JSON body
    }
    throw new Error(errorMessage);
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

// Health Check
export async function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/health");
}

// Workspaces
export async function listWorkspaces(): Promise<WorkspaceListResponse> {
  return request<WorkspaceListResponse>("/api/v1/workspaces");
}

export async function createWorkspace(
  data: WorkspaceCreate
): Promise<Workspace> {
  return request<Workspace>("/api/v1/workspaces", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getWorkspace(workspaceId: string): Promise<Workspace> {
  return request<Workspace>(`/api/v1/workspaces/${workspaceId}`);
}

export async function deleteWorkspace(workspaceId: string): Promise<void> {
  return request<void>(`/api/v1/workspaces/${workspaceId}`, {
    method: "DELETE",
  });
}

// Documents
export async function listDocuments(
  workspaceId: string
): Promise<DocumentListResponse> {
  return request<DocumentListResponse>(
    `/api/v1/workspaces/${workspaceId}/documents`
  );
}

export async function uploadDocument(
  workspaceId: string,
  file: File
): Promise<DocumentRead> {
  const formData = new FormData();
  formData.append("file", file);

  return request<DocumentRead>(
    `/api/v1/workspaces/${workspaceId}/documents`,
    {
      method: "POST",
      body: formData,
    }
  );
}

export async function getDocumentStatus(
  workspaceId: string,
  documentId: string
): Promise<IngestionJobStatus> {
  return request<IngestionJobStatus>(
    `/api/v1/workspaces/${workspaceId}/documents/${documentId}/status`
  );
}

export async function deleteDocument(
  workspaceId: string,
  documentId: string
): Promise<void> {
  return request<void>(
    `/api/v1/workspaces/${workspaceId}/documents/${documentId}`,
    {
      method: "DELETE",
    }
  );
}

// Facts
export interface FactFilterParams {
  document_id?: string;
  subject?: string;
  attribute?: string;
  query?: string;
  skip?: number;
  limit?: number;
}

export async function listFacts(
  workspaceId: string,
  params?: FactFilterParams
): Promise<FactListResponse> {
  const query = new URLSearchParams();
  if (params?.document_id) query.set("document_id", params.document_id);
  if (params?.subject) query.set("subject", params.subject);
  if (params?.attribute) query.set("attribute", params.attribute);
  if (params?.query) query.set("query", params.query);
  if (params?.skip !== undefined) query.set("skip", params.skip.toString());
  if (params?.limit !== undefined) query.set("limit", params.limit.toString());

  const qs = query.toString();
  return request<FactListResponse>(
    `/api/v1/workspaces/${workspaceId}/facts${qs ? `?${qs}` : ""}`
  );
}

export async function getFact(
  workspaceId: string,
  factId: string
): Promise<FactRead> {
  return request<FactRead>(
    `/api/v1/workspaces/${workspaceId}/facts/${factId}`
  );
}

// Arbitration
export interface ArbitrationFilterParams {
  relationship?: string;
  min_confidence?: number;
  skip?: number;
  limit?: number;
}

export async function listArbitrations(
  workspaceId: string,
  params?: ArbitrationFilterParams
): Promise<ArbitrationListResponse> {
  const query = new URLSearchParams();
  if (params?.relationship) query.set("relationship", params.relationship);
  if (params?.min_confidence !== undefined)
    query.set("min_confidence", params.min_confidence.toString());
  if (params?.skip !== undefined) query.set("skip", params.skip.toString());
  if (params?.limit !== undefined)
    query.set("limit", params.limit.toString());

  const qs = query.toString();
  return request<ArbitrationListResponse>(
    `/api/v1/workspaces/${workspaceId}/arbitration${qs ? `?${qs}` : ""}`
  );
}

export async function triggerArbitration(
  workspaceId: string,
  forceRerun: boolean = false
): Promise<{ job_id: string; message: string; status: string }> {
  return request<{ job_id: string; message: string; status: string }>(
    `/api/v1/workspaces/${workspaceId}/arbitration/run`,
    {
      method: "POST",
      body: JSON.stringify({ force_rerun: forceRerun }),
    }
  );
}

export async function getArbitrationCases(
  workspaceId: string
): Promise<CaseExplorerResponse> {
  return request<CaseExplorerResponse>(
    `/api/v1/workspaces/${workspaceId}/arbitration/cases`
  );
}
