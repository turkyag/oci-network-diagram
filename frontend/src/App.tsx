import { useState, useCallback } from 'react';
import { Shield } from 'lucide-react';
import { Sidebar } from '@/components/Sidebar';
import { DiagramCanvas } from '@/components/DiagramCanvas';
import { DetailPanel } from '@/components/DetailPanel';
import { SearchBar } from '@/components/SearchBar';
import { useTopology } from '@/hooks/useTopology';
import { useFlowHighlight } from '@/hooks/useFlowHighlight';
import type { DiagramNodeData } from '@/types/oci';

export default function App() {
  const {
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
  } = useTopology();

  const [selectedNode, setSelectedNode] = useState<DiagramNodeData | null>(null);
  const [highlightedNodes, setHighlightedNodes] = useState<string[]>([]);

  const selectedNodeId = selectedNode?.resource_id || null;
  const { highlightedNodeIds, highlightedEdgeIds } = useFlowHighlight(diagramData, analysisData, selectedNodeId);

  const handleNodeClick = useCallback((nodeData: DiagramNodeData) => {
    setSelectedNode(nodeData);
  }, []);

  const handleCloseDetail = useCallback(() => {
    setSelectedNode(null);
  }, []);

  const handleCanvasClick = useCallback(() => {
    setSelectedNode(null);
  }, []);

  return (
    <div className="app-layout">
      <Sidebar
        topologies={topologies}
        selectedId={selectedId}
        topologyDetail={topologyDetail}
        diagramData={diagramData}
        loading={loading}
        onSelect={selectTopology}
      />

      <div className="main-area">
        <div className="toolbar">
          <SearchBar
            nodes={diagramData?.nodes || []}
            onHighlight={(ids) => setHighlightedNodes(ids)}
          />
          <div className="toolbar-separator" />
          <button
            className={`toolbar-btn ${showSecurity ? 'active' : ''}`}
            onClick={toggleSecurity}
            title={showSecurity ? 'Hide Security' : 'Show Security'}
          >
            <Shield size={14} />
            Security
          </button>
        </div>

        <DiagramCanvas
          diagramData={diagramData}
          analysisData={analysisData}
          showSecurity={showSecurity}
          loading={diagramLoading}
          error={error}
          hasSelection={selectedId !== null}
          onNodeClick={handleNodeClick}
          highlightedNodes={highlightedNodes}
          highlightedNodeIds={highlightedNodeIds}
          highlightedEdgeIds={highlightedEdgeIds}
          onPaneClick={handleCanvasClick}
        />
      </div>

      {selectedNode && (
        <DetailPanel
          data={selectedNode}
          analysisData={analysisData}
          onClose={handleCloseDetail}
        />
      )}
    </div>
  );
}
