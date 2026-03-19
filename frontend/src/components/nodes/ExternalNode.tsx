import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import { Globe, Building2, Database, Map } from 'lucide-react';
import type { DiagramNodeData } from '@/types/oci';

type ExternalNodeProps = NodeProps & { data: DiagramNodeData };

const EXTERNAL_CONFIG: Record<string, { icon: typeof Globe; className: string; label: string }> = {
  internet: { icon: Globe, className: 'external-internet', label: 'Internet' },
  on_premises: { icon: Building2, className: 'external-onprem', label: 'On-Premises' },
  oracle_services: { icon: Database, className: 'external-oracle', label: 'Oracle Services' },
  other_region: { icon: Map, className: 'external-region', label: 'Other Region' },
};

function ExternalNodeComponent({ data }: ExternalNodeProps) {
  const resourceType = (data.resource_type as string) || 'internet';
  const config = EXTERNAL_CONFIG[resourceType] || EXTERNAL_CONFIG.internet;
  const Icon = config.icon;

  return (
    <div className={`external-node ${config.className}`}>
      <div className="external-icon">
        <Icon size={20} />
      </div>
      <span className="external-label">{data.label || config.label}</span>
      <Handle type="target" position={Position.Bottom} />
      <Handle type="source" position={Position.Top} />
    </div>
  );
}

export const ExternalNode = memo(ExternalNodeComponent);
