import { useMemo } from 'react';
import type { AnalysisData, DiagramData } from '@/types/oci';

interface FlowHighlightResult {
  highlightedNodeIds: Set<string>;
  highlightedEdgeIds: Set<string>;
}

export function useFlowHighlight(
  diagramData: DiagramData | null,
  analysisData: AnalysisData | null,
  selectedNodeId: string | null,
): FlowHighlightResult {
  return useMemo(() => {
    const empty = { highlightedNodeIds: new Set<string>(), highlightedEdgeIds: new Set<string>() };
    if (!selectedNodeId || !diagramData || !analysisData) return empty;

    const nodeIds = new Set<string>();
    const edgeIds = new Set<string>();
    nodeIds.add(selectedNodeId);

    // Find the selected node
    const selectedNode = diagramData.nodes.find(n => n.id === selectedNodeId);
    if (!selectedNode) return empty;
    const type = selectedNode.data?.resource_type || selectedNode.type;

    // Helper: add all edges touching a node
    const addEdgesFor = (nid: string) => {
      for (const e of diagramData.edges) {
        if (e.source === nid || e.target === nid) {
          edgeIds.add(e.id);
          nodeIds.add(e.source);
          nodeIds.add(e.target);
        }
      }
    };

    if (type === 'subnet') {
      // Subnet -> Route Table -> Gateway path
      const rtOcid = analysisData.subnet_to_route_table?.[selectedNodeId];
      if (rtOcid) {
        nodeIds.add(rtOcid);
        addEdgesFor(selectedNodeId); // subnet->RT edge
        addEdgesFor(rtOcid); // RT->gateway edges
      }
    } else if (type === 'route_table') {
      // Route Table -> all subnets using it + all target gateways
      const subnets = analysisData.route_table_to_subnets?.[selectedNodeId] || [];
      for (const sid of subnets) {
        nodeIds.add(sid);
      }
      addEdgesFor(selectedNodeId);
    } else if (type === 'drg') {
      // DRG -> all attachments + DRG route tables + connected VCNs
      addEdgesFor(selectedNodeId);
      // Also highlight DRG route table nodes
      for (const n of diagramData.nodes) {
        if (n.type === 'drgRouteTable') {
          nodeIds.add(n.id);
          addEdgesFor(n.id);
        }
      }
    } else if (['internet_gateway', 'nat_gateway', 'service_gateway'].includes(type)) {
      // Gateway -> all route rules pointing to it + external
      addEdgesFor(selectedNodeId);
    } else if (type === 'vcn') {
      // VCN -> all subnets + all gateways + all route tables + DRG attachment
      for (const n of diagramData.nodes) {
        if (n.parentId === selectedNodeId) {
          nodeIds.add(n.id);
        }
      }
      addEdgesFor(selectedNodeId);
    } else {
      // Default: highlight direct connections
      addEdgesFor(selectedNodeId);
    }

    return { highlightedNodeIds: nodeIds, highlightedEdgeIds: edgeIds };
  }, [selectedNodeId, diagramData, analysisData]);
}
