from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
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


@dataclass
class Topology:
    """Aggregate root representing one network topology."""

    id: int | None
    name: str
    description: str
    metadata_json: dict | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    vcns: list[VCN] = field(default_factory=list)
    subnets: list[Subnet] = field(default_factory=list)
    internet_gateways: list[InternetGateway] = field(default_factory=list)
    nat_gateways: list[NATGateway] = field(default_factory=list)
    service_gateways: list[ServiceGateway] = field(default_factory=list)
    drgs: list[DRG] = field(default_factory=list)
    drg_attachments: list[DRGAttachment] = field(default_factory=list)
    drg_route_tables: list[DRGRouteTable] = field(default_factory=list)
    drg_route_rules: list[DRGRouteRule] = field(default_factory=list)
    remote_peering_connections: list[RemotePeeringConnection] = field(default_factory=list)
    local_peering_gateways: list[LocalPeeringGateway] = field(default_factory=list)
    route_tables: list[RouteTable] = field(default_factory=list)
    route_rules: list[RouteRule] = field(default_factory=list)
    security_lists: list[SecurityList] = field(default_factory=list)
    security_rules: list[SecurityRule] = field(default_factory=list)
    network_security_groups: list[NetworkSecurityGroup] = field(default_factory=list)
    nsg_rules: list[NSGRule] = field(default_factory=list)
    load_balancers: list[LoadBalancer] = field(default_factory=list)
    network_load_balancers: list[NetworkLoadBalancer] = field(default_factory=list)
    ipsec_connections: list[IPSecConnection] = field(default_factory=list)
    cpes: list[CPE] = field(default_factory=list)
    ipsec_tunnels: list[IPSecTunnel] = field(default_factory=list)
    network_firewalls: list[NetworkFirewall] = field(default_factory=list)
    dhcp_options: list[DHCPOptions] = field(default_factory=list)
    public_ips: list[PublicIP] = field(default_factory=list)
    cross_connects: list[CrossConnect] = field(default_factory=list)
    virtual_circuits: list[VirtualCircuit] = field(default_factory=list)
    drg_route_distributions: list[DRGRouteDistribution] = field(default_factory=list)

    @classmethod
    def create(cls, name: str, description: str) -> Topology:
        return cls(
            id=None,
            name=name,
            description=description,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
