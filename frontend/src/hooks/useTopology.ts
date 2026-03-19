import { useState, useEffect, useCallback } from 'react';
import type { TopologySummary, TopologyDetail, DiagramData, AnalysisData } from '@/types/oci';
import * as api from '@/services/api';

interface UseTopologyReturn {
  topologies: TopologySummary[];
  selectedId: number | null;
  topologyDetail: TopologyDetail | null;
  diagramData: DiagramData | null;
  analysisData: AnalysisData | null;
  loading: boolean;
  diagramLoading: boolean;
  error: string | null;
  showSecurity: boolean;
  selectTopology: (id: number) => void;
  toggleSecurity: () => void;
}

export function useTopology(): UseTopologyReturn {
  const [topologies, setTopologies] = useState<TopologySummary[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [topologyDetail, setTopologyDetail] = useState<TopologyDetail | null>(null);
  const [diagramData, setDiagramData] = useState<DiagramData | null>(null);
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);
  const [loading, setLoading] = useState(true);
  const [diagramLoading, setDiagramLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSecurity, setShowSecurity] = useState(false);

  const refreshTopologies = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.fetchTopologies();
      setTopologies(data);

      if (data.length > 0) {
        setSelectedId((prev) => {
          if (prev && data.some((t) => t.id === prev)) return prev;
          return data[0].id;
        });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch topologies');
    } finally {
      setLoading(false);
    }
  }, []);

  const refreshDiagram = useCallback(async () => {
    if (!selectedId) return;
    try {
      setDiagramLoading(true);
      setError(null);
      const [detail, diagram, analysis] = await Promise.all([
        api.fetchTopology(selectedId),
        api.fetchDiagram(selectedId),
        api.fetchAnalysis(selectedId).catch(() => null),
      ]);
      setTopologyDetail(detail);
      setDiagramData(diagram);
      setAnalysisData(analysis);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load diagram');
    } finally {
      setDiagramLoading(false);
    }
  }, [selectedId]);

  useEffect(() => { refreshTopologies(); }, [refreshTopologies]);

  useEffect(() => {
    if (selectedId) {
      refreshDiagram();
    } else {
      setTopologyDetail(null);
      setDiagramData(null);
      setAnalysisData(null);
    }
  }, [selectedId, refreshDiagram]);

  const selectTopology = useCallback((id: number) => {
    setSelectedId(id);
  }, []);

  const toggleSecurity = useCallback(() => {
    setShowSecurity((prev) => !prev);
  }, []);

  return {
    topologies,
    selectedId,
    topologyDetail,
    diagramData,
    analysisData,
    loading,
    diagramLoading,
    error,
    showSecurity,
    selectTopology,
    toggleSecurity,
  };
}
