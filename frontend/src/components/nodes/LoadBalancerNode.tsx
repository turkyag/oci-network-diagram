import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import { Server } from 'lucide-react';
import type { DiagramNodeData } from '@/types/oci';

type LBNodeProps = NodeProps & { data: DiagramNodeData };

function LoadBalancerNodeComponent({ data }: LBNodeProps) {
  const isPrivate = (data.properties?.is_private as boolean) ?? false;
  const variant = isPrivate ? 'private' : 'public';
  const ips = (data.properties?.ip_addresses as string[]) || [];
  const shape = (data.properties?.shape as string) || (data.properties?.shape_name as string) || '';
  const isNlb = data.resource_type === 'network_load_balancer';

  return (
    <div className={`flow-node node-lb ${variant}`}>
      <Handle type="target" position={Position.Top} />
      <Handle type="target" position={Position.Left} id="left" />
      <Server size={18} className={`node-lb-icon ${variant}`} />
      <div className="node-lb-info">
        <div className="node-lb-type">
          {isNlb ? 'Network LB' : 'Load Balancer'}
          {shape ? ` / ${shape}` : ''}
        </div>
        <div className="node-lb-name">{data.label}</div>
        {ips.length > 0 && <div className="node-lb-ip mono">{ips[0]}</div>}
        <span className={`badge badge-sm ${isPrivate ? 'badge-amber' : 'badge-green'}`}>
          {isPrivate ? 'Private' : 'Public'}
        </span>
      </div>
      <Handle type="source" position={Position.Bottom} />
      <Handle type="source" position={Position.Right} id="right" />
    </div>
  );
}

export const LoadBalancerNode = memo(LoadBalancerNodeComponent);
