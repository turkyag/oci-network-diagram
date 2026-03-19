import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import { GitBranch } from 'lucide-react';
import type { DiagramNodeData } from '@/types/oci';

type DrgRouteTableNodeProps = NodeProps & { data: DiagramNodeData };

function DrgRouteTableNodeComponent({ data }: DrgRouteTableNodeProps) {
  const ruleCount = (data.properties?.rule_count as number) ?? 0;
  const isEcmp = (data.properties?.is_ecmp_enabled as boolean) ?? false;

  return (
    <div className="drg-rt-node">
      <Handle type="target" position={Position.Top} />
      <div className="drg-rt-header">
        <GitBranch size={12} className="drg-rt-icon" />
        <span className="drg-rt-name">{data.label}</span>
        <span className="drg-rt-count badge badge-sm badge-cyan">{ruleCount}</span>
      </div>
      {isEcmp && <span className="drg-rt-ecmp badge badge-sm badge-amber">ECMP</span>}
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}

export const DrgRouteTableNode = memo(DrgRouteTableNodeComponent);
