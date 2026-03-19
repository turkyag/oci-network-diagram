from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SecurityList:
    id: int | None
    topology_id: int
    ocid: str
    vcn_id: str
    display_name: str


@dataclass
class SecurityRule:
    id: int | None
    topology_id: int
    security_list_id: str
    direction: str
    protocol: str
    source: str = ""
    destination: str = ""
    source_port_range_min: int | None = None
    source_port_range_max: int | None = None
    destination_port_range_min: int | None = None
    destination_port_range_max: int | None = None
    description: str = ""


@dataclass
class NetworkSecurityGroup:
    id: int | None
    topology_id: int
    ocid: str
    vcn_id: str
    display_name: str


@dataclass
class NSGRule:
    id: int | None
    topology_id: int
    nsg_id: str
    direction: str
    protocol: str
    source: str = ""
    destination: str = ""
    source_type: str = ""
    destination_type: str = ""
    source_port_range_min: int | None = None
    source_port_range_max: int | None = None
    destination_port_range_min: int | None = None
    destination_port_range_max: int | None = None
    description: str = ""


@dataclass
class NetworkFirewall:
    id: int | None = None
    topology_id: int | None = None
    ocid: str = ""
    display_name: str = ""
    subnet_id: str = ""
    vcn_id: str = ""
    policy_id: str = ""
    ip_addresses: list = field(default_factory=list)
    lifecycle_state: str = ""
