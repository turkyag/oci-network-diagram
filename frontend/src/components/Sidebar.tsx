import { Network, Cloud, Layers, GitBranch, Shield, Route, Server, ChevronDown } from 'lucide-react';
import type { TopologySummary, TopologyDetail } from '@/types/oci';

interface SidebarProps {
  topologies: TopologySummary[];
  selectedId: number | null;
  topologyDetail: TopologyDetail | null;
  loading: boolean;
  onSelect: (id: number) => void;
}

export function Sidebar({
  topologies,
  selectedId,
  topologyDetail,
  loading,
  onSelect,
}: SidebarProps) {
  const selected = topologies.find((t) => t.id === selectedId);

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-brand">
          <Network size={20} className="sidebar-brand-icon" />
          <span>OCI Network Explorer</span>
        </div>
      </div>

      {/* Region selector — only if multiple topologies */}
      {topologies.length > 1 && (
        <div className="sidebar-section">
          <label className="sidebar-label">Region</label>
          <div className="sidebar-select-wrapper">
            <select
              className="sidebar-select"
              value={selectedId ?? ''}
              onChange={(e) => onSelect(Number(e.target.value))}
            >
              {topologies.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name.replace('oci-', '')}
                </option>
              ))}
            </select>
            <ChevronDown size={12} className="sidebar-select-icon" />
          </div>
        </div>
      )}

      {/* Topology info */}
      {selected && (
        <div className="sidebar-section">
          <label className="sidebar-label">Topology</label>
          <div className="sidebar-topology-name">{selected.name || 'Loading...'}</div>
          {selected.description && (
            <div className="sidebar-topology-desc">{selected.description}</div>
          )}
        </div>
      )}

      {/* Resource inventory */}
      {loading ? (
        <div className="loading-container">
          <div className="spinner" />
        </div>
      ) : topologyDetail ? (
        <div className="sidebar-section">
          <label className="sidebar-label">Resources</label>
          <div className="sidebar-inventory">
            <InventoryRow icon={Cloud} label="VCNs" count={topologyDetail.vcns.length} />
            <InventoryRow icon={Layers} label="Subnets" count={topologyDetail.subnets.length} />
            <InventoryRow icon={GitBranch} label="DRGs" count={topologyDetail.drgs.length} />
            <InventoryRow icon={Route} label="Route Tables" count={topologyDetail.route_tables.length} />
            <InventoryRow icon={Shield} label="Security Lists" count={topologyDetail.security_lists.length} />
            <InventoryRow icon={Shield} label="NSGs" count={topologyDetail.network_security_groups.length} />
            <InventoryRow icon={Server} label="Load Balancers" count={topologyDetail.load_balancers.length + topologyDetail.network_load_balancers.length} />
            {topologyDetail.ipsec_connections.length > 0 && (
              <InventoryRow icon={Network} label="IPSec VPNs" count={topologyDetail.ipsec_connections.length} />
            )}
            {topologyDetail.remote_peering_connections.length > 0 && (
              <InventoryRow icon={Network} label="RPCs" count={topologyDetail.remote_peering_connections.length} />
            )}
            {topologyDetail.local_peering_gateways.length > 0 && (
              <InventoryRow icon={Network} label="LPGs" count={topologyDetail.local_peering_gateways.length} />
            )}
            {(() => {
              const firewalls = (topologyDetail as unknown as Record<string, unknown>).network_firewalls as unknown[] | undefined;
              return firewalls && firewalls.length > 0
                ? <InventoryRow icon={Shield} label="Firewalls" count={firewalls.length} />
                : null;
            })()}
          </div>
        </div>
      ) : topologies.length === 0 ? (
        <div className="sidebar-section">
          <div className="sidebar-empty">
            <p>No data synced yet.</p>
            <code className="sidebar-cmd">docker compose run --rm oci-sync</code>
          </div>
        </div>
      ) : null}

      {/* Last sync time */}
      {selected && (
        <div className="sidebar-footer">
          <div className="sidebar-sync-time">
            Last sync: {new Date(selected.created_at).toLocaleString('en-US', {
              month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
            })}
          </div>
        </div>
      )}
    </aside>
  );
}

function InventoryRow({ icon: Icon, label, count }: { icon: typeof Cloud; label: string; count: number }) {
  if (count === 0) return null;
  return (
    <div className="inventory-row">
      <Icon size={12} className="inventory-icon" />
      <span className="inventory-label">{label}</span>
      <span className="inventory-count mono">{count}</span>
    </div>
  );
}
