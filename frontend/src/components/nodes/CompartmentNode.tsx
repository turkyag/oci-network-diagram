import { memo } from 'react';
import { type NodeProps } from '@xyflow/react';
import { Layers } from 'lucide-react';
import type { DiagramNodeData } from '@/types/oci';

type CompartmentNodeProps = NodeProps & { data: DiagramNodeData };

function CompartmentNodeComponent({ data }: CompartmentNodeProps) {
  const compId = (data.properties?.compartment_id as string) || '';
  const isRoot = compId.includes('.tenancy.');

  return (
    <div className="compartment-container">
      <div className="compartment-tab">
        <Layers size={10} className="compartment-tab-icon" />
        <span className="compartment-tab-label">
          {isRoot ? 'ROOT' : 'COMPARTMENT'}
        </span>
        <span className="compartment-tab-name">{data.label}</span>
      </div>
      <div className="compartment-border-accent" />
    </div>
  );
}

export const CompartmentNode = memo(CompartmentNodeComponent);
