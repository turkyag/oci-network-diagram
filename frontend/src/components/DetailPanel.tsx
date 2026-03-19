import { useState, useCallback } from 'react';
import { X, ChevronDown, ChevronRight, AlertTriangle } from 'lucide-react';
import type { DiagramNodeData, VcnChildren, DrgChildren, AnalysisData } from '@/types/oci';

interface DetailPanelProps {
  data: DiagramNodeData;
  analysisData?: AnalysisData | null;
  onClose: () => void;
}

const TYPE_LABELS: Record<string, string> = {
  vcn: 'Virtual Cloud Network',
  subnet: 'Subnet',
  drg: 'Dynamic Routing Gateway',
  internet_gateway: 'Internet Gateway',
  nat_gateway: 'NAT Gateway',
  service_gateway: 'Service Gateway',
  gateway: 'Gateway',
  load_balancer: 'Load Balancer',
  network_load_balancer: 'Network Load Balancer',
  security_list: 'Security List',
  network_security_group: 'Network Security Group',
  route_table: 'Route Table',
  routeTable: 'Route Table',
  remote_peering_connection: 'Remote Peering Connection',
  local_peering_gateway: 'Local Peering Gateway',
  lpg: 'Local Peering Gateway',
  ipsec_connection: 'IPSec Connection',
  cpe: 'Customer Premises Equipment',
  ipsec_tunnel: 'IPSec Tunnel',
  drg_attachment: 'DRG Attachment',
  drg_route_table: 'DRG Route Table',
  drgRouteTable: 'DRG Route Table',
  cross_connect: 'Cross Connect',
  virtual_circuit: 'Virtual Circuit',
  network_firewall: 'Network Firewall',
  firewall: 'Network Firewall',
  external: 'External Boundary',
};

const HIDDEN_KEYS = new Set(['label', 'type', 'resource_type', 'resource_id', 'children', 'detail']);

export function DetailPanel({ data, analysisData, onClose }: DetailPanelProps) {
  const typeLabel = TYPE_LABELS[data.resource_type] || data.resource_type;
  const properties = data.properties || {};

  return (
    <div className="detail-panel">
      <div className="detail-panel-header">
        <div>
          <div className="detail-panel-type">{typeLabel}</div>
          <div className="detail-panel-title">{data.label}</div>
        </div>
        <button className="btn btn-ghost" onClick={onClose}>
          <X size={18} />
        </button>
      </div>

      <div className="detail-panel-body">
        {/* Identity Section */}
        <div className="detail-section">
          <div className="detail-section-title">Identity</div>
          <div className="detail-field">
            <span className="detail-field-label">Name</span>
            <span className="detail-field-value">{data.label}</span>
          </div>
          {data.resource_id && (
            <div className="detail-field">
              <span className="detail-field-label">OCID</span>
              <span className="detail-field-value detail-ocid mono">{data.resource_id}</span>
            </div>
          )}
          <div className="detail-field">
            <span className="detail-field-label">Type</span>
            <span className="detail-field-value">
              <span className="detail-tag detail-tag-cyan">{formatResourceType(data.resource_type)}</span>
            </span>
          </div>
          {(properties.compartment_name as string || properties.compartment_id as string) ? (
            <div className="detail-field">
              <span className="detail-field-label">Compartment</span>
              <span className="detail-field-value">{(properties.compartment_name as string) || (properties.compartment_id as string)}</span>
            </div>
          ) : null}
        </div>

        {/* Type-specific content */}
        {renderTypeContent(data, properties, analysisData)}

        {/* VCN Tabbed Detail */}
        {data.resource_type === 'vcn' && (data.detail || data.children) && (
          <VcnDetailTabs detail={(data.detail || data.children) as VcnChildren} />
        )}

        {/* DRG Tabbed Detail (tabs handled separately from DrgContent properties) */}
        {data.resource_type === 'drg' && (data.detail || data.children) && (
          <DrgDetailTabs detail={(data.detail || data.children) as DrgChildren} />
        )}
      </div>
    </div>
  );
}

/* ========== Type-Specific Content ========== */

function renderTypeContent(
  data: DiagramNodeData,
  properties: Record<string, unknown>,
  analysisData?: AnalysisData | null,
) {
  switch (data.resource_type) {
    case 'vcn':
      return <VcnContent properties={properties} />;
    case 'subnet':
      return <SubnetContent data={data} properties={properties} analysisData={analysisData} />;
    case 'routeTable':
    case 'route_table':
      return <RouteTableContent data={data} properties={properties} analysisData={analysisData} />;
    case 'drg':
      return <DrgContent properties={properties} />;
    case 'drgRouteTable':
    case 'drg_route_table':
      return <DrgRouteTableContent properties={properties} />;
    case 'gateway':
    case 'internet_gateway':
    case 'nat_gateway':
    case 'service_gateway':
      return <GatewayContent data={data} properties={properties} />;
    case 'external':
      return <ExternalContent properties={properties} />;
    case 'lpg':
    case 'local_peering_gateway':
      return <LpgContent properties={properties} />;
    case 'firewall':
    case 'network_firewall':
      return <FirewallContent properties={properties} />;
    case 'load_balancer':
    case 'network_load_balancer':
      return <LoadBalancerContent data={data} properties={properties} />;
    case 'ipsec_connection':
      return <IpsecConnectionContent properties={properties} />;
    default:
      return <GenericContent properties={properties} />;
  }
}

/* --- VCN --- */
function VcnContent({ properties }: { properties: Record<string, unknown> }) {
  const cidrBlocks = (properties.cidr_blocks as string[]) || [];
  const dnsLabel = properties.dns_label as string | undefined;
  const nsgs = (properties.network_security_groups as Array<{
    display_name: string;
    ocid?: string;
    rules?: Array<{
      direction: string;
      protocol: string;
      source?: string;
      destination?: string;
      description?: string;
    }>;
  }>) || [];

  const [nsgExpanded, setNsgExpanded] = useState<Record<string, boolean>>({});

  const toggleNsg = useCallback((name: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setNsgExpanded((prev) => ({ ...prev, [name]: !prev[name] }));
  }, []);

  return (
    <>
      <div className="detail-section">
        <div className="detail-section-title">Configuration</div>
        {cidrBlocks.length > 0 && (
          <div className="detail-field">
            <span className="detail-field-label">CIDRs</span>
            <span className="detail-field-value mono">{cidrBlocks.join(', ')}</span>
          </div>
        )}
        {dnsLabel && (
          <div className="detail-field">
            <span className="detail-field-label">DNS Label</span>
            <span className="detail-field-value mono">{dnsLabel}</span>
          </div>
        )}
        {properties.lifecycle_state != null && (
          <div className="detail-field">
            <span className="detail-field-label">State</span>
            <span className="detail-field-value">
              <span className="detail-tag detail-tag-green">{String(properties.lifecycle_state)}</span>
            </span>
          </div>
        )}
      </div>

      {/* Network Security Groups */}
      {nsgs.length > 0 && (
        <div className="detail-section">
          <div className="detail-section-title">Network Security Groups</div>
          {nsgs.map((nsg, i) => (
            <div key={i}>
              <div
                className="detail-expandable-header"
                onClick={(e) => toggleNsg(nsg.display_name, e)}
              >
                {nsgExpanded[nsg.display_name] ? <ChevronDown size={11} /> : <ChevronRight size={11} />}
                <span className="detail-item-name">{nsg.display_name}</span>
                <span className="badge badge-purple">{nsg.rules?.length || 0} rules</span>
              </div>
              {nsgExpanded[nsg.display_name] && nsg.rules && nsg.rules.length > 0 && (
                <div className="detail-expandable-content">
                  {nsg.rules.map((r, ri) => (
                    <div className="detail-rule-row" key={ri}>
                      <span className={`detail-rule-direction ${r.direction === 'INGRESS' ? 'ingress' : 'egress'}`}>
                        {r.direction === 'INGRESS' ? 'IN' : 'OUT'}
                      </span>
                      <span>{protocolName(r.protocol)}</span>
                      <span className="mono">{r.source || r.destination || '*'}</span>
                      {r.description && <span className="detail-rule-desc">{r.description}</span>}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </>
  );
}

/* --- Subnet --- */
function SubnetContent({
  data,
  properties,
  analysisData,
}: {
  data: DiagramNodeData;
  properties: Record<string, unknown>;
  analysisData?: AnalysisData | null;
}) {
  const [securityOpen, setSecurityOpen] = useState(false);
  const cidr = (properties.cidr_block as string) || (properties.cidr as string) || '';
  const isPublic = properties.prohibit_public_ip_on_vnic === false || properties.is_public === true;
  const routeTableName = properties.route_table_name as string | undefined;
  const securityListNames = properties.security_list_names as string[] | undefined;

  // Try to get analysis flow rules for this subnet
  const analysisFlow = analysisData?.flows?.find(
    (f) => f.subnet_ocid === data.resource_id || f.subnet_name === data.label,
  );
  const rules = analysisFlow?.rules || (data.detail?.rules as Array<{
    destination: string;
    destination_type: string;
    target_type: string;
    target_name: string;
    is_default_route?: boolean;
  }>) || (properties.rules as Array<{
    destination: string;
    destination_type: string;
    target_type: string;
    target_name: string;
    is_default_route?: boolean;
  }>) || undefined;

  return (
    <>
      <div className="detail-section">
        <div className="detail-section-title">Configuration</div>
        {cidr && (
          <div className="detail-field">
            <span className="detail-field-label">CIDR</span>
            <span className="detail-field-value mono">{cidr}</span>
          </div>
        )}
        <div className="detail-field">
          <span className="detail-field-label">Access</span>
          <span className="detail-field-value">
            <span className={`detail-tag ${isPublic ? 'detail-tag-green' : 'detail-tag-amber'}`}>
              {isPublic ? 'Public' : 'Private'}
            </span>
          </span>
        </div>
        {properties.dns_label != null && (
          <div className="detail-field">
            <span className="detail-field-label">DNS Label</span>
            <span className="detail-field-value mono">{String(properties.dns_label)}</span>
          </div>
        )}
      </div>

      {/* Route Table */}
      <div className="detail-section">
        <div className="detail-section-title">Route Table</div>
        {(routeTableName || analysisFlow?.route_table_name) && (
          <div className="detail-field">
            <span className="detail-field-label">Name</span>
            <span className="detail-field-value detail-rt-link">{routeTableName || analysisFlow?.route_table_name}</span>
          </div>
        )}
        {rules && rules.length > 0 && (
          <div className="detail-route-rules">
            {rules.map((r, i) => (
              <div className={`detail-rule-row ${r.is_default_route ? 'default-route' : ''}`} key={i}>
                <span className="mono">{r.destination}</span>
                <ChevronRight size={10} className="detail-rule-arrow" />
                <span>{r.target_name || 'UNKNOWN'}</span>
                {r.target_type && <span className="detail-tag detail-tag-cyan">{r.target_type}</span>}
                {(!r.target_name || r.target_name === 'UNKNOWN') && (
                  <AlertTriangle size={10} className="detail-warning-icon" />
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Security Lists (with detailed rules if available) */}
      <SecurityListsSection
        securityListNames={securityListNames}
        securityLists={properties.security_lists as Array<{
          display_name: string;
          rules?: Array<{
            direction: string;
            protocol: string;
            source?: string;
            destination?: string;
            description?: string;
            destination_port_range_min?: number;
            destination_port_range_max?: number;
          }>;
        }> | undefined}
      />
    </>
  );
}

/* --- Security Lists Section (for subnet detail) --- */
function SecurityListsSection({
  securityListNames,
  securityLists,
}: {
  securityListNames?: string[];
  securityLists?: Array<{
    display_name: string;
    rules?: Array<{
      direction: string;
      protocol: string;
      source?: string;
      destination?: string;
      description?: string;
      destination_port_range_min?: number;
      destination_port_range_max?: number;
    }>;
  }>;
}) {
  const [securityOpen, setSecurityOpen] = useState(false);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  const toggle = useCallback((name: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setExpanded((prev) => ({ ...prev, [name]: !prev[name] }));
  }, []);

  // Prefer detailed security_lists from backend; fall back to name-only list
  const detailedLists = securityLists || [];
  const hasDetailed = detailedLists.length > 0;
  const count = hasDetailed ? detailedLists.length : (securityListNames?.length || 0);

  if (count === 0) return null;

  return (
    <div className="detail-section">
      <div
        className="detail-expandable-header"
        onClick={() => setSecurityOpen(!securityOpen)}
      >
        {securityOpen ? <ChevronDown size={11} /> : <ChevronRight size={11} />}
        <span className="detail-item-name">Security Lists</span>
        <span className="badge badge-cyan">{count}</span>
      </div>
      {securityOpen && (
        <div className="detail-expandable-content">
          {hasDetailed ? (
            detailedLists.map((sl, i) => (
              <div key={i}>
                <div
                  className="detail-expandable-header"
                  onClick={(e) => toggle(sl.display_name, e)}
                  style={{ paddingLeft: '4px' }}
                >
                  {expanded[sl.display_name] ? <ChevronDown size={10} /> : <ChevronRight size={10} />}
                  <span className="detail-item-name">{sl.display_name}</span>
                  <span className="badge badge-cyan">{sl.rules?.length || 0} rules</span>
                </div>
                {expanded[sl.display_name] && sl.rules && sl.rules.length > 0 && (
                  <div className="detail-expandable-content" style={{ paddingLeft: '8px' }}>
                    {sl.rules.map((r, ri) => (
                      <div className="detail-rule-row" key={ri}>
                        <span className={`detail-rule-direction ${r.direction === 'INGRESS' ? 'ingress' : 'egress'}`}>
                          {r.direction === 'INGRESS' ? 'IN' : 'OUT'}
                        </span>
                        <span>{protocolName(r.protocol)}</span>
                        <span className="mono">{r.source || r.destination || '*'}</span>
                        {r.destination_port_range_min !== undefined && (
                          <span className="mono">:{portRange(r.destination_port_range_min, r.destination_port_range_max)}</span>
                        )}
                        {r.description && <span className="detail-rule-desc">{r.description}</span>}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))
          ) : (
            securityListNames!.map((name, i) => (
              <div className="detail-field" key={i}>
                <span className="detail-field-label">{name}</span>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

/* --- Route Table --- */
function RouteTableContent({
  data,
  properties,
  analysisData,
}: {
  data: DiagramNodeData;
  properties: Record<string, unknown>;
  analysisData?: AnalysisData | null;
}) {
  // Try to find analysis flow data for this route table
  const analysisFlow = analysisData?.flows?.find(
    (f) => f.route_table_ocid === data.resource_id || f.route_table_name === data.label,
  );
  const rules = analysisFlow?.rules || (data.detail?.rules as Array<{
    destination: string;
    destination_type?: string;
    target_type?: string;
    target_name?: string;
    network_entity_id?: string;
    description?: string;
    is_default_route?: boolean;
  }>) || (properties.rules as Array<{
    destination: string;
    destination_type?: string;
    target_type?: string;
    target_name?: string;
    network_entity_id?: string;
    description?: string;
    is_default_route?: boolean;
  }>) || undefined;

  const ruleCount = rules?.length || (properties.rule_count as number) || 0;

  return (
    <>
      <div className="detail-section">
        <div className="detail-section-title">Overview</div>
        <div className="detail-field">
          <span className="detail-field-label">Rules</span>
          <span className="detail-field-value">
            <span className="detail-tag detail-tag-amber">{ruleCount} rules</span>
          </span>
        </div>
      </div>

      {rules && rules.length > 0 && (
        <div className="detail-section">
          <div className="detail-section-title">Route Rules</div>
          <div className="detail-route-rules">
            {rules.map((r, i) => {
              const isDefault = r.is_default_route || r.destination === '0.0.0.0/0';
              const targetName = r.target_name || '';
              const hasUnknownTarget = !targetName || targetName === 'UNKNOWN';
              return (
                <div className={`detail-rule-row ${isDefault ? 'default-route' : ''}`} key={i}>
                  <span className="mono">{r.destination}</span>
                  <ChevronRight size={10} className="detail-rule-arrow" />
                  <span>{hasUnknownTarget ? truncateId((r as Record<string, unknown>).network_entity_id as string || '') : targetName}</span>
                  {r.target_type && <span className="detail-tag detail-tag-cyan">{r.target_type}</span>}
                  {hasUnknownTarget && <AlertTriangle size={10} className="detail-warning-icon" />}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </>
  );
}

/* --- DRG (properties only, tabs handled separately) --- */
function DrgContent({ properties }: { properties: Record<string, unknown> }) {
  const compartmentName = properties.compartment_name as string | undefined;
  const compartment = compartmentName || (properties.compartment_id as string | undefined);
  const routeDistributions = properties.route_distributions as Array<{ name: string; type: string }> | undefined;
  const attachments = (properties.attachments as Array<{
    name?: string;
    display_name?: string;
    type?: string;
    network_type?: string;
    network_id?: string;
  }>) || [];
  const drgRouteTables = (properties.drg_route_tables as Array<{
    display_name: string;
    is_ecmp_enabled?: boolean;
    rules?: Array<{
      destination: string;
      destination_type?: string;
      next_hop_drg_attachment_id?: string;
      next_hop?: string;
    }>;
  }>) || [];

  const [expandedRt, setExpandedRt] = useState<Record<string, boolean>>({});

  const toggleRt = useCallback((name: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setExpandedRt((prev) => ({ ...prev, [name]: !prev[name] }));
  }, []);

  return (
    <>
      <div className="detail-section">
        <div className="detail-section-title">Configuration</div>
        {compartment && (
          <div className="detail-field">
            <span className="detail-field-label">Compartment</span>
            <span className="detail-field-value">{truncateId(compartment)}</span>
          </div>
        )}
        {properties.lifecycle_state != null && (
          <div className="detail-field">
            <span className="detail-field-label">State</span>
            <span className="detail-field-value">
              <span className="detail-tag detail-tag-green">{String(properties.lifecycle_state)}</span>
            </span>
          </div>
        )}
      </div>

      {/* Attachments */}
      {attachments.length > 0 && (
        <div className="detail-section">
          <div className="detail-section-title">Attachments</div>
          {attachments.map((a, i) => (
            <div className="detail-field" key={i}>
              <span className="detail-field-label">{a.name || a.display_name || `Attachment ${i + 1}`}</span>
              <span className="detail-field-value">
                <span className="detail-tag detail-tag-purple">{a.type || a.network_type || 'VCN'}</span>
              </span>
            </div>
          ))}
        </div>
      )}

      {/* DRG Route Tables */}
      {drgRouteTables.length > 0 && (
        <div className="detail-section">
          <div className="detail-section-title">DRG Route Tables</div>
          {drgRouteTables.map((rt, i) => (
            <div key={i}>
              <div
                className="detail-expandable-header"
                onClick={(e) => toggleRt(rt.display_name, e)}
              >
                {expandedRt[rt.display_name] ? <ChevronDown size={11} /> : <ChevronRight size={11} />}
                <span className="detail-item-name">{rt.display_name}</span>
                {rt.is_ecmp_enabled && <span className="badge badge-cyan">ECMP</span>}
                <span className="badge badge-amber">{rt.rules?.length || 0} rules</span>
              </div>
              {expandedRt[rt.display_name] && rt.rules && rt.rules.length > 0 && (
                <div className="detail-expandable-content">
                  {rt.rules.map((r, ri) => (
                    <div className="detail-rule-row" key={ri}>
                      <span className="mono">{r.destination}</span>
                      <ChevronRight size={10} className="detail-rule-arrow" />
                      <span>{r.destination_type || 'VCN attachment'}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {routeDistributions && routeDistributions.length > 0 && (
        <div className="detail-section">
          <div className="detail-section-title">Route Distributions</div>
          {routeDistributions.map((d, i) => (
            <div className="detail-field" key={i}>
              <span className="detail-field-label">{d.name}</span>
              <span className="detail-field-value">
                <span className="detail-tag detail-tag-cyan">{d.type}</span>
              </span>
            </div>
          ))}
        </div>
      )}
    </>
  );
}

/* --- DRG Route Table --- */
function DrgRouteTableContent({ properties }: { properties: Record<string, unknown> }) {
  const isEcmp = properties.is_ecmp_enabled === true;
  const rules = properties.rules as Array<{
    destination: string;
    destination_type?: string;
    next_hop_drg_attachment_id?: string;
    next_hop?: string;
  }> | undefined;

  return (
    <>
      <div className="detail-section">
        <div className="detail-section-title">Configuration</div>
        <div className="detail-field">
          <span className="detail-field-label">ECMP</span>
          <span className="detail-field-value">
            <span className={`detail-tag ${isEcmp ? 'detail-tag-green' : 'detail-tag-amber'}`}>
              {isEcmp ? 'Enabled' : 'Disabled'}
            </span>
          </span>
        </div>
      </div>

      {rules && rules.length > 0 && (
        <div className="detail-section">
          <div className="detail-section-title">DRG Route Rules</div>
          <div className="detail-route-rules">
            {rules.map((r, i) => (
              <div className="detail-rule-row" key={i}>
                <span className="mono">{r.destination}</span>
                <ChevronRight size={10} className="detail-rule-arrow" />
                <span>{truncateId(r.next_hop_drg_attachment_id || r.next_hop || '')}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  );
}

/* --- Gateway (IGW / NAT / SGW) --- */
function GatewayContent({ data, properties }: { data: DiagramNodeData; properties: Record<string, unknown> }) {
  const gwType = (properties.gateway_type as string) || data.resource_type;
  const isEnabled = properties.is_enabled;
  const natIp = properties.nat_ip as string | undefined;
  const publicIp = properties.public_ip as string | undefined;
  const services = properties.services as string[] | undefined;
  const usedByRoutes = (properties.used_by_routes as Array<{
    destination?: string;
    route_table_name?: string;
  }>) || [];

  return (
    <>
      <div className="detail-section">
        <div className="detail-section-title">Configuration</div>
        <div className="detail-field">
          <span className="detail-field-label">Type</span>
          <span className="detail-field-value">
            <span className="detail-tag detail-tag-cyan">{formatGatewayType(gwType)}</span>
          </span>
        </div>
        {isEnabled !== undefined && (
          <div className="detail-field">
            <span className="detail-field-label">Status</span>
            <span className="detail-field-value">
              <span className={`detail-tag ${isEnabled ? 'detail-tag-green' : 'detail-tag-red'}`}>
                {isEnabled ? 'Enabled' : 'Disabled'}
              </span>
            </span>
          </div>
        )}
        {(natIp || publicIp) && (
          <div className="detail-field">
            <span className="detail-field-label">Public IP</span>
            <span className="detail-field-value mono">{natIp || publicIp}</span>
          </div>
        )}
        {services && services.length > 0 && (
          <div className="detail-field">
            <span className="detail-field-label">Services</span>
            <span className="detail-field-value">{services.join(', ')}</span>
          </div>
        )}
        {properties.lifecycle_state != null && (
          <div className="detail-field">
            <span className="detail-field-label">State</span>
            <span className="detail-field-value">{String(properties.lifecycle_state)}</span>
          </div>
        )}
      </div>

      {/* Used By Route Rules */}
      {usedByRoutes.length > 0 && (
        <div className="detail-section">
          <div className="detail-section-title">Used By Route Rules</div>
          {usedByRoutes.map((r, i) => (
            <div className="detail-field" key={i}>
              <span className="detail-field-label mono">{r.destination || 'unknown'}</span>
              {r.route_table_name && (
                <span className="detail-field-value" style={{ opacity: 0.7 }}>
                  from {r.route_table_name}
                </span>
              )}
            </div>
          ))}
        </div>
      )}
    </>
  );
}

/* --- External --- */
function ExternalContent({ properties }: { properties: Record<string, unknown> }) {
  const externalType = (properties.external_type as string) || (properties.type as string) || 'External';
  const description = properties.description as string | undefined;

  return (
    <div className="detail-section">
      <div className="detail-section-title">Boundary</div>
      <div className="detail-field">
        <span className="detail-field-label">Type</span>
        <span className="detail-field-value">
          <span className="detail-tag detail-tag-purple">{externalType}</span>
        </span>
      </div>
      <div className="detail-field">
        <span className="detail-field-label">Description</span>
        <span className="detail-field-value" style={description ? undefined : { color: 'var(--text-dim)' }}>
          {description || 'Represents a network boundary outside this topology'}
        </span>
      </div>
    </div>
  );
}

/* --- LPG --- */
function LpgContent({ properties }: { properties: Record<string, unknown> }) {
  const peerId = properties.peer_id as string | undefined;
  const peeringStatus = properties.peering_status as string | undefined;

  return (
    <div className="detail-section">
      <div className="detail-section-title">Peering</div>
      {peerId && (
        <div className="detail-field">
          <span className="detail-field-label">Peer ID</span>
          <span className="detail-field-value">{truncateId(peerId)}</span>
        </div>
      )}
      <div className="detail-field">
        <span className="detail-field-label">Status</span>
        <span className="detail-field-value">
          <span
            className={`detail-tag ${
              peeringStatus === 'PEERED'
                ? 'detail-tag-green'
                : peeringStatus === 'REVOKED'
                ? 'detail-tag-red'
                : 'detail-tag-amber'
            }`}
          >
            {peeringStatus || 'N/A'}
          </span>
        </span>
      </div>
      {properties.is_cross_tenancy_peering !== undefined && (
        <div className="detail-field">
          <span className="detail-field-label">Cross-tenancy</span>
          <span className="detail-field-value">{properties.is_cross_tenancy_peering ? 'Yes' : 'No'}</span>
        </div>
      )}
    </div>
  );
}

/* --- Firewall --- */
function FirewallContent({ properties }: { properties: Record<string, unknown> }) {
  const policyId = properties.policy_id as string | undefined;
  const subnetId = properties.subnet_id as string | undefined;

  return (
    <div className="detail-section">
      <div className="detail-section-title">Configuration</div>
      {policyId && (
        <div className="detail-field">
          <span className="detail-field-label">Policy ID</span>
          <span className="detail-field-value">{truncateId(policyId)}</span>
        </div>
      )}
      {subnetId && (
        <div className="detail-field">
          <span className="detail-field-label">Subnet ID</span>
          <span className="detail-field-value">{truncateId(subnetId)}</span>
        </div>
      )}
      {properties.ip_addresses != null && (
        <div className="detail-field">
          <span className="detail-field-label">IP Addresses</span>
          <span className="detail-field-value mono">
            {(properties.ip_addresses as string[]).join(', ') || '-'}
          </span>
        </div>
      )}
    </div>
  );
}

/* --- Load Balancer --- */
function LoadBalancerContent({ data, properties }: { data: DiagramNodeData; properties: Record<string, unknown> }) {
  const isNlb = data.resource_type === 'network_load_balancer';
  const shape = (properties.shape as string) || (properties.shape_name as string) || '';
  const isPrivate = properties.is_private === true;
  const ipAddresses = (properties.ip_addresses as string[]) || [];
  const subnetIds = (properties.subnet_ids as string[]) || [];

  return (
    <>
      <div className="detail-section">
        <div className="detail-section-title">Configuration</div>
        <div className="detail-field">
          <span className="detail-field-label">Type</span>
          <span className="detail-field-value">
            <span className="detail-tag detail-tag-purple">{isNlb ? 'Network LB' : 'Load Balancer'}</span>
          </span>
        </div>
        {shape && (
          <div className="detail-field">
            <span className="detail-field-label">Shape</span>
            <span className="detail-field-value">{shape}</span>
          </div>
        )}
        <div className="detail-field">
          <span className="detail-field-label">Access</span>
          <span className="detail-field-value">
            <span className={`detail-tag ${isPrivate ? 'detail-tag-amber' : 'detail-tag-green'}`}>
              {isPrivate ? 'Private' : 'Public'}
            </span>
          </span>
        </div>
      </div>
      {ipAddresses.length > 0 && (
        <div className="detail-section">
          <div className="detail-section-title">IP Addresses</div>
          {ipAddresses.map((ip, i) => (
            <div className="detail-field" key={i}>
              <span className="detail-field-label">IP {i + 1}</span>
              <span className="detail-field-value mono">{ip}</span>
            </div>
          ))}
        </div>
      )}
      {subnetIds.length > 0 && (
        <div className="detail-section">
          <div className="detail-section-title">Subnets</div>
          {subnetIds.map((sid, i) => (
            <div className="detail-field" key={i}>
              <span className="detail-field-label">Subnet {i + 1}</span>
              <span className="detail-field-value">{truncateId(sid)}</span>
            </div>
          ))}
        </div>
      )}
    </>
  );
}

/* --- IPSec Connection --- */
function IpsecConnectionContent({ properties }: { properties: Record<string, unknown> }) {
  const staticRoutes = (properties.static_routes as string[]) || [];
  const tunnels = (properties.tunnels as Array<{
    name: string; status: string; vpn_ip: string; cpe_ip: string; routing: string;
  }>) || [];
  const [tunnelsOpen, setTunnelsOpen] = useState(false);

  return (
    <>
      <div className="detail-section">
        <div className="detail-section-title">Configuration</div>
        {staticRoutes.length > 0 && (
          <div className="detail-field">
            <span className="detail-field-label">Static Routes</span>
            <span className="detail-field-value mono">{staticRoutes.join(', ')}</span>
          </div>
        )}
        {tunnels.length > 0 && (
          <div className="detail-field">
            <span className="detail-field-label">Tunnels</span>
            <span className="detail-field-value">
              <span className="detail-tag detail-tag-cyan">{tunnels.length} tunnels</span>
            </span>
          </div>
        )}
      </div>
      {tunnels.length > 0 && (
        <div className="detail-section">
          <div
            className="detail-expandable-header"
            onClick={() => setTunnelsOpen(!tunnelsOpen)}
          >
            {tunnelsOpen ? <ChevronDown size={11} /> : <ChevronRight size={11} />}
            <span className="detail-item-name">IPSec Tunnels</span>
            <span className="badge badge-cyan">{tunnels.length}</span>
          </div>
          {tunnelsOpen && (
            <div className="detail-expandable-content">
              {tunnels.map((t, i) => (
                <div key={i} style={{ marginBottom: '8px' }}>
                  <div className="detail-field">
                    <span className="detail-field-label">{t.name || `Tunnel ${i + 1}`}</span>
                    <span className="detail-field-value">
                      <span className={`detail-tag ${t.status === 'UP' ? 'detail-tag-green' : 'detail-tag-red'}`}>
                        {t.status || 'N/A'}
                      </span>
                    </span>
                  </div>
                  {t.vpn_ip && (
                    <div className="detail-field">
                      <span className="detail-field-label">VPN IP</span>
                      <span className="detail-field-value mono">{t.vpn_ip}</span>
                    </div>
                  )}
                  {t.cpe_ip && (
                    <div className="detail-field">
                      <span className="detail-field-label">CPE IP</span>
                      <span className="detail-field-value mono">{t.cpe_ip}</span>
                    </div>
                  )}
                  {t.routing && (
                    <div className="detail-field">
                      <span className="detail-field-label">Routing</span>
                      <span className="detail-field-value">{t.routing}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </>
  );
}

/* --- Generic fallback --- */
function GenericContent({ properties }: { properties: Record<string, unknown> }) {
  const entries = Object.entries(properties).filter(([key]) => !HIDDEN_KEYS.has(key));
  if (entries.length === 0) return null;

  return (
    <div className="detail-section">
      <div className="detail-section-title">Properties</div>
      {entries.map(([key, value]) => (
        <div className="detail-field" key={key}>
          <span className="detail-field-label">{formatKey(key)}</span>
          <span className="detail-field-value">{formatValue(value)}</span>
        </div>
      ))}
    </div>
  );
}

/* ========== VCN Detail Tabs ========== */

type VcnTabId = 'security' | 'routing' | 'nsgs' | 'dhcp' | 'firewalls';

const VCN_TABS: { id: VcnTabId; label: string }[] = [
  { id: 'security', label: 'Security' },
  { id: 'routing', label: 'Routing' },
  { id: 'nsgs', label: 'NSGs' },
  { id: 'dhcp', label: 'DHCP' },
  { id: 'firewalls', label: 'Firewalls' },
];

function VcnDetailTabs({ detail }: { detail: VcnChildren }) {
  const [activeTab, setActiveTab] = useState<VcnTabId>('security');

  const handleTabClick = useCallback((e: React.MouseEvent, tabId: VcnTabId) => {
    e.stopPropagation();
    setActiveTab(tabId);
  }, []);

  return (
    <div className="detail-section">
      <div className="detail-tabs">
        {VCN_TABS.map((tab) => (
          <button
            key={tab.id}
            className={`detail-tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={(e) => handleTabClick(e, tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>
      {activeTab === 'security' && <VcnSecurityContent detail={detail} />}
      {activeTab === 'routing' && <VcnRoutingContent detail={detail} />}
      {activeTab === 'nsgs' && <VcnNsgContent detail={detail} />}
      {activeTab === 'dhcp' && <VcnDhcpContent detail={detail} />}
      {activeTab === 'firewalls' && <VcnFirewallContent detail={detail} />}
    </div>
  );
}

function VcnSecurityContent({ detail }: { detail: VcnChildren }) {
  const sls = detail.security_lists || [];
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  const toggle = useCallback((id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }));
  }, []);

  if (sls.length === 0) return <div className="detail-empty">No security lists</div>;

  return (
    <div className="detail-list">
      {sls.map((sl) => (
        <div key={sl.ocid}>
          <div className="detail-expandable-header" onClick={(e) => toggle(sl.ocid, e)}>
            {expanded[sl.ocid] ? <ChevronDown size={11} /> : <ChevronRight size={11} />}
            <span className="detail-item-name">{sl.display_name}</span>
            <span className="badge badge-cyan">{sl.rules?.length || 0} rules</span>
          </div>
          {expanded[sl.ocid] && sl.rules && (
            <div className="detail-expandable-content">
              {sl.rules.map((r, i) => (
                <div className="detail-rule-row" key={i}>
                  <span className={`detail-rule-direction ${r.direction === 'INGRESS' ? 'ingress' : 'egress'}`}>
                    {r.direction === 'INGRESS' ? 'IN' : 'OUT'}
                  </span>
                  <span>{protocolName(r.protocol)}</span>
                  <span>{r.source || r.destination || '*'}</span>
                  {r.destination_port_range_min !== undefined && (
                    <span>{portRange(r.destination_port_range_min, r.destination_port_range_max)}</span>
                  )}
                  {r.description && <span className="detail-rule-desc">{r.description}</span>}
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function VcnRoutingContent({ detail }: { detail: VcnChildren }) {
  const rts = detail.route_tables || [];
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  const toggle = useCallback((id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }));
  }, []);

  if (rts.length === 0) return <div className="detail-empty">No route tables</div>;

  return (
    <div className="detail-list">
      {rts.map((rt) => (
        <div key={rt.ocid}>
          <div className="detail-expandable-header" onClick={(e) => toggle(rt.ocid, e)}>
            {expanded[rt.ocid] ? <ChevronDown size={11} /> : <ChevronRight size={11} />}
            <span className="detail-item-name">{rt.display_name}</span>
            <span className="badge badge-amber">{rt.rules?.length || 0} rules</span>
          </div>
          {expanded[rt.ocid] && rt.rules && (
            <div className="detail-expandable-content">
              {rt.rules.map((r, i) => (
                <div className="detail-rule-row" key={i}>
                  <span>{r.destination}</span>
                  <span className="badge badge-cyan">{r.destination_type}</span>
                  <span>{truncateId(r.network_entity_id)}</span>
                  {r.description && <span className="detail-rule-desc">{r.description}</span>}
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function VcnNsgContent({ detail }: { detail: VcnChildren }) {
  const nsgs = detail.network_security_groups || [];
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  const toggle = useCallback((id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }));
  }, []);

  if (nsgs.length === 0) return <div className="detail-empty">No network security groups</div>;

  return (
    <div className="detail-list">
      {nsgs.map((nsg) => (
        <div key={nsg.ocid}>
          <div className="detail-expandable-header" onClick={(e) => toggle(nsg.ocid, e)}>
            {expanded[nsg.ocid] ? <ChevronDown size={11} /> : <ChevronRight size={11} />}
            <span className="detail-item-name">{nsg.display_name}</span>
            <span className="badge badge-purple">{nsg.rules?.length || 0} rules</span>
          </div>
          {expanded[nsg.ocid] && nsg.rules && (
            <div className="detail-expandable-content">
              {nsg.rules.map((r, i) => (
                <div className="detail-rule-row" key={i}>
                  <span className={`detail-rule-direction ${r.direction === 'INGRESS' ? 'ingress' : 'egress'}`}>
                    {r.direction === 'INGRESS' ? 'IN' : 'OUT'}
                  </span>
                  <span>{protocolName(r.protocol)}</span>
                  <span>{r.source || r.destination || '*'}</span>
                  {r.description && <span className="detail-rule-desc">{r.description}</span>}
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function VcnDhcpContent({ detail }: { detail: VcnChildren }) {
  const dhcp = detail.dhcp_options || [];
  if (dhcp.length === 0) return <div className="detail-empty">No DHCP options</div>;

  return (
    <div className="detail-list">
      {dhcp.map((d) => (
        <div className="detail-field" key={d.ocid}>
          <span className="detail-field-label">{d.display_name}</span>
          <span className="detail-field-value">{d.options?.length || 0} options</span>
        </div>
      ))}
    </div>
  );
}

function VcnFirewallContent({ detail }: { detail: VcnChildren }) {
  const fws = detail.network_firewalls || [];
  if (fws.length === 0) return <div className="detail-empty">No network firewalls</div>;

  return (
    <div className="detail-list">
      {fws.map((fw) => (
        <div className="detail-field" key={fw.ocid}>
          <span className="detail-field-label">{fw.display_name}</span>
          <span className="detail-field-value">{fw.ip_addresses?.join(', ') || '-'}</span>
        </div>
      ))}
    </div>
  );
}

/* ========== DRG Detail Tabs ========== */

type DrgTabId = 'attachments' | 'routes' | 'rpcs' | 'distributions';

const DRG_TABS: { id: DrgTabId; label: string }[] = [
  { id: 'attachments', label: 'Attachments' },
  { id: 'routes', label: 'Routes' },
  { id: 'rpcs', label: 'RPCs' },
  { id: 'distributions', label: 'Distributions' },
];

function DrgDetailTabs({ detail }: { detail: DrgChildren }) {
  const [activeTab, setActiveTab] = useState<DrgTabId>('attachments');

  const handleTabClick = useCallback((e: React.MouseEvent, tabId: DrgTabId) => {
    e.stopPropagation();
    setActiveTab(tabId);
  }, []);

  return (
    <div className="detail-section">
      <div className="detail-tabs">
        {DRG_TABS.map((tab) => (
          <button
            key={tab.id}
            className={`detail-tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={(e) => handleTabClick(e, tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>
      {activeTab === 'attachments' && <DrgAttachmentsContent detail={detail} />}
      {activeTab === 'routes' && <DrgRoutesContent detail={detail} />}
      {activeTab === 'rpcs' && <DrgRpcsContent detail={detail} />}
      {activeTab === 'distributions' && <DrgDistributionsContent detail={detail} />}
    </div>
  );
}

function DrgAttachmentsContent({ detail }: { detail: DrgChildren }) {
  const items = detail.attachments || [];
  if (items.length === 0) return <div className="detail-empty">No attachments</div>;

  return (
    <div className="detail-list">
      {items.map((a) => (
        <div className="detail-field" key={a.ocid}>
          <span className="detail-field-label">{a.display_name}</span>
          <span className="detail-field-value">
            <span className="detail-tag detail-tag-purple">{a.network_type}</span>
          </span>
        </div>
      ))}
    </div>
  );
}

function DrgRoutesContent({ detail }: { detail: DrgChildren }) {
  const rts = detail.route_tables || [];
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  const toggle = useCallback((id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }));
  }, []);

  if (rts.length === 0) return <div className="detail-empty">No DRG route tables</div>;

  return (
    <div className="detail-list">
      {rts.map((rt) => (
        <div key={rt.ocid}>
          <div className="detail-expandable-header" onClick={(e) => toggle(rt.ocid, e)}>
            {expanded[rt.ocid] ? <ChevronDown size={11} /> : <ChevronRight size={11} />}
            <span className="detail-item-name">{rt.display_name}</span>
            {rt.is_ecmp_enabled && <span className="badge badge-cyan">ECMP</span>}
            <span className="badge badge-amber">{rt.rules?.length || 0} rules</span>
          </div>
          {expanded[rt.ocid] && rt.rules && (
            <div className="detail-expandable-content">
              {rt.rules.map((r, i) => (
                <div className="detail-rule-row" key={i}>
                  <span>{r.destination}</span>
                  <span className="badge badge-cyan">{r.destination_type}</span>
                  <span>{truncateId(r.next_hop_drg_attachment_id)}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function DrgRpcsContent({ detail }: { detail: DrgChildren }) {
  const rpcs = detail.remote_peering_connections || [];
  if (rpcs.length === 0) return <div className="detail-empty">No remote peering connections</div>;

  return (
    <div className="detail-list">
      {rpcs.map((rpc) => (
        <div className="detail-field" key={rpc.ocid}>
          <span className="detail-field-label">{rpc.display_name}</span>
          <span className="detail-field-value">
            {rpc.peer_region && <span className="detail-tag detail-tag-cyan">{rpc.peer_region}</span>}
            <span
              className={`detail-tag ${
                rpc.peering_status === 'PEERED'
                  ? 'detail-tag-green'
                  : rpc.peering_status === 'REVOKED'
                  ? 'detail-tag-red'
                  : 'detail-tag-amber'
              }`}
            >
              {rpc.peering_status || 'N/A'}
            </span>
          </span>
        </div>
      ))}
    </div>
  );
}

function DrgDistributionsContent({ detail }: { detail: DrgChildren }) {
  const dists = detail.route_distributions || [];
  if (dists.length === 0) return <div className="detail-empty">No route distributions</div>;

  return (
    <div className="detail-list">
      {dists.map((d) => (
        <div className="detail-field" key={d.ocid}>
          <span className="detail-field-label">{d.display_name}</span>
          <span className="detail-field-value">
            <span className="detail-tag detail-tag-cyan">{d.distribution_type}</span>
          </span>
        </div>
      ))}
    </div>
  );
}

/* ========== Helpers ========== */

function formatResourceType(type: string): string {
  const map: Record<string, string> = {
    vcn: 'Virtual Cloud Network',
    subnet: 'Subnet',
    drg: 'Dynamic Routing Gateway',
    drg_route_table: 'DRG Route Table',
    drgRouteTable: 'DRG Route Table',
    route_table: 'Route Table',
    routeTable: 'Route Table',
    internet_gateway: 'Internet Gateway',
    nat_gateway: 'NAT Gateway',
    service_gateway: 'Service Gateway',
    gateway: 'Gateway',
    lpg: 'Local Peering Gateway',
    local_peering_gateway: 'Local Peering Gateway',
    rpc: 'Remote Peering Connection',
    remote_peering_connection: 'Remote Peering Connection',
    cpe: 'Customer Premises Equipment',
    ipsec_connection: 'IPSec Connection',
    ipsec_tunnel: 'IPSec Tunnel',
    network_firewall: 'Network Firewall',
    firewall: 'Network Firewall',
    load_balancer: 'Load Balancer',
    network_load_balancer: 'Network Load Balancer',
    cross_connect: 'Cross-Connect (FastConnect)',
    virtual_circuit: 'Virtual Circuit',
    compartment: 'Compartment',
    security_list: 'Security List',
    network_security_group: 'Network Security Group',
    drg_attachment: 'DRG Attachment',
    external: 'External Boundary',
  };
  return map[type] || type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

function formatKey(key: string): string {
  return key
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined) return '-';
  if (typeof value === 'boolean') return value ? 'Yes' : 'No';
  if (Array.isArray(value)) return value.length > 0 ? value.join(', ') : '-';
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
}

function truncateId(id: string): string {
  return id || '-';
}

function formatGatewayType(type: string): string {
  const map: Record<string, string> = {
    internet_gateway: 'IGW',
    nat_gateway: 'NAT',
    service_gateway: 'SGW',
    gateway: 'Gateway',
  };
  return map[type] || type;
}

function protocolName(proto: string): string {
  const map: Record<string, string> = { '6': 'TCP', '17': 'UDP', '1': 'ICMP', all: 'ALL' };
  return map[proto] || proto;
}

function portRange(min?: number, max?: number): string {
  if (min === undefined && max === undefined) return 'All';
  if (min === max) return String(min);
  return `${min}-${max}`;
}
