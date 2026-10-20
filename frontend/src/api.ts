export type EventRecord = {
  event_id: string;
  event_type: string;
  event_time: string;
  observed_time: string;
  host_id?: string | null;
  user_id?: string | null;
  source?: string;
  attributes?: Record<string, unknown>;
};

export type GraphEdge = {
  source_event_id: string;
  target_event_id: string;
  relationship_type: string;
  supporting_evidence: string[];
  contradictory_evidence: string[];
  missing_evidence: string[];
  score: number;
  evidence_strength: string;
  explanation: string;
  alternative_interpretations: string[];
  provenance: string[];
};

export type GraphData = { version: number; nodes: EventRecord[]; edges: GraphEdge[]; rejected_candidates: GraphEdge[]; missing_evidence: string[] };
export type Investigation = { id: string; name: string; description?: string | null; events: EventRecord[]; graph?: GraphData | null };
export type Experiment = { id: string; status: string; scenario_id: string; seed: number; metrics: Record<string, number | string>; configuration: Record<string, unknown> };
export type SyntheticScenario = { scenario_id: string; seed: number; events: EventRecord[]; ground_truth_count: number };

const API_ROOT = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_ROOT}${path}`, { headers: { "Content-Type": "application/json" }, ...init });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed with status ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<{ status: string; persistence: string }>("/health"),
  investigations: () => request<Investigation[]>("/investigations"),
  createInvestigation: (name: string) => request<Investigation>("/investigations", { method: "POST", body: JSON.stringify({ name }) }),
  events: (id: string) => request<EventRecord[]>(`/investigations/${id}/events`),
  timeline: (id: string) => request<EventRecord[]>(`/investigations/${id}/timeline`),
  graph: (id: string) => request<GraphData>(`/investigations/${id}/graph`),
  reconstruct: (id: string) => request<GraphData>(`/investigations/${id}/reconstruct`, { method: "POST" }),
  importEvents: (id: string, events: EventRecord[]) => request<{ investigation_id: string }>(`/investigations/${id}/events`, { method: "POST", body: JSON.stringify({ events }) }),
  syntheticScenario: (seed: number) => request<SyntheticScenario>("/synthetic-scenarios", { method: "POST", body: JSON.stringify({ seed, noise_count: 1 }) }),
  experiments: () => request<Experiment[]>("/experiments"),
  runExperiment: (seed: number) => request<Experiment>("/experiments", { method: "POST", body: JSON.stringify({ seed, noise_count: 1 }) }),
};
