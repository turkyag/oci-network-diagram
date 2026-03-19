import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import { Globe, ArrowUpDown, Database } from 'lucide-react';
import type { DiagramNodeData } from '@/types/oci';

type GatewayNodeProps = NodeProps & { data: DiagramNodeData };

const GATEWAY_CONFIG: Record<string, { icon: typeof Globe; className: string; label: string }> = {
  internet_gateway: { icon: Globe, className: 'gw-igw', label: 'IGW' },
  nat_gateway: { icon: ArrowUpDown, className: 'gw-nat', label: 'NAT' },
  service_gateway: { icon: Database, className: 'gw-sgw', label: 'SGW' },
};

function GatewayNodeComponent({ data }: GatewayNodeProps) {
  const gwType = (data.properties?.gateway_type as string) || 'internet_gateway';
  const config = GATEWAY_CONFIG[gwType] || GATEWAY_CONFIG.internet_gateway;
  const Icon = config.icon;

  return (
    <div className={`gateway-node ${config.className}`}>
      <Handle type="target" position={Position.Top} />
      <Handle type="source" position={Position.Top} id="top-source" />
      <div className="gateway-icon">
        <Icon size={18} />
      </div>
      <div className="gateway-info">
        <span className="gateway-type">{config.label}</span>
        <span className="gateway-name">{data.label}</span>
      </div>
      <Handle type="target" position={Position.Bottom} id="bottom-target" />
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}

export const GatewayNode = memo(GatewayNodeComponent);
