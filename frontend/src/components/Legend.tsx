import { useState } from 'react';
import {
  Info,
  ChevronDown,
  ChevronUp,
  Globe,
  Layers,
  GitBranch,
  Shield,
  Cloud,
  Zap,
  Link,
  Lock,
  Radio,
  Server,
  Flame,
} from 'lucide-react';

const NODE_TYPES = [
  { icon: Cloud, label: 'VCN', color: 'var(--accent-primary)' },
  { icon: Layers, label: 'Subnet', color: 'var(--accent-primary)' },
  { icon: GitBranch, label: 'Route Table', color: 'var(--accent-secondary)' },
  { icon: Radio, label: 'DRG', color: 'var(--accent-purple)' },
  { icon: Globe, label: 'IGW', color: '#22c55e' },
  { icon: Lock, label: 'NAT', color: '#f59e0b' },
  { icon: Shield, label: 'SGW', color: '#a855f7' },
  { icon: Link, label: 'LPG', color: '#6366f1' },
  { icon: Zap, label: 'IPSec', color: '#ef4444' },
  { icon: Server, label: 'CPE', color: '#ef4444' },
  { icon: Flame, label: 'Firewall', color: '#f97316' },
];

const EDGE_COLORS = [
  { color: '#22c55e', label: 'Internet traffic', dashed: false },
  { color: '#ef4444', label: 'On-prem / VPN', dashed: false },
  { color: '#a855f7', label: 'Oracle Services', dashed: false },
  { color: '#06b6d4', label: 'DRG routing', dashed: false },
  { color: '#6366f1', label: 'Peering', dashed: false },
  { color: '#f97316', label: 'Firewall inspected', dashed: true },
  { color: '#64748b', label: 'Subnet \u2192 Route Table', dashed: false },
];

const LINE_STYLES = [
  { label: 'Direct', style: 'solid' },
  { label: 'Routing flow', style: 'dashed' },
  { label: 'Active', style: 'animated' },
];

export function Legend() {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="legend">
      <div className="legend-header" onClick={() => setExpanded(!expanded)}>
        <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <Info size={12} />
          Legend
        </span>
        {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
      </div>

      {expanded && (
        <div className="legend-body">
          {/* Node Types */}
          <div className="legend-section">
            <div className="legend-section-title">Node Types</div>
            {NODE_TYPES.map((n) => (
              <div className="legend-item" key={n.label}>
                <span className="legend-icon" style={{ color: n.color }}>
                  <n.icon size={12} />
                </span>
                <span>{n.label}</span>
              </div>
            ))}
          </div>

          {/* Edge Colors */}
          <div className="legend-section">
            <div className="legend-section-title">Edge Colors</div>
            {EDGE_COLORS.map((e) => (
              <div className="legend-item" key={e.label}>
                <span
                  className={`legend-swatch ${e.dashed ? 'dashed' : ''}`}
                  style={e.dashed ? { borderTopColor: e.color } : { background: e.color }}
                />
                <span>{e.label}</span>
              </div>
            ))}
          </div>

          {/* Line Styles */}
          <div className="legend-section">
            <div className="legend-section-title">Line Styles</div>
            {LINE_STYLES.map((s) => (
              <div className="legend-item" key={s.label}>
                <span
                  className={`legend-swatch ${s.style === 'dashed' ? 'dashed' : ''}`}
                  style={
                    s.style === 'solid'
                      ? { background: 'var(--text-muted)' }
                      : s.style === 'dashed'
                      ? { borderTopColor: 'var(--text-muted)' }
                      : {
                          background: 'var(--accent-primary)',
                          boxShadow: '0 0 4px var(--accent-primary)',
                        }
                  }
                />
                <span>{s.label}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
