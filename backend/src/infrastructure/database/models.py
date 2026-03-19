from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class TopologyModel(Base):
    __tablename__ = "topologies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    vcns: Mapped[list[VCNModel]] = relationship(back_populates="topology", cascade="all, delete-orphan")
    subnets: Mapped[list[SubnetModel]] = relationship(back_populates="topology", cascade="all, delete-orphan")
    internet_gateways: Mapped[list[InternetGatewayModel]] = relationship(back_populates="topology", cascade="all, delete-orphan")
    nat_gateways: Mapped[list[NATGatewayModel]] = relationship(back_populates="topology", cascade="all, delete-orphan")
    service_gateways: Mapped[list[ServiceGatewayModel]] = relationship(back_populates="topology", cascade="all, delete-orphan")
    drgs: Mapped[list[DRGModel]] = relationship(back_populates="topology", cascade="all, delete-orphan")
    drg_attachments: Mapped[list[DRGAttachmentModel]] = relationship(back_populates="topology", cascade="all, delete-orphan")
    drg_route_tables: Mapped[list[DRGRouteTableModel]] = relationship(back_populates="topology", cascade="all, delete-orphan")
    drg_route_rules: Mapped[list[DRGRouteRuleModel]] = relationship(back_populates="topology", cascade="all, delete-orphan")
    remote_peering_connections: Mapped[list[RemotePeeringConnectionModel]] = relationship(back_populates="topology", cascade="all, delete-orphan")
    local_peering_gateways: Mapped[list[LocalPeeringGatewayModel]] = relationship(back_populates="topology", cascade="all, delete-orphan")
    route_tables: Mapped[list[RouteTableModel]] = relationship(back_populates="topology", cascade="all, delete-orphan")
    route_rules: Mapped[list[RouteRuleModel]] = relationship(back_populates="topology", cascade="all, delete-orphan")
    security_lists: Mapped[list[SecurityListModel]] = relationship(back_populates="topology", cascade="all, delete-orphan")
    security_rules: Mapped[list[SecurityRuleModel]] = relationship(back_populates="topology", cascade="all, delete-orphan")
    network_security_groups: Mapped[list[NetworkSecurityGroupModel]] = relationship(back_populates="topology", cascade="all, delete-orphan")
    nsg_rules: Mapped[list[NSGRuleModel]] = relationship(back_populates="topology", cascade="all, delete-orphan")
    load_balancers: Mapped[list[LoadBalancerModel]] = relationship(back_populates="topology", cascade="all, delete-orphan")
    network_load_balancers: Mapped[list[NetworkLoadBalancerModel]] = relationship(back_populates="topology", cascade="all, delete-orphan")
    ipsec_connections: Mapped[list[IPSecConnectionModel]] = relationship(back_populates="topology", cascade="all, delete-orphan")
    cpes: Mapped[list[CPEModel]] = relationship(back_populates="topology", cascade="all, delete-orphan")
    ipsec_tunnels: Mapped[list[IPSecTunnelModel]] = relationship(back_populates="topology", cascade="all, delete-orphan")
    network_firewalls: Mapped[list[NetworkFirewallModel]] = relationship(back_populates="topology", cascade="all, delete-orphan")
    dhcp_options: Mapped[list[DHCPOptionsModel]] = relationship(back_populates="topology", cascade="all, delete-orphan")
    public_ips: Mapped[list[PublicIPModel]] = relationship(back_populates="topology", cascade="all, delete-orphan")
    cross_connects: Mapped[list[CrossConnectModel]] = relationship(back_populates="topology", cascade="all, delete-orphan")
    virtual_circuits: Mapped[list[VirtualCircuitModel]] = relationship(back_populates="topology", cascade="all, delete-orphan")
    drg_route_distributions: Mapped[list[DRGRouteDistributionModel]] = relationship(back_populates="topology", cascade="all, delete-orphan")


class VCNModel(Base):
    __tablename__ = "vcns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topology_id: Mapped[int] = mapped_column(ForeignKey("topologies.id", ondelete="CASCADE"), index=True)
    ocid: Mapped[str] = mapped_column(String(255), index=True)
    display_name: Mapped[str] = mapped_column(String(255))
    cidr_blocks: Mapped[list] = mapped_column(JSON, default=list)
    dns_label: Mapped[str] = mapped_column(String(255), default="")
    compartment_id: Mapped[str] = mapped_column(String(255), default="")

    topology: Mapped[TopologyModel] = relationship(back_populates="vcns")


class SubnetModel(Base):
    __tablename__ = "subnets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topology_id: Mapped[int] = mapped_column(ForeignKey("topologies.id", ondelete="CASCADE"), index=True)
    ocid: Mapped[str] = mapped_column(String(255), index=True)
    vcn_id: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(255))
    cidr_block: Mapped[str] = mapped_column(String(50))
    subnet_domain_name: Mapped[str] = mapped_column(String(255), default="")
    route_table_id: Mapped[str] = mapped_column(String(255), default="")
    security_list_ids: Mapped[list] = mapped_column(JSON, default=list)
    prohibit_public_ip_on_vnic: Mapped[bool] = mapped_column(Boolean, default=True)

    topology: Mapped[TopologyModel] = relationship(back_populates="subnets")


class InternetGatewayModel(Base):
    __tablename__ = "internet_gateways"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topology_id: Mapped[int] = mapped_column(ForeignKey("topologies.id", ondelete="CASCADE"), index=True)
    ocid: Mapped[str] = mapped_column(String(255), index=True)
    vcn_id: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(255))
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    topology: Mapped[TopologyModel] = relationship(back_populates="internet_gateways")


class NATGatewayModel(Base):
    __tablename__ = "nat_gateways"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topology_id: Mapped[int] = mapped_column(ForeignKey("topologies.id", ondelete="CASCADE"), index=True)
    ocid: Mapped[str] = mapped_column(String(255), index=True)
    vcn_id: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(255))
    public_ip: Mapped[str] = mapped_column(String(50), default="")

    topology: Mapped[TopologyModel] = relationship(back_populates="nat_gateways")


class ServiceGatewayModel(Base):
    __tablename__ = "service_gateways"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topology_id: Mapped[int] = mapped_column(ForeignKey("topologies.id", ondelete="CASCADE"), index=True)
    ocid: Mapped[str] = mapped_column(String(255), index=True)
    vcn_id: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(255))
    services: Mapped[list] = mapped_column(JSON, default=list)

    topology: Mapped[TopologyModel] = relationship(back_populates="service_gateways")


class DRGModel(Base):
    __tablename__ = "drgs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topology_id: Mapped[int] = mapped_column(ForeignKey("topologies.id", ondelete="CASCADE"), index=True)
    ocid: Mapped[str] = mapped_column(String(255), index=True)
    display_name: Mapped[str] = mapped_column(String(255))
    compartment_id: Mapped[str] = mapped_column(String(255), default="")

    topology: Mapped[TopologyModel] = relationship(back_populates="drgs")


class DRGAttachmentModel(Base):
    __tablename__ = "drg_attachments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topology_id: Mapped[int] = mapped_column(ForeignKey("topologies.id", ondelete="CASCADE"), index=True)
    ocid: Mapped[str] = mapped_column(String(255), index=True)
    drg_id: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(255))
    network_type: Mapped[str] = mapped_column(String(50), default="")
    network_id: Mapped[str] = mapped_column(String(255), default="")

    topology: Mapped[TopologyModel] = relationship(back_populates="drg_attachments")


class DRGRouteTableModel(Base):
    __tablename__ = "drg_route_tables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topology_id: Mapped[int] = mapped_column(ForeignKey("topologies.id", ondelete="CASCADE"), index=True)
    ocid: Mapped[str] = mapped_column(String(255), index=True)
    drg_id: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(255))
    is_ecmp_enabled: Mapped[bool] = mapped_column(Boolean, default=False)

    topology: Mapped[TopologyModel] = relationship(back_populates="drg_route_tables")


class DRGRouteRuleModel(Base):
    __tablename__ = "drg_route_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topology_id: Mapped[int] = mapped_column(ForeignKey("topologies.id", ondelete="CASCADE"), index=True)
    drg_route_table_id: Mapped[str] = mapped_column(String(255))
    destination: Mapped[str] = mapped_column(String(255))
    destination_type: Mapped[str] = mapped_column(String(50))
    next_hop_drg_attachment_id: Mapped[str] = mapped_column(String(255))

    topology: Mapped[TopologyModel] = relationship(back_populates="drg_route_rules")


class RemotePeeringConnectionModel(Base):
    __tablename__ = "remote_peering_connections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topology_id: Mapped[int] = mapped_column(ForeignKey("topologies.id", ondelete="CASCADE"), index=True)
    ocid: Mapped[str] = mapped_column(String(255), index=True)
    drg_id: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(255))
    peer_id: Mapped[str] = mapped_column(String(255), default="")
    peer_region: Mapped[str] = mapped_column(String(100), default="")
    peering_status: Mapped[str] = mapped_column(String(50), default="")

    topology: Mapped[TopologyModel] = relationship(back_populates="remote_peering_connections")


class LocalPeeringGatewayModel(Base):
    __tablename__ = "local_peering_gateways"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topology_id: Mapped[int] = mapped_column(ForeignKey("topologies.id", ondelete="CASCADE"), index=True)
    ocid: Mapped[str] = mapped_column(String(255), index=True)
    vcn_id: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(255))
    peer_id: Mapped[str] = mapped_column(String(255), default="")
    peering_status: Mapped[str] = mapped_column(String(50), default="")

    topology: Mapped[TopologyModel] = relationship(back_populates="local_peering_gateways")


class RouteTableModel(Base):
    __tablename__ = "route_tables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topology_id: Mapped[int] = mapped_column(ForeignKey("topologies.id", ondelete="CASCADE"), index=True)
    ocid: Mapped[str] = mapped_column(String(255), index=True)
    vcn_id: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(255))

    topology: Mapped[TopologyModel] = relationship(back_populates="route_tables")


class RouteRuleModel(Base):
    __tablename__ = "route_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topology_id: Mapped[int] = mapped_column(ForeignKey("topologies.id", ondelete="CASCADE"), index=True)
    route_table_id: Mapped[str] = mapped_column(String(255))
    destination: Mapped[str] = mapped_column(String(255))
    destination_type: Mapped[str] = mapped_column(String(50))
    network_entity_id: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")

    topology: Mapped[TopologyModel] = relationship(back_populates="route_rules")


class SecurityListModel(Base):
    __tablename__ = "security_lists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topology_id: Mapped[int] = mapped_column(ForeignKey("topologies.id", ondelete="CASCADE"), index=True)
    ocid: Mapped[str] = mapped_column(String(255), index=True)
    vcn_id: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(255))

    topology: Mapped[TopologyModel] = relationship(back_populates="security_lists")


class SecurityRuleModel(Base):
    __tablename__ = "security_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topology_id: Mapped[int] = mapped_column(ForeignKey("topologies.id", ondelete="CASCADE"), index=True)
    security_list_id: Mapped[str] = mapped_column(String(255))
    direction: Mapped[str] = mapped_column(String(20))
    protocol: Mapped[str] = mapped_column(String(10))
    source: Mapped[str] = mapped_column(String(255), default="")
    destination: Mapped[str] = mapped_column(String(255), default="")
    source_port_range_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_port_range_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    destination_port_range_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    destination_port_range_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str] = mapped_column(Text, default="")

    topology: Mapped[TopologyModel] = relationship(back_populates="security_rules")


class NetworkSecurityGroupModel(Base):
    __tablename__ = "network_security_groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topology_id: Mapped[int] = mapped_column(ForeignKey("topologies.id", ondelete="CASCADE"), index=True)
    ocid: Mapped[str] = mapped_column(String(255), index=True)
    vcn_id: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(255))

    topology: Mapped[TopologyModel] = relationship(back_populates="network_security_groups")


class NSGRuleModel(Base):
    __tablename__ = "nsg_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topology_id: Mapped[int] = mapped_column(ForeignKey("topologies.id", ondelete="CASCADE"), index=True)
    nsg_id: Mapped[str] = mapped_column(String(255))
    direction: Mapped[str] = mapped_column(String(20))
    protocol: Mapped[str] = mapped_column(String(10))
    source: Mapped[str] = mapped_column(String(255), default="")
    destination: Mapped[str] = mapped_column(String(255), default="")
    source_type: Mapped[str] = mapped_column(String(50), default="")
    destination_type: Mapped[str] = mapped_column(String(50), default="")
    source_port_range_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_port_range_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    destination_port_range_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    destination_port_range_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str] = mapped_column(Text, default="")

    topology: Mapped[TopologyModel] = relationship(back_populates="nsg_rules")


class LoadBalancerModel(Base):
    __tablename__ = "load_balancers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topology_id: Mapped[int] = mapped_column(ForeignKey("topologies.id", ondelete="CASCADE"), index=True)
    ocid: Mapped[str] = mapped_column(String(255), index=True)
    display_name: Mapped[str] = mapped_column(String(255))
    ip_addresses: Mapped[list] = mapped_column(JSON, default=list)
    shape: Mapped[str] = mapped_column(String(100), default="")
    subnet_ids: Mapped[list] = mapped_column(JSON, default=list)
    is_private: Mapped[bool] = mapped_column(Boolean, default=False)

    topology: Mapped[TopologyModel] = relationship(back_populates="load_balancers")


class NetworkLoadBalancerModel(Base):
    __tablename__ = "network_load_balancers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topology_id: Mapped[int] = mapped_column(ForeignKey("topologies.id", ondelete="CASCADE"), index=True)
    ocid: Mapped[str] = mapped_column(String(255), index=True)
    display_name: Mapped[str] = mapped_column(String(255))
    ip_addresses: Mapped[list] = mapped_column(JSON, default=list)
    subnet_ids: Mapped[list] = mapped_column(JSON, default=list)
    is_private: Mapped[bool] = mapped_column(Boolean, default=False)
    is_preserve_source: Mapped[bool] = mapped_column(Boolean, default=False)

    topology: Mapped[TopologyModel] = relationship(back_populates="network_load_balancers")


class IPSecConnectionModel(Base):
    __tablename__ = "ipsec_connections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topology_id: Mapped[int] = mapped_column(ForeignKey("topologies.id", ondelete="CASCADE"), index=True)
    ocid: Mapped[str] = mapped_column(String(255), index=True)
    drg_id: Mapped[str] = mapped_column(String(255))
    cpe_id: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(255))
    static_routes: Mapped[list] = mapped_column(JSON, default=list)
    cpe_local_identifier: Mapped[str] = mapped_column(String(255), default="")

    topology: Mapped[TopologyModel] = relationship(back_populates="ipsec_connections")


class CPEModel(Base):
    __tablename__ = "cpes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topology_id: Mapped[int] = mapped_column(ForeignKey("topologies.id", ondelete="CASCADE"), index=True)
    ocid: Mapped[str] = mapped_column(String(255), index=True)
    display_name: Mapped[str] = mapped_column(String(255))
    ip_address: Mapped[str] = mapped_column(String(50), default="")
    cpe_device_shape_id: Mapped[str] = mapped_column(String(255), default="")

    topology: Mapped[TopologyModel] = relationship(back_populates="cpes")


class IPSecTunnelModel(Base):
    __tablename__ = "ipsec_tunnels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topology_id: Mapped[int] = mapped_column(ForeignKey("topologies.id", ondelete="CASCADE"), index=True)
    ocid: Mapped[str] = mapped_column(String(255), index=True)
    ipsec_connection_id: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default="")
    vpn_ip: Mapped[str] = mapped_column(String(50), default="")
    cpe_ip: Mapped[str] = mapped_column(String(50), default="")
    routing: Mapped[str] = mapped_column(String(50), default="")
    bgp_info: Mapped[dict] = mapped_column(JSON, default=dict)

    topology: Mapped[TopologyModel] = relationship(back_populates="ipsec_tunnels")


# --- New models for Job 1 ---


class NetworkFirewallModel(Base):
    __tablename__ = "network_firewalls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topology_id: Mapped[int] = mapped_column(ForeignKey("topologies.id", ondelete="CASCADE"), index=True)
    ocid: Mapped[str] = mapped_column(String(255), index=True)
    display_name: Mapped[str] = mapped_column(String(255), default="")
    subnet_id: Mapped[str] = mapped_column(String(255), default="")
    vcn_id: Mapped[str] = mapped_column(String(255), default="")
    policy_id: Mapped[str] = mapped_column(String(255), default="")
    ip_addresses: Mapped[list] = mapped_column(JSON, default=list)
    lifecycle_state: Mapped[str] = mapped_column(String(50), default="")

    topology: Mapped[TopologyModel] = relationship(back_populates="network_firewalls")


class DHCPOptionsModel(Base):
    __tablename__ = "dhcp_options"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topology_id: Mapped[int] = mapped_column(ForeignKey("topologies.id", ondelete="CASCADE"), index=True)
    ocid: Mapped[str] = mapped_column(String(255), index=True)
    vcn_id: Mapped[str] = mapped_column(String(255), default="")
    display_name: Mapped[str] = mapped_column(String(255), default="")
    options: Mapped[list] = mapped_column(JSON, default=list)

    topology: Mapped[TopologyModel] = relationship(back_populates="dhcp_options")


class PublicIPModel(Base):
    __tablename__ = "public_ips"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topology_id: Mapped[int] = mapped_column(ForeignKey("topologies.id", ondelete="CASCADE"), index=True)
    ocid: Mapped[str] = mapped_column(String(255), index=True)
    display_name: Mapped[str] = mapped_column(String(255), default="")
    ip_address: Mapped[str] = mapped_column(String(50), default="")
    lifetime: Mapped[str] = mapped_column(String(50), default="")
    assigned_entity_id: Mapped[str] = mapped_column(String(255), default="")
    assigned_entity_type: Mapped[str] = mapped_column(String(100), default="")
    compartment_id: Mapped[str] = mapped_column(String(255), default="")

    topology: Mapped[TopologyModel] = relationship(back_populates="public_ips")


class CrossConnectModel(Base):
    __tablename__ = "cross_connects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topology_id: Mapped[int] = mapped_column(ForeignKey("topologies.id", ondelete="CASCADE"), index=True)
    ocid: Mapped[str] = mapped_column(String(255), index=True)
    display_name: Mapped[str] = mapped_column(String(255), default="")
    compartment_id: Mapped[str] = mapped_column(String(255), default="")
    location_name: Mapped[str] = mapped_column(String(255), default="")
    port_speed_shape_name: Mapped[str] = mapped_column(String(100), default="")
    cross_connect_group_id: Mapped[str] = mapped_column(String(255), default="")
    lifecycle_state: Mapped[str] = mapped_column(String(50), default="")

    topology: Mapped[TopologyModel] = relationship(back_populates="cross_connects")


class VirtualCircuitModel(Base):
    __tablename__ = "virtual_circuits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topology_id: Mapped[int] = mapped_column(ForeignKey("topologies.id", ondelete="CASCADE"), index=True)
    ocid: Mapped[str] = mapped_column(String(255), index=True)
    display_name: Mapped[str] = mapped_column(String(255), default="")
    compartment_id: Mapped[str] = mapped_column(String(255), default="")
    type: Mapped[str] = mapped_column(String(50), default="")
    bandwidth_shape_name: Mapped[str] = mapped_column(String(100), default="")
    bgp_session_state: Mapped[str] = mapped_column(String(50), default="")
    gateway_id: Mapped[str] = mapped_column(String(255), default="")
    provider_name: Mapped[str] = mapped_column(String(255), default="")
    region: Mapped[str] = mapped_column(String(100), default="")
    lifecycle_state: Mapped[str] = mapped_column(String(50), default="")

    topology: Mapped[TopologyModel] = relationship(back_populates="virtual_circuits")


class DRGRouteDistributionModel(Base):
    __tablename__ = "drg_route_distributions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topology_id: Mapped[int] = mapped_column(ForeignKey("topologies.id", ondelete="CASCADE"), index=True)
    ocid: Mapped[str] = mapped_column(String(255), index=True)
    drg_id: Mapped[str] = mapped_column(String(255), default="")
    display_name: Mapped[str] = mapped_column(String(255), default="")
    distribution_type: Mapped[str] = mapped_column(String(50), default="")

    topology: Mapped[TopologyModel] = relationship(back_populates="drg_route_distributions")
