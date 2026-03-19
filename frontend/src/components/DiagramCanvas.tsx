import { useCallback, useEffect, useMemo, useRef } from 'react';
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  BackgroundVariant,
  useNodesState,
  useEdgesState,
  type Node,
  type Edge,
  type NodeMouseHandler,
  type NodeDragHandler,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Network, AlertTriangle } from 'lucide-react';
import { nodeTypes } from './nodes';
import { WarningsBanner } from './WarningsBanner';
import { Legend } from './Legend';
import { useZoomLevel } from '@/hooks/useZoomLevel';
import type { DiagramData, DiagramNodeData, AnalysisData } from '@/types/oci';

interface DiagramCanvasProps {
  diagramData: DiagramData | null;
  analysisData?: AnalysisData | null;
  showSecurity?: boolean;
  loading: boolean;
  error: string | null;
  hasSelection: boolean;
  onNodeClick: (nodeData: DiagramNodeData) => void;
  highlightedNodes?: string[];
  highlightedNodeIds?: Set<string>;
  highlightedEdgeIds?: Set<string>;
  onPaneClick?: () => void;
}

const defaultEdgeOptions = {
  style: { strokeWidth: 1.5 },
};

export function DiagramCanvas({
  diagramData,
  loading,
  error,
  hasSelection,
  onNodeClick,
  highlightedNodes,
  highlightedNodeIds,
  highlightedEdgeIds,
  onPaneClick,
}: DiagramCanvasProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const { zoomLevel, onViewportChange } = useZoomLevel();

  const warnings = diagramData?.warnings || [];

  useEffect(() => {
    if (diagramData) {
      setNodes(diagramData.nodes as Node[]);
      setEdges(
        diagramData.edges.map((e) => ({
          ...e,
          animated: e.animated ?? false,
          style: {
            strokeWidth: 1.5,
            ...e.style,
          },
        })) as Edge[]
      );
    } else {
      setNodes([]);
      setEdges([]);
    }
  }, [diagramData, setNodes, setEdges]);

  const styledNodes = useMemo(() => {
    const hasFlowHighlight = highlightedNodeIds && highlightedNodeIds.size > 0;
    const hasSearchHighlight = highlightedNodes && highlightedNodes.length > 0;
    if (!hasFlowHighlight && !hasSearchHighlight) return nodes;
    return nodes.map(n => {
      const isHighlighted = hasFlowHighlight
        ? highlightedNodeIds.has(n.id)
        : highlightedNodes!.includes(n.id);
      return {
        ...n,
        style: {
          ...n.style,
          opacity: isHighlighted ? 1 : 0.15,
          transition: 'opacity 0.3s ease',
        },
      };
    });
  }, [nodes, highlightedNodes, highlightedNodeIds]);

  const styledEdges = useMemo(() => {
    const hasHighlight = highlightedEdgeIds && highlightedEdgeIds.size > 0;
    if (!hasHighlight) return edges;
    return edges.map(e => ({
      ...e,
      style: {
        ...e.style,
        opacity: highlightedEdgeIds.has(e.id) ? 1 : 0.1,
        strokeWidth: highlightedEdgeIds.has(e.id) ? 2.5 : 1,
        transition: 'opacity 0.3s ease',
      },
    }));
  }, [edges, highlightedEdgeIds]);

  const handleNodeClick: NodeMouseHandler = useCallback(
    (_, node) => {
      if (node.data) {
        onNodeClick(node.data as DiagramNodeData);
      }
    },
    [onNodeClick]
  );

  // Track compartment drag to move all member nodes together
  const dragStartPos = useRef<{ x: number; y: number } | null>(null);

  const handleNodeDragStart: NodeDragHandler = useCallback((_, node) => {
    if (node.type === 'compartment') {
      dragStartPos.current = { x: node.position.x, y: node.position.y };
    }
  }, []);

  const handleNodeDragStop: NodeDragHandler = useCallback((_, node) => {
    if (node.type !== 'compartment' || !dragStartPos.current) return;

    const startX = dragStartPos.current.x;
    const startY = dragStartPos.current.y;
    const dx = node.position.x - startX;
    const dy = node.position.y - startY;
    dragStartPos.current = null;

    if (Math.abs(dx) < 1 && Math.abs(dy) < 1) return;

    // Find the compartment's compartment_id
    const compId = (node.data as Record<string, unknown>)?.resource_id as string;
    if (!compId) return;

    // Move all nodes belonging to this compartment:
    // 1. Resource nodes (VCN, DRG, gateway, RT) matched by compartment_id
    // 2. Sub-compartment nodes matched by parent compartment relationship
    // 3. Child nodes (subnets) move automatically via React Flow parentId
    setNodes((prev) =>
      prev.map((n) => {
        if (n.id === node.id) return n; // compartment itself already moved
        if (n.type === 'external') return n;
        if (n.parentId) return n; // subnets move with VCN

        const data = n.data as Record<string, unknown> | undefined;
        const props = data?.properties as Record<string, unknown> | undefined;
        const nodeCompId = props?.compartment_id as string;

        // Move resource nodes that belong to this compartment
        if (n.type !== 'compartment' && nodeCompId === compId) {
          return { ...n, position: { x: n.position.x + dx, y: n.position.y + dy } };
        }

        // Move sub-compartment nodes (their resources have a different comp_id,
        // but they're visually inside this parent compartment)
        // Check if this compartment's bounding box was inside the dragged compartment
        if (n.type === 'compartment') {
          const nStyle = n.style as Record<string, number> | undefined;
          const nw = nStyle?.width || 0;
          const compStyle = node.style as Record<string, number> | undefined;
          const pw = compStyle?.width || 0;
          // Simple check: if this compartment was inside the dragged one's original bounds
          const wasInside = n.position.x >= startX - 50 &&
            n.position.x + nw <= startX + pw + 50;
          if (wasInside) {
            return { ...n, position: { x: n.position.x + dx, y: n.position.y + dy } };
          }
        }

        return n;
      })
    );
  }, [setNodes]);

  const fitViewOptions = useMemo(
    () => ({ padding: 0.15, duration: 400 }),
    []
  );

  // --- Empty / Loading / Error states ---
  if (!hasSelection) {
    return (
      <div className="canvas-area">
        <div className="empty-state">
          <Network size={48} className="empty-state-icon" />
          <h3>OCI Network Explorer</h3>
          <p>No network data found. Sync your OCI infrastructure to visualize it.</p>
          <code className="empty-state-cmd">docker compose run --rm oci-sync sync.py --config-file /oci/config</code>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="canvas-area">
        <div className="loading-container">
          <div className="spinner" />
          <span className="loading-text">Rendering diagram...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="canvas-area">
        <div className="error-state">
          <AlertTriangle size={40} className="error-state-icon" />
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (!diagramData || (diagramData.nodes.length === 0 && diagramData.edges.length === 0)) {
    return (
      <div className="canvas-area">
        <div className="empty-state">
          <Network size={48} className="empty-state-icon" />
          <h3>OCI Network Explorer</h3>
          <p>No network data found. Sync your OCI infrastructure to visualize it.</p>
          <code className="empty-state-cmd">docker compose run --rm oci-sync sync.py --config-file /oci/config</code>
        </div>
      </div>
    );
  }

  return (
    <div className={`canvas-area zoom-${zoomLevel}`}>
      {warnings.length > 0 && <WarningsBanner warnings={warnings} />}
      <ReactFlow
        nodes={styledNodes}
        edges={styledEdges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={handleNodeClick}
        onNodeDragStart={handleNodeDragStart}
        onNodeDragStop={handleNodeDragStop}
        onPaneClick={onPaneClick}
        onViewportChange={onViewportChange}
        nodeTypes={nodeTypes}
        defaultEdgeOptions={defaultEdgeOptions}
        fitView
        fitViewOptions={fitViewOptions}
        minZoom={0.1}
        maxZoom={2}
        proOptions={{ hideAttribution: true }}
      >
        <Background
          variant={BackgroundVariant.Dots}
          gap={20}
          size={1}
          color="rgba(30, 41, 59, 0.5)"
        />
        <MiniMap
          nodeStrokeWidth={1}
          pannable
          zoomable
          nodeColor={(node) => {
            if (node.type === 'compartment') return 'transparent';
            if (node.type === 'vcn') return '#06b6d4';
            if (node.type === 'subnet') return '#1e293b';
            if (node.type === 'drg') return '#3b82f6';
            if (node.type === 'gateway') return '#22c55e';
            if (node.type === 'routeTable') return '#475569';
            return '#334155';
          }}
          nodeStrokeColor={(node) => {
            if (node.type === 'compartment') return 'transparent';
            return '#475569';
          }}
          style={{
            backgroundColor: '#0a0e17',
          }}
        />
        <Controls showInteractive={false} />
      </ReactFlow>
      <Legend />
    </div>
  );
}
