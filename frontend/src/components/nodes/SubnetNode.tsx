import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import type { DiagramNodeData } from '@/types/oci';

type SubnetNodeProps = NodeProps & { data: DiagramNodeData };

function SubnetNodeComponent({ data }: SubnetNodeProps) {
  const cidr = (data.properties?.cidr_block as string) || '';
  const isPublic = (data.properties?.is_public as boolean) ?? false;
  const routeTableName = (data.properties?.route_table_name as string) || '';

  return (
    <div className={`subnet-node ${isPublic ? 'public' : 'private'}`}>
      <Handle type="target" position={Position.Left} id="left" />
      <div className="subnet-content">
        <div className="subnet-header-row">
          <span className={`subnet-access-dot ${isPublic ? 'public' : 'private'}`} title={isPublic ? 'Public' : 'Private'} />
          <span className="subnet-name">{data.label}</span>
        </div>
        <span className="subnet-cidr mono">{cidr}</span>
        {routeTableName && (
          <span className="subnet-rt mono">RT: {routeTableName}</span>
        )}
      </div>
      <Handle type="source" position={Position.Right} id="right" />
    </div>
  );
}

export const SubnetNode = memo(SubnetNodeComponent);
