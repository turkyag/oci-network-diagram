import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import { Cloud } from 'lucide-react';
import type { DiagramNodeData } from '@/types/oci';

type VcnNodeProps = NodeProps & { data: DiagramNodeData };

function VcnNodeComponent({ data }: VcnNodeProps) {
  const cidrBlocks = (data.properties?.cidr_blocks as string[]) || [];
  const dnsLabel = (data.properties?.dns_label as string) || '';

  return (
    <div className="vcn-container">
      <Handle type="target" position={Position.Top} />
      <Handle type="target" position={Position.Left} id="left" />
      <div className="vcn-header">
        <Cloud size={14} className="vcn-icon" />
        <span className="vcn-badge">VCN</span>
        <span className="vcn-name">{data.label}</span>
        {dnsLabel && <span className="vcn-dns mono">{dnsLabel}</span>}
        <span className="vcn-cidr mono">{cidrBlocks.join(', ')}</span>
      </div>
      <Handle type="source" position={Position.Bottom} />
      <Handle type="source" position={Position.Right} id="right" />
    </div>
  );
}

export const VcnNode = memo(VcnNodeComponent);
