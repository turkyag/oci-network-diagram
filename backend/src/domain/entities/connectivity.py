from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DRG:
    id: int | None
    topology_id: int
    ocid: str
    display_name: str
    compartment_id: str = ""


@dataclass
class DRGAttachment:
    id: int | None
    topology_id: int
    ocid: str
    drg_id: str
    display_name: str
    network_type: str = ""
    network_id: str = ""


@dataclass
class RemotePeeringConnection:
    id: int | None
    topology_id: int
    ocid: str
    drg_id: str
    display_name: str
    peer_id: str = ""
    peer_region: str = ""
    peering_status: str = ""


@dataclass
class LocalPeeringGateway:
    id: int | None
    topology_id: int
    ocid: str
    vcn_id: str
    display_name: str
    peer_id: str = ""
    peering_status: str = ""


@dataclass
class IPSecConnection:
    id: int | None
    topology_id: int
    ocid: str
    drg_id: str
    cpe_id: str
    display_name: str
    static_routes: list[str] = field(default_factory=list)
    cpe_local_identifier: str = ""


@dataclass
class CPE:
    id: int | None
    topology_id: int
    ocid: str
    display_name: str
    ip_address: str = ""
    cpe_device_shape_id: str = ""


@dataclass
class IPSecTunnel:
    id: int | None
    topology_id: int
    ocid: str
    ipsec_connection_id: str
    display_name: str
    status: str = ""
    vpn_ip: str = ""
    cpe_ip: str = ""
    routing: str = ""
    bgp_info: dict = field(default_factory=dict)


@dataclass
class CrossConnect:
    id: int | None = None
    topology_id: int | None = None
    ocid: str = ""
    display_name: str = ""
    compartment_id: str = ""
    location_name: str = ""
    port_speed_shape_name: str = ""
    cross_connect_group_id: str = ""
    lifecycle_state: str = ""


@dataclass
class VirtualCircuit:
    id: int | None = None
    topology_id: int | None = None
    ocid: str = ""
    display_name: str = ""
    compartment_id: str = ""
    type: str = ""
    bandwidth_shape_name: str = ""
    bgp_session_state: str = ""
    gateway_id: str = ""
    provider_name: str = ""
    region: str = ""
    lifecycle_state: str = ""


@dataclass
class DRGRouteDistribution:
    id: int | None = None
    topology_id: int | None = None
    ocid: str = ""
    drg_id: str = ""
    display_name: str = ""
    distribution_type: str = ""
