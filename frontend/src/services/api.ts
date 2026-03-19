import type {
  TopologySummary,
  TopologyDetail,
  DiagramData,
  AnalysisData,
} from '@/types/oci';

const BASE_URL = import.meta.env.VITE_API_URL || '';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${BASE_URL}${path}`;
  const res = await fetch(url, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...options?.headers },
  });

  if (!res.ok) {
    let message = `Request failed: ${res.status}`;
    try {
      const body = await res.json();
      if (body.detail) message = body.detail;
    } catch { /* ignore */ }
    throw new Error(message);
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

export const fetchTopologies = () =>
  request<TopologySummary[]>('/api/topologies');

export const fetchTopology = (id: number) =>
  request<TopologyDetail>(`/api/topologies/${id}`);

export const fetchDiagram = (id: number) =>
  request<DiagramData>(`/api/topologies/${id}/diagram`);

export const fetchAnalysis = (id: number) =>
  request<AnalysisData>(`/api/topologies/${id}/analysis`);
