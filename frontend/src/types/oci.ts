/* ============================================================
   OCI Network Diagram — Domain Types
   ============================================================ */

// --- Topology ---
export interface TopologySummary {
  id: number;
  name: string;
  description: string;
  vcn_count: number;
  drg_count: number;
  subnet_count?: number;
  created_at: string;
  updated_at?: string;
}

export interface Topology {
  id: number;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface TopologyDetail extends Topology {
  vcns: VCN[];
  subnets: Subnet[];
  internet_gateways: InternetGateway[];
  nat_gateways: NATGateway[];
  service_gateways: ServiceGateway[];
  drgs: DRG[];
  drg_attachments: DRGAttachment[];
  drg_route_tables: DRGRouteTable[];
  drg_route_rules: DRGRouteRule[];
  remote_peering_connections: RemotePeeringConnection[];
  local_peering_gateways: LocalPeeringGateway[];
  route_tables: RouteTable[];
  route_rules: RouteRule[];
  security_lists: SecurityList[];
  security_rules: SecurityRule[];
  network_security_groups: NetworkSecurityGroup[];
  nsg_rules: NSGRule[];
  load_balancers: LoadBalancer[];
  network_load_balancers: NetworkLoadBalancer[];
  ipsec_connections: IPSecConnection[];
  cpes: CPE[];
  ipsec_tunnels: IPSecTunnel[];
}

// --- VCN ---
export interface VCN {
  id: string;
  topology_id: string;
  ocid: string;
  name: string;
  compartment_id: string;
  cidr_blocks: string[];
  dns_label: string;
  lifecycle_state: string;
  created_at: string;
}

// --- Subnet ---
export interface Subnet {
  id: string;
  topology_id: string;
  vcn_id: string;
  ocid: string;
  name: string;
  cidr_block: string;
  dns_label: string;
  subnet_domain_name: string;
  prohibit_public_ip_on_vnic: boolean;
  route_table_id: string;
  security_list_ids: string[];
  lifecycle_state: string;
  created_at: string;
}

// --- Gateways ---
export interface InternetGateway {
  id: string;
  topology_id: string;
  vcn_id: string;
  ocid: string;
  name: string;
  is_enabled: boolean;
  lifecycle_state: string;
  created_at: string;
}

export interface NATGateway {
  id: string;
  topology_id: string;
  vcn_id: string;
  ocid: string;
  name: string;
  nat_ip: string;
  is_enabled: boolean;
  lifecycle_state: string;
  created_at: string;
}

export interface ServiceGateway {
  id: string;
  topology_id: string;
  vcn_id: string;
  ocid: string;
  name: string;
  services: string[];
  lifecycle_state: string;
  created_at: string;
}

// --- DRG ---
export interface DRG {
  id: string;
  topology_id: string;
  ocid: string;
  name: string;
  compartment_id: string;
  lifecycle_state: string;
  created_at: string;
}

export interface DRGAttachment {
  id: string;
  topology_id: string;
  drg_id: string;
  ocid: string;
  name: string;
  network_id: string;
  network_type: string;
  drg_route_table_id: string;
  lifecycle_state: string;
  created_at: string;
}

export interface DRGRouteTable {
  id: string;
  topology_id: string;
  drg_id: string;
  ocid: string;
  name: string;
  import_drg_route_distribution_id: string;
  is_ecmp_enabled: boolean;
  lifecycle_state: string;
  created_at: string;
}

export interface DRGRouteRule {
  id: string;
  topology_id: string;
  drg_route_table_id: string;
  destination: string;
  destination_type: string;
  next_hop_drg_attachment_id: string;
  is_conflict: boolean;
  is_blackhole: boolean;
  route_provenance: string;
}

// --- Peering ---
export interface RemotePeeringConnection {
  id: string;
  topology_id: string;
  drg_id: string;
  ocid: string;
  name: string;
  peer_id: string;
  peer_region_name: string;
  peer_tenancy_id: string;
  peering_status: string;
  is_cross_tenancy_peering: boolean;
  lifecycle_state: string;
  created_at: string;
}

export interface LocalPeeringGateway {
  id: string;
  topology_id: string;
  vcn_id: string;
  ocid: string;
  name: string;
  peer_id: string;
  peering_status: string;
  is_cross_tenancy_peering: boolean;
  route_table_id: string;
  lifecycle_state: string;
  created_at: string;
}

// --- Routing ---
export interface RouteTable {
  id: string;
  topology_id: string;
  vcn_id: string;
  ocid: string;
  name: string;
  lifecycle_state: string;
  created_at: string;
}

export interface RouteRule {
  id: string;
  topology_id: string;
  route_table_id: string;
  destination: string;
  destination_type: string;
  network_entity_id: string;
  description: string;
}

// --- Security ---
export interface SecurityList {
  id: string;
  topology_id: string;
  vcn_id: string;
  ocid: string;
  name: string;
  lifecycle_state: string;
  created_at: string;
}

export interface SecurityRule {
  id: string;
  topology_id: string;
  security_list_id: string;
  direction: string;
  protocol: string;
  source: string;
  destination: string;
  source_type: string;
  destination_type: string;
  is_stateless: boolean;
  tcp_options: string | null;
  udp_options: string | null;
  icmp_options: string | null;
  description: string;
}

export interface NetworkSecurityGroup {
  id: string;
  topology_id: string;
  vcn_id: string;
  ocid: string;
  name: string;
  lifecycle_state: string;
  created_at: string;
}

export interface NSGRule {
  id: string;
  topology_id: string;
  nsg_id: string;
  direction: string;
  protocol: string;
  source: string;
  destination: string;
  source_type: string;
  destination_type: string;
  is_stateless: boolean;
  tcp_options: string | null;
  udp_options: string | null;
  icmp_options: string | null;
  description: string;
}

// --- Load Balancers ---
export interface LoadBalancer {
  id: string;
  topology_id: string;
  ocid: string;
  name: string;
  shape_name: string;
  ip_addresses: string[];
  is_private: boolean;
  subnet_ids: string[];
  nsg_ids: string[];
  lifecycle_state: string;
  created_at: string;
}

export interface NetworkLoadBalancer {
  id: string;
  topology_id: string;
  ocid: string;
  name: string;
  ip_addresses: string[];
  is_private: boolean;
  subnet_id: string;
  nsg_ids: string[];
  is_preserve_source_destination: boolean;
  lifecycle_state: string;
  created_at: string;
}

// --- VPN / IPSec ---
export interface IPSecConnection {
  id: string;
  topology_id: string;
  drg_id: string;
  cpe_id: string;
  ocid: string;
  name: string;
  static_routes: string[];
  cpe_local_identifier: string;
  cpe_local_identifier_type: string;
  lifecycle_state: string;
  created_at: string;
}

export interface CPE {
  id: string;
  topology_id: string;
  ocid: string;
  name: string;
  ip_address: string;
  cpe_device_shape_id: string;
  lifecycle_state: string;
  created_at: string;
}

export interface IPSecTunnel {
  id: string;
  topology_id: string;
  ipsec_connection_id: string;
  ocid: string;
  name: string;
  status: string;
  ike_version: string;
  routing: string;
  bgp_session_info: string | null;
  encryption_domain_config: string | null;
  vpn_ip: string;
  cpe_ip: string;
  lifecycle_state: string;
  created_at: string;
}

// --- New domain types ---
export interface NetworkFirewall {
  ocid: string;
  display_name: string;
  subnet_id: string;
  policy_id?: string;
  ip_addresses?: string[];
}

export interface DHCPOptions {
  ocid: string;
  display_name: string;
  options: unknown[];
}

export interface PublicIP {
  ocid: string;
  display_name: string;
  ip_address: string;
  scope: string;
  lifetime: string;
}

export interface CrossConnect {
  ocid: string;
  display_name: string;
  port_speed_shape_name: string;
  location_name: string;
  lifecycle_state: string;
}

export interface VirtualCircuit {
  ocid: string;
  display_name: string;
  bandwidth_shape_name: string;
  bgp_management: string;
  type: string;
  lifecycle_state: string;
}

export interface DRGRouteDistribution {
  ocid: string;
  display_name: string;
  distribution_type: string;
}

// --- VCN Children (embedded in VCN node data) ---
export interface VcnChildren {
  subnets: Array<{
    ocid: string;
    display_name: string;
    cidr_block: string;
    subnet_domain_name?: string;
    route_table_id?: string;
    security_list_ids?: string[];
  }>;
  internet_gateways: Array<{
    ocid: string;
    display_name: string;
    is_enabled: boolean;
  }>;
  nat_gateways: Array<{
    ocid: string;
    display_name: string;
    public_ip: string;
  }>;
  service_gateways: Array<{
    ocid: string;
    display_name: string;
    services: string[];
  }>;
  security_lists: Array<{
    ocid: string;
    display_name: string;
    rules: Array<{
      direction: string;
      protocol: string;
      source?: string;
      destination?: string;
      description?: string;
      destination_port_range_min?: number;
      destination_port_range_max?: number;
    }>;
  }>;
  network_security_groups: Array<{
    ocid: string;
    display_name: string;
    rules: Array<{
      direction: string;
      protocol: string;
      source?: string;
      destination?: string;
      description?: string;
    }>;
  }>;
  route_tables: Array<{
    ocid: string;
    display_name: string;
    rules: Array<{
      destination: string;
      destination_type: string;
      network_entity_id: string;
      description?: string;
    }>;
  }>;
  local_peering_gateways: Array<{
    ocid: string;
    display_name: string;
    peer_id?: string;
    peering_status?: string;
  }>;
  dhcp_options: Array<{
    ocid: string;
    display_name: string;
    options: unknown[];
  }>;
  network_firewalls: Array<{
    ocid: string;
    display_name: string;
    subnet_id: string;
    policy_id?: string;
    ip_addresses?: string[];
  }>;
}

// --- DRG Children (embedded in DRG node data) ---
export interface DrgChildren {
  attachments: Array<{
    ocid: string;
    display_name: string;
    network_type: string;
    network_id: string;
  }>;
  route_tables: Array<{
    ocid: string;
    display_name: string;
    is_ecmp_enabled: boolean;
    rules: Array<{
      destination: string;
      destination_type: string;
      next_hop_drg_attachment_id: string;
    }>;
  }>;
  remote_peering_connections: Array<{
    ocid: string;
    display_name: string;
    peer_id?: string;
    peer_region?: string;
    peering_status?: string;
  }>;
  route_distributions: Array<{
    ocid: string;
    display_name: string;
    distribution_type: string;
  }>;
}

// --- React Flow Diagram ---
export interface DiagramNodeData {
  label: string;
  type: string;
  resource_type: string;
  resource_id: string;
  properties: Record<string, unknown>;
  detail?: Record<string, unknown[]>;
  children?: VcnChildren | DrgChildren;  // keep for backwards compat
  [key: string]: unknown;
}

export interface DiagramNode {
  id: string;
  type: string;
  position: { x: number; y: number };
  data: DiagramNodeData;
  parentId?: string;
  extent?: 'parent' | undefined;
  style?: Record<string, string | number>;
}

export interface DiagramEdge {
  id: string;
  source: string;
  target: string;
  type?: string;
  animated?: boolean;
  label?: string;
  style?: Record<string, string | number>;
  className?: string;
  data?: Record<string, unknown>;
}

export interface DiagramData {
  nodes: DiagramNode[];
  edges: DiagramEdge[];
  warnings?: FlowWarning[];
}

// --- Flow Analysis ---
export interface FlowWarning {
  severity: 'info' | 'warning' | 'error';
  code: string;
  message: string;
  affected_resources: string[];
}

export interface AnalysisData {
  flows: Array<{
    subnet_ocid: string;
    subnet_name: string;
    route_table_ocid: string;
    route_table_name: string;
    rules: Array<{
      destination: string;
      destination_type: string;
      target_type: string;
      target_ocid: string;
      target_name: string;
      is_default_route: boolean;
      is_local: boolean;
    }>;
  }>;
  drg_flows: Array<Record<string, unknown>>;
  warnings: FlowWarning[];
  subnet_to_route_table: Record<string, string>;
  route_table_to_subnets: Record<string, string[]>;
  gateway_to_route_rules: Record<string, string[]>;
}
