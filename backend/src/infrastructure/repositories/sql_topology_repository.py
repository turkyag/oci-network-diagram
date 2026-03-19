from __future__ import annotations

from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.entities.connectivity import (
    CPE,
    DRG,
    DRGAttachment,
    DRGRouteDistribution,
    CrossConnect,
    IPSecConnection,
    IPSecTunnel,
    LocalPeeringGateway,
    RemotePeeringConnection,
    VirtualCircuit,
)
from src.domain.entities.load_balancing import LoadBalancer, NetworkLoadBalancer
from src.domain.entities.network import (
    VCN,
    DHCPOptions,
    InternetGateway,
    NATGateway,
    PublicIP,
    ServiceGateway,
    Subnet,
)
from src.domain.entities.routing import DRGRouteRule, DRGRouteTable, RouteRule, RouteTable
from src.domain.entities.security import (
    NSGRule,
    NetworkFirewall,
    NetworkSecurityGroup,
    SecurityList,
    SecurityRule,
)
from src.domain.entities.topology import Topology
from src.domain.repositories import TopologyRepository
from src.infrastructure.database.models import (
    CPEModel,
    CrossConnectModel,
    DHCPOptionsModel,
    DRGAttachmentModel,
    DRGModel,
    DRGRouteDistributionModel,
    DRGRouteRuleModel,
    DRGRouteTableModel,
    InternetGatewayModel,
    IPSecConnectionModel,
    IPSecTunnelModel,
    LoadBalancerModel,
    LocalPeeringGatewayModel,
    NATGatewayModel,
    NSGRuleModel,
    NetworkFirewallModel,
    NetworkLoadBalancerModel,
    NetworkSecurityGroupModel,
    PublicIPModel,
    RemotePeeringConnectionModel,
    RouteRuleModel,
    RouteTableModel,
    SecurityListModel,
    SecurityRuleModel,
    ServiceGatewayModel,
    SubnetModel,
    TopologyModel,
    VCNModel,
    VirtualCircuitModel,
)


class SqlTopologyRepository(TopologyRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, topology_id: int) -> Topology | None:
        stmt = (
            select(TopologyModel)
            .where(TopologyModel.id == topology_id)
            .options(
                selectinload(TopologyModel.vcns),
                selectinload(TopologyModel.subnets),
                selectinload(TopologyModel.internet_gateways),
                selectinload(TopologyModel.nat_gateways),
                selectinload(TopologyModel.service_gateways),
                selectinload(TopologyModel.drgs),
                selectinload(TopologyModel.drg_attachments),
                selectinload(TopologyModel.drg_route_tables),
                selectinload(TopologyModel.drg_route_rules),
                selectinload(TopologyModel.remote_peering_connections),
                selectinload(TopologyModel.local_peering_gateways),
                selectinload(TopologyModel.route_tables),
                selectinload(TopologyModel.route_rules),
                selectinload(TopologyModel.security_lists),
                selectinload(TopologyModel.security_rules),
                selectinload(TopologyModel.network_security_groups),
                selectinload(TopologyModel.nsg_rules),
                selectinload(TopologyModel.load_balancers),
                selectinload(TopologyModel.network_load_balancers),
                selectinload(TopologyModel.ipsec_connections),
                selectinload(TopologyModel.cpes),
                selectinload(TopologyModel.ipsec_tunnels),
                selectinload(TopologyModel.network_firewalls),
                selectinload(TopologyModel.dhcp_options),
                selectinload(TopologyModel.public_ips),
                selectinload(TopologyModel.cross_connects),
                selectinload(TopologyModel.virtual_circuits),
                selectinload(TopologyModel.drg_route_distributions),
            )
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def list_all(self) -> list[Topology]:
        stmt = (
            select(TopologyModel)
            .options(
                selectinload(TopologyModel.vcns),
                selectinload(TopologyModel.drgs),
            )
            .order_by(TopologyModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [
            Topology(
                id=m.id,
                name=m.name,
                description=m.description,
                created_at=m.created_at,
                updated_at=m.updated_at,
                vcns=[self._vcn_to_entity(v) for v in m.vcns],
                drgs=[self._drg_to_entity(d) for d in m.drgs],
            )
            for m in models
        ]

    async def save(self, topology: Topology) -> Topology:
        if topology.id:
            stmt = select(TopologyModel).where(TopologyModel.id == topology.id)
            result = await self._session.execute(stmt)
            model = result.scalar_one_or_none()
            if model:
                model.name = topology.name
                model.description = topology.description
                model.updated_at = datetime.utcnow()
            else:
                model = TopologyModel(
                    name=topology.name,
                    description=topology.description,
                )
                self._session.add(model)
        else:
            model = TopologyModel(
                name=topology.name,
                description=topology.description,
            )
            self._session.add(model)

        await self._session.flush()
        await self._session.commit()

        topology.id = model.id
        topology.created_at = model.created_at
        topology.updated_at = model.updated_at
        return topology

    async def delete(self, topology_id: int) -> bool:
        stmt = select(TopologyModel).where(TopologyModel.id == topology_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return False
        await self._session.delete(model)
        await self._session.commit()
        return True

    async def import_topology_data(self, topology_id: int, data: dict) -> Topology:
        await self._clear_resources(topology_id)
        await self._bulk_insert(topology_id, data)
        await self._session.commit()
        return await self.get_by_id(topology_id)

    async def _clear_resources(self, topology_id: int) -> None:
        tables = [
            VCNModel, SubnetModel, InternetGatewayModel, NATGatewayModel,
            ServiceGatewayModel, DRGModel, DRGAttachmentModel, DRGRouteTableModel,
            DRGRouteRuleModel, RemotePeeringConnectionModel, LocalPeeringGatewayModel,
            RouteTableModel, RouteRuleModel, SecurityListModel, SecurityRuleModel,
            NetworkSecurityGroupModel, NSGRuleModel, LoadBalancerModel,
            NetworkLoadBalancerModel, IPSecConnectionModel, CPEModel, IPSecTunnelModel,
            NetworkFirewallModel, DHCPOptionsModel, PublicIPModel,
            CrossConnectModel, VirtualCircuitModel, DRGRouteDistributionModel,
        ]
        for table in tables:
            await self._session.execute(
                delete(table).where(table.topology_id == topology_id)
            )

    async def _bulk_insert(self, topology_id: int, data: dict) -> None:
        mapping = {
            "vcns": VCNModel,
            "subnets": SubnetModel,
            "internet_gateways": InternetGatewayModel,
            "nat_gateways": NATGatewayModel,
            "service_gateways": ServiceGatewayModel,
            "drgs": DRGModel,
            "drg_attachments": DRGAttachmentModel,
            "drg_route_tables": DRGRouteTableModel,
            "drg_route_rules": DRGRouteRuleModel,
            "remote_peering_connections": RemotePeeringConnectionModel,
            "local_peering_gateways": LocalPeeringGatewayModel,
            "route_tables": RouteTableModel,
            "route_rules": RouteRuleModel,
            "security_lists": SecurityListModel,
            "security_rules": SecurityRuleModel,
            "network_security_groups": NetworkSecurityGroupModel,
            "nsg_rules": NSGRuleModel,
            "load_balancers": LoadBalancerModel,
            "network_load_balancers": NetworkLoadBalancerModel,
            "ipsec_connections": IPSecConnectionModel,
            "cpes": CPEModel,
            "ipsec_tunnels": IPSecTunnelModel,
            "network_firewalls": NetworkFirewallModel,
            "dhcp_options": DHCPOptionsModel,
            "public_ips": PublicIPModel,
            "cross_connects": CrossConnectModel,
            "virtual_circuits": VirtualCircuitModel,
            "drg_route_distributions": DRGRouteDistributionModel,
        }

        for key, model_cls in mapping.items():
            items = data.get(key, [])
            if not items:
                continue
            # Get valid column names for the model
            valid_cols = {c.key for c in model_cls.__table__.columns}
            for item in items:
                item.pop("id", None)
                item["topology_id"] = topology_id
                filtered = {k: v for k, v in item.items() if k in valid_cols}
                self._session.add(model_cls(**filtered))

    def _to_entity(self, m: TopologyModel) -> Topology:
        return Topology(
            id=m.id,
            name=m.name,
            description=m.description,
            created_at=m.created_at,
            updated_at=m.updated_at,
            vcns=[self._vcn_to_entity(v) for v in m.vcns],
            subnets=[Subnet(id=s.id, topology_id=s.topology_id, ocid=s.ocid, vcn_id=s.vcn_id, display_name=s.display_name, cidr_block=s.cidr_block, subnet_domain_name=s.subnet_domain_name, route_table_id=s.route_table_id, security_list_ids=s.security_list_ids or [], prohibit_public_ip_on_vnic=s.prohibit_public_ip_on_vnic) for s in m.subnets],
            internet_gateways=[InternetGateway(id=g.id, topology_id=g.topology_id, ocid=g.ocid, vcn_id=g.vcn_id, display_name=g.display_name, is_enabled=g.is_enabled) for g in m.internet_gateways],
            nat_gateways=[NATGateway(id=g.id, topology_id=g.topology_id, ocid=g.ocid, vcn_id=g.vcn_id, display_name=g.display_name, public_ip=g.public_ip) for g in m.nat_gateways],
            service_gateways=[ServiceGateway(id=g.id, topology_id=g.topology_id, ocid=g.ocid, vcn_id=g.vcn_id, display_name=g.display_name, services=g.services or []) for g in m.service_gateways],
            drgs=[self._drg_to_entity(d) for d in m.drgs],
            drg_attachments=[DRGAttachment(id=a.id, topology_id=a.topology_id, ocid=a.ocid, drg_id=a.drg_id, display_name=a.display_name, network_type=a.network_type, network_id=a.network_id) for a in m.drg_attachments],
            drg_route_tables=[DRGRouteTable(id=t.id, topology_id=t.topology_id, ocid=t.ocid, drg_id=t.drg_id, display_name=t.display_name, is_ecmp_enabled=t.is_ecmp_enabled) for t in m.drg_route_tables],
            drg_route_rules=[DRGRouteRule(id=r.id, topology_id=r.topology_id, drg_route_table_id=r.drg_route_table_id, destination=r.destination, destination_type=r.destination_type, next_hop_drg_attachment_id=r.next_hop_drg_attachment_id) for r in m.drg_route_rules],
            remote_peering_connections=[RemotePeeringConnection(id=r.id, topology_id=r.topology_id, ocid=r.ocid, drg_id=r.drg_id, display_name=r.display_name, peer_id=r.peer_id, peer_region=r.peer_region, peering_status=r.peering_status) for r in m.remote_peering_connections],
            local_peering_gateways=[LocalPeeringGateway(id=l.id, topology_id=l.topology_id, ocid=l.ocid, vcn_id=l.vcn_id, display_name=l.display_name, peer_id=l.peer_id, peering_status=l.peering_status) for l in m.local_peering_gateways],
            route_tables=[RouteTable(id=t.id, topology_id=t.topology_id, ocid=t.ocid, vcn_id=t.vcn_id, display_name=t.display_name) for t in m.route_tables],
            route_rules=[RouteRule(id=r.id, topology_id=r.topology_id, route_table_id=r.route_table_id, destination=r.destination, destination_type=r.destination_type, network_entity_id=r.network_entity_id, description=r.description) for r in m.route_rules],
            security_lists=[SecurityList(id=s.id, topology_id=s.topology_id, ocid=s.ocid, vcn_id=s.vcn_id, display_name=s.display_name) for s in m.security_lists],
            security_rules=[SecurityRule(id=r.id, topology_id=r.topology_id, security_list_id=r.security_list_id, direction=r.direction, protocol=r.protocol, source=r.source, destination=r.destination, source_port_range_min=r.source_port_range_min, source_port_range_max=r.source_port_range_max, destination_port_range_min=r.destination_port_range_min, destination_port_range_max=r.destination_port_range_max, description=r.description) for r in m.security_rules],
            network_security_groups=[NetworkSecurityGroup(id=n.id, topology_id=n.topology_id, ocid=n.ocid, vcn_id=n.vcn_id, display_name=n.display_name) for n in m.network_security_groups],
            nsg_rules=[NSGRule(id=r.id, topology_id=r.topology_id, nsg_id=r.nsg_id, direction=r.direction, protocol=r.protocol, source=r.source, destination=r.destination, source_type=r.source_type, destination_type=r.destination_type, source_port_range_min=r.source_port_range_min, source_port_range_max=r.source_port_range_max, destination_port_range_min=r.destination_port_range_min, destination_port_range_max=r.destination_port_range_max, description=r.description) for r in m.nsg_rules],
            load_balancers=[LoadBalancer(id=l.id, topology_id=l.topology_id, ocid=l.ocid, display_name=l.display_name, ip_addresses=l.ip_addresses or [], shape=l.shape, subnet_ids=l.subnet_ids or [], is_private=l.is_private) for l in m.load_balancers],
            network_load_balancers=[NetworkLoadBalancer(id=n.id, topology_id=n.topology_id, ocid=n.ocid, display_name=n.display_name, ip_addresses=n.ip_addresses or [], subnet_ids=n.subnet_ids or [], is_private=n.is_private, is_preserve_source=n.is_preserve_source) for n in m.network_load_balancers],
            ipsec_connections=[IPSecConnection(id=i.id, topology_id=i.topology_id, ocid=i.ocid, drg_id=i.drg_id, cpe_id=i.cpe_id, display_name=i.display_name, static_routes=i.static_routes or [], cpe_local_identifier=i.cpe_local_identifier) for i in m.ipsec_connections],
            cpes=[CPE(id=c.id, topology_id=c.topology_id, ocid=c.ocid, display_name=c.display_name, ip_address=c.ip_address, cpe_device_shape_id=c.cpe_device_shape_id) for c in m.cpes],
            ipsec_tunnels=[IPSecTunnel(id=t.id, topology_id=t.topology_id, ocid=t.ocid, ipsec_connection_id=t.ipsec_connection_id, display_name=t.display_name, status=t.status, vpn_ip=t.vpn_ip, cpe_ip=t.cpe_ip, routing=t.routing, bgp_info=t.bgp_info or {}) for t in m.ipsec_tunnels],
            network_firewalls=[NetworkFirewall(id=f.id, topology_id=f.topology_id, ocid=f.ocid, display_name=f.display_name, subnet_id=f.subnet_id, vcn_id=f.vcn_id, policy_id=f.policy_id, ip_addresses=f.ip_addresses or [], lifecycle_state=f.lifecycle_state) for f in m.network_firewalls],
            dhcp_options=[DHCPOptions(id=d.id, topology_id=d.topology_id, ocid=d.ocid, vcn_id=d.vcn_id, display_name=d.display_name, options=d.options or []) for d in m.dhcp_options],
            public_ips=[PublicIP(id=p.id, topology_id=p.topology_id, ocid=p.ocid, display_name=p.display_name, ip_address=p.ip_address, lifetime=p.lifetime, assigned_entity_id=p.assigned_entity_id, assigned_entity_type=p.assigned_entity_type, compartment_id=p.compartment_id) for p in m.public_ips],
            cross_connects=[CrossConnect(id=c.id, topology_id=c.topology_id, ocid=c.ocid, display_name=c.display_name, compartment_id=c.compartment_id, location_name=c.location_name, port_speed_shape_name=c.port_speed_shape_name, cross_connect_group_id=c.cross_connect_group_id, lifecycle_state=c.lifecycle_state) for c in m.cross_connects],
            virtual_circuits=[VirtualCircuit(id=v.id, topology_id=v.topology_id, ocid=v.ocid, display_name=v.display_name, compartment_id=v.compartment_id, type=v.type, bandwidth_shape_name=v.bandwidth_shape_name, bgp_session_state=v.bgp_session_state, gateway_id=v.gateway_id, provider_name=v.provider_name, region=v.region, lifecycle_state=v.lifecycle_state) for v in m.virtual_circuits],
            drg_route_distributions=[DRGRouteDistribution(id=d.id, topology_id=d.topology_id, ocid=d.ocid, drg_id=d.drg_id, display_name=d.display_name, distribution_type=d.distribution_type) for d in m.drg_route_distributions],
        )

    @staticmethod
    def _vcn_to_entity(v: VCNModel) -> VCN:
        return VCN(id=v.id, topology_id=v.topology_id, ocid=v.ocid, display_name=v.display_name, cidr_blocks=v.cidr_blocks or [], dns_label=v.dns_label, compartment_id=v.compartment_id)

    @staticmethod
    def _drg_to_entity(d: DRGModel) -> DRG:
        return DRG(id=d.id, topology_id=d.topology_id, ocid=d.ocid, display_name=d.display_name, compartment_id=d.compartment_id)
