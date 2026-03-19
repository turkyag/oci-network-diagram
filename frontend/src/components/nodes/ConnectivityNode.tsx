import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import { Building2, Lock, CircuitBoard, Zap, Radio } from 'lucide-react';
import type { DiagramNodeData } from '@/types/oci';

type ConnectivityNodeProps = NodeProps & { data: DiagramNodeData };

const TYPE_CONFIG: Record<string, { icon: typeof Lock; className: string; label: string }> = {
  cpe: { icon: Building2, className: 'conn-cpe', label: 'CPE' },
  ipsec_connection: { icon: Lock, className: 'conn-ipsec', label: 'IPSec VPN' },
  cross_connect: { icon: CircuitBoard, className: 'conn-fastconnect', label: 'FastConnect' },
  virtual_circuit: { icon: Zap, className: 'conn-vc', label: 'Virtual Circuit' },
  rpc: { icon: Radio, className: 'conn-rpc', label: 'Remote Peering' },
};

function ConnectivityNodeComponent({ data }: ConnectivityNodeProps) {
  const config = TYPE_CONFIG[data.resource_type] || TYPE_CONFIG.cpe;
  const Icon = config.icon;

  const ipAddress = (data.properties?.ip_address as string) || '';
  const vpnIp = (data.properties?.vpn_ip as string) || '';
  const status =
    (data.properties?.status as string) ||
    (data.properties?.lifecycle_state as string) ||
    '';
  const bandwidth = (data.properties?.bandwidth_shape_name as string) || '';
  const isUp = ['UP', 'AVAILABLE', 'PROVISIONED'].includes(status.toUpperCase());

  return (
    <div className={`connectivity-node ${config.className}`}>
      <Handle type="target" position={Position.Top} />
      <Handle type="target" position={Position.Left} id="left" />
      <div className="conn-icon">
        <Icon size={16} />
      </div>
      <div className="conn-info">
        <span className="conn-type">{config.label}</span>
        <span className="conn-name">{data.label}</span>
        {(ipAddress || vpnIp) && (
          <span className="conn-ip mono">{ipAddress || vpnIp}</span>
        )}
        {bandwidth && (
          <span className="conn-bandwidth mono">{bandwidth}</span>
        )}
        {status && (
          <span className={`conn-status-dot ${isUp ? 'up' : 'down'}`} title={status} />
        )}
      </div>
      <Handle type="source" position={Position.Bottom} />
      <Handle type="source" position={Position.Right} id="right" />
    </div>
  );
}

export const ConnectivityNode = memo(ConnectivityNodeComponent);
