import {
  CaseSummary,
  EvidenceItem,
  Hypothesis,
  Finding,
  AtomicClaim,
  GraphData,
  TimelineEvent,
  ChainOfCustody,
  ModelObservatory,
  ConfigResponse,
} from './types';

const BASE_URL = '';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${url}`, options);
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`API Error ${res.status}: ${errorText || res.statusText}`);
  }
  return res.json();
}

export const api = {
  getHealth: () => fetchJson<{ status: string; uptime_seconds: number; timestamp: string }>('/api/health'),
  getConfig: () => fetchJson<ConfigResponse>('/api/config'),
  getModelObservatory: () => fetchJson<ModelObservatory>('/api/models/observatory'),

  // Cases
  getCases: () => fetchJson<CaseSummary[]>('/api/cases'),
  getCase: (caseId: string) => fetchJson<any>(`/api/cases/${caseId}`),
  createCase: (data: { case_id: string; evidence_path: string; description?: string }) =>
    fetchJson<CaseSummary>('/api/cases', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }),

  // Evidence
  getEvidence: (caseId: string) =>
    fetchJson<{ items: EvidenceItem[]; item_count: number; total_bytes: number }>(`/api/cases/${caseId}/evidence`),

  // Investigation Pipeline
  startInvestigation: (caseId: string) =>
    fetchJson<{ case_id: string; success: boolean; status: string; current_stage: string }>(
      `/api/cases/${caseId}/investigate/start`,
      { method: 'POST' }
    ),
  stepInvestigation: (caseId: string) =>
    fetchJson<{ advanced_to?: string; success?: boolean; message?: string }>(
      `/api/cases/${caseId}/investigate/step`,
      { method: 'POST' }
    ),

  // Forensic Outputs
  getHypotheses: (caseId: string) => fetchJson<Hypothesis[]>(`/api/cases/${caseId}/hypotheses`),
  getFindings: (caseId: string) => fetchJson<Finding[]>(`/api/cases/${caseId}/findings`),
  getFindingDetail: (caseId: string, findingId: string) =>
    fetchJson<Finding>(`/api/cases/${caseId}/findings/${findingId}`),
  getAtomicClaims: (caseId: string) => fetchJson<AtomicClaim[]>(`/api/cases/${caseId}/atomic_claims`),
  getGraph: (caseId: string) => fetchJson<any>(`/api/cases/${caseId}/graph`),
  getTimeline: (caseId: string) => fetchJson<TimelineEvent[]>(`/api/cases/${caseId}/timeline`),
  getCustody: (caseId: string) => fetchJson<ChainOfCustody>(`/api/cases/${caseId}/custody`),

  // Report URLs
  getReportHtmlUrl: (caseId: string) => `/api/cases/${caseId}/reports/html`,
  getReportMarkdownUrl: (caseId: string) => `/api/cases/${caseId}/reports/markdown`,
  getReportJsonUrl: (caseId: string) => `/api/cases/${caseId}/reports/json`,
};

