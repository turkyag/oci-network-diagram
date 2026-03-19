import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import { GitBranch } from 'lucide-react';
import type { DiagramNodeData } from '@/types/oci';

type RouteTableNodeProps = NodeProps & { data: DiagramNodeData };

interface RouteRule {
  destination?: string;
  target_name?: string;
  target_type?: string;
  target?: string;
  description?: string;
}

function RouteTableNodeComponent({ data }: RouteTableNodeProps) {
  const ruleCount = (data.properties?.rule_count as number) ?? 0;
  const rules = (data.properties?.rules as RouteRule[]) || [];

  return (
    <div className="rt-node">
      <Handle type="target" position={Position.Top} />
      <Handle type="target" position={Position.Left} id="left" />
      <div className="rt-header">
        <GitBranch size={14} className="rt-icon" />
        <span className="rt-name">{data.label}</span>
        <span className="rt-count badge badge-sm badge-cyan">{ruleCount} rules</span>
      </div>
      {rules.length > 0 && (
        <div className="rt-rules">
          {rules.slice(0, 5).map((rule, i) => (
            <div key={i} className="rt-rule mono">
              <span className="rt-rule-dest">{rule.destination || '—'}</span>
              <span className="rt-rule-arrow">&rarr;</span>
              <span className="rt-rule-target">{rule.target_name || rule.target || rule.description || '—'}</span>
            </div>
          ))}
          {rules.length > 5 && (
            <div className="rt-rule-more">+{rules.length - 5} more</div>
          )}
        </div>
      )}
      <Handle type="source" position={Position.Bottom} />
      <Handle type="source" position={Position.Right} id="right" />
    </div>
  );
}

export const RouteTableNode = memo(RouteTableNodeComponent);
