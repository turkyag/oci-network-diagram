import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import { GitBranch } from 'lucide-react';
import type { DiagramNodeData } from '@/types/oci';

type DrgNodeProps = NodeProps & { data: DiagramNodeData };

function DrgNodeComponent({ data }: DrgNodeProps) {
  const attachCount = (data.properties?.attachment_count as number) ?? 0;
  const rpcCount = (data.properties?.rpc_count as number) ?? 0;

  return (
    <div className="drg-node">
      <Handle type="target" position={Position.Top} />
      <Handle type="target" position={Position.Left} id="left" />
      <div className="drg-icon">
        <GitBranch size={24} />
      </div>
      <div className="drg-info">
        <span className="drg-badge">DRG</span>
        <span className="drg-name">{data.label}</span>
        <div className="drg-stats">
          {attachCount > 0 && <span className="drg-stat">{attachCount} attachments</span>}
          {attachCount > 0 && rpcCount > 0 && <span className="drg-stat-sep">&middot;</span>}
          {rpcCount > 0 && <span className="drg-stat">{rpcCount} RPCs</span>}
        </div>
      </div>
      <Handle type="source" position={Position.Bottom} />
      <Handle type="source" position={Position.Right} id="right" />
    </div>
  );
}

export const DrgNode = memo(DrgNodeComponent);
