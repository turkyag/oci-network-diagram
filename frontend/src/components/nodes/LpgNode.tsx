import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import { Link } from 'lucide-react';
import type { DiagramNodeData } from '@/types/oci';

type LpgNodeProps = NodeProps & { data: DiagramNodeData };

function LpgNodeComponent({ data }: LpgNodeProps) {
  const peeringStatus = (data.properties?.peering_status as string) || '';
  const isPeered = peeringStatus.toUpperCase() === 'PEERED';

  return (
    <div className="lpg-node">
      <Handle type="target" position={Position.Top} />
      <Handle type="target" position={Position.Left} id="left" />
      <div className="lpg-icon">
        <Link size={16} />
      </div>
      <div className="lpg-info">
        <span className="lpg-name">{data.label}</span>
        {peeringStatus && (
          <span className={`lpg-status badge badge-sm ${isPeered ? 'badge-green' : 'badge-amber'}`}>
            {peeringStatus}
          </span>
        )}
      </div>
      <Handle type="source" position={Position.Bottom} />
      <Handle type="source" position={Position.Right} id="right" />
    </div>
  );
}

export const LpgNode = memo(LpgNodeComponent);
