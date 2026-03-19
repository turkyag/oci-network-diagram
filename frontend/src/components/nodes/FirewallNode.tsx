import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import { ShieldAlert } from 'lucide-react';
import type { DiagramNodeData } from '@/types/oci';

type FirewallNodeProps = NodeProps & { data: DiagramNodeData };

function FirewallNodeComponent({ data }: FirewallNodeProps) {
  const policyId = (data.properties?.policy_id as string) || '';
  return (
    <div className="firewall-node">
      <Handle type="target" position={Position.Top} />
      <div className="firewall-icon">
        <ShieldAlert size={18} />
      </div>
      <div className="firewall-info">
        <span className="firewall-badge">Firewall</span>
        <span className="firewall-name">{data.label}</span>
        {policyId && (
          <span className="firewall-policy mono">{policyId}</span>
        )}
      </div>
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}

export const FirewallNode = memo(FirewallNodeComponent);
