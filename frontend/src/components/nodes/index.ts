import { ExternalNode } from './ExternalNode';
import { VcnNode } from './VcnNode';
import { SubnetNode } from './SubnetNode';
import { RouteTableNode } from './RouteTableNode';
import { GatewayNode } from './GatewayNode';
import { DrgNode } from './DrgNode';
import { DrgRouteTableNode } from './DrgRouteTableNode';
import { LpgNode } from './LpgNode';
import { ConnectivityNode } from './ConnectivityNode';
import { FirewallNode } from './FirewallNode';
import { LoadBalancerNode } from './LoadBalancerNode';
import { CompartmentNode } from './CompartmentNode';

export const nodeTypes = {
  external: ExternalNode,
  gateway: GatewayNode,
  drg: DrgNode,
  drgRouteTable: DrgRouteTableNode,
  vcn: VcnNode,
  subnet: SubnetNode,
  routeTable: RouteTableNode,
  lpg: LpgNode,
  connectivity: ConnectivityNode,
  firewall: FirewallNode,
  loadBalancer: LoadBalancerNode,
  compartment: CompartmentNode,
};
