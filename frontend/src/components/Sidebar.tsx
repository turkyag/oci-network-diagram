import { useState } from 'react';
import { Network, Cloud, Layers, GitBranch, Shield, Route, Server, Globe, Box, ChevronDown, ChevronRight, MapPin } from 'lucide-react';
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
  const region = selected?.name.replace('oci-', '') || '';

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-brand">
          <Network size={20} className="sidebar-brand-icon" />
          <span>OCI Network Explorer</span>
        </div>
      </div>

      {/* Region */}
      {region && (
        <div className="sidebar-section">
          <div className="sidebar-region">
            <MapPin size={12} />
            <span className="mono">{region}</span>
          </div>
        </div>
      )}

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

      {/* Compartment tree with resources */}
      {loading ? (
        <div className="loading-container">
          <div className="spinner" />
        </div>
      ) : topologyDetail ? (
        <CompartmentTree detail={topologyDetail} />
      ) : topologies.length === 0 ? (
        <div className="sidebar-section">
          <div className="sidebar-empty">
            <p>No data synced yet.</p>
            <code className="sidebar-cmd">docker compose run --rm oci-sync sync.py --config-file /oci/config</code>
          </div>
        </div>
      ) : null}

      {/* Last sync */}
      {selected && (
        <div className="sidebar-footer">
          <div className="sidebar-sync-time">
            Synced {new Date(selected.created_at).toLocaleString('en-US', {
              month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
            })}
          </div>
        </div>
      )}
    </aside>
  );
}

function CompartmentTree({ detail }: { detail: TopologyDetail }) {
  const [expanded, setExpanded] = useState<Record<string, boolean>>({ root: true });

  const toggle = (key: string) => {
    setExpanded(prev => ({ ...prev, [key]: !prev[key] }));
  };

  // Group resources by compartment
  // Since we only have compartment_id on VCNs and DRGs, derive from those
  const compartments = new Map<string, { name: string; resources: ResourceGroup }>();

  // Build compartment map from VCNs
  for (const vcn of detail.vcns) {
    const compId = (vcn as Record<string, unknown>).compartment_id as string || 'unknown';
    if (!compartments.has(compId)) {
      const name = compId.includes('.tenancy.') ? 'Root Compartment' : `Compartment ...${compId.slice(-8)}`;
      compartments.set(compId, { name, resources: emptyGroup() });
    }
    const group = compartments.get(compId)!;
    group.resources.vcns.push(vcn.display_name || (vcn as Record<string, unknown>).name as string || 'VCN');
  }

  // If no compartments found, create a default root
  if (compartments.size === 0) {
    compartments.set('root', { name: 'Root Compartment', resources: emptyGroup() });
  }

  // Assign all other resources to the first (root) compartment for now
  const rootGroup = compartments.values().next().value!.resources;
  rootGroup.subnets = detail.subnets.length;
  rootGroup.drgs = detail.drgs.map(d => d.display_name || (d as Record<string, unknown>).name as string || 'DRG');
  rootGroup.routeTables = detail.route_tables.length;
  rootGroup.securityLists = detail.security_lists.length;
  rootGroup.nsgs = detail.network_security_groups.length;
  rootGroup.igws = detail.internet_gateways.length;
  rootGroup.natGws = detail.nat_gateways.length;
  rootGroup.sgws = detail.service_gateways.length;
  rootGroup.lbs = detail.load_balancers.length + detail.network_load_balancers.length;
  rootGroup.ipsec = detail.ipsec_connections.length;
  rootGroup.rpcs = detail.remote_peering_connections.length;
  rootGroup.lpgs = detail.local_peering_gateways.length;

  return (
    <div className="sidebar-section compartment-tree">
      <label className="sidebar-label">Compartments</label>
      {Array.from(compartments.entries()).map(([compId, { name, resources }]) => {
        const key = compId.slice(-12) || 'root';
        const isOpen = expanded[key] !== false; // default open

        return (
          <div key={key} className="comp-node">
            <div className="comp-header" onClick={() => toggle(key)}>
              {isOpen ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
              <Box size={12} className="comp-icon" />
              <span className="comp-name">{name}</span>
            </div>

            {isOpen && (
              <div className="comp-resources">
                {/* VCNs — expandable */}
                {resources.vcns.map((vcnName, i) => (
                  <VcnTreeNode key={i} name={vcnName} resources={resources} />
                ))}

                {/* DRGs */}
                {resources.drgs.map((drgName, i) => (
                  <div key={`drg-${i}`} className="comp-resource-item">
                    <GitBranch size={11} className="comp-res-icon drg" />
                    <span>{drgName}</span>
                  </div>
                ))}

                {/* Standalone counts */}
                {resources.lbs > 0 && (
                  <div className="comp-resource-item">
                    <Server size={11} className="comp-res-icon" />
                    <span>Load Balancers</span>
                    <span className="comp-count">{resources.lbs}</span>
                  </div>
                )}
                {resources.ipsec > 0 && (
                  <div className="comp-resource-item">
                    <Network size={11} className="comp-res-icon" />
                    <span>IPSec VPNs</span>
                    <span className="comp-count">{resources.ipsec}</span>
                  </div>
                )}
                {resources.rpcs > 0 && (
                  <div className="comp-resource-item">
                    <Network size={11} className="comp-res-icon" />
                    <span>RPCs</span>
                    <span className="comp-count">{resources.rpcs}</span>
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

function VcnTreeNode({ name, resources }: { name: string; resources: ResourceGroup }) {
  const [open, setOpen] = useState(true);

  return (
    <div className="comp-vcn">
      <div className="comp-resource-item vcn-item" onClick={() => setOpen(!open)}>
        {open ? <ChevronDown size={10} /> : <ChevronRight size={10} />}
        <Cloud size={11} className="comp-res-icon vcn" />
        <span className="comp-vcn-name">{name}</span>
      </div>
      {open && (
        <div className="comp-vcn-children">
          <ResourceCount icon={Layers} label="Subnets" count={resources.subnets} />
          <ResourceCount icon={Globe} label="IGWs" count={resources.igws} />
          <ResourceCount icon={Globe} label="NAT GWs" count={resources.natGws} />
          <ResourceCount icon={Globe} label="SGWs" count={resources.sgws} />
          <ResourceCount icon={Route} label="Route Tables" count={resources.routeTables} />
          <ResourceCount icon={Shield} label="Security Lists" count={resources.securityLists} />
          <ResourceCount icon={Shield} label="NSGs" count={resources.nsgs} />
          <ResourceCount icon={Network} label="LPGs" count={resources.lpgs} />
        </div>
      )}
    </div>
  );
}

function ResourceCount({ icon: Icon, label, count }: { icon: typeof Cloud; label: string; count: number }) {
  if (count === 0) return null;
  return (
    <div className="comp-resource-count">
      <Icon size={10} className="comp-res-icon-sm" />
      <span>{label}</span>
      <span className="comp-count">{count}</span>
    </div>
  );
}

interface ResourceGroup {
  vcns: string[];
  drgs: string[];
  subnets: number;
  routeTables: number;
  securityLists: number;
  nsgs: number;
  igws: number;
  natGws: number;
  sgws: number;
  lbs: number;
  ipsec: number;
  rpcs: number;
  lpgs: number;
}

function emptyGroup(): ResourceGroup {
  return { vcns: [], drgs: [], subnets: 0, routeTables: 0, securityLists: 0, nsgs: 0, igws: 0, natGws: 0, sgws: 0, lbs: 0, ipsec: 0, rpcs: 0, lpgs: 0 };
}
