from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class VCN:
    id: int | None
    topology_id: int
    ocid: str
    display_name: str
    cidr_blocks: list[str] = field(default_factory=list)
    dns_label: str = ""
    compartment_id: str = ""


@dataclass
class Subnet:
    id: int | None
    topology_id: int
    ocid: str
    vcn_id: str
    display_name: str
    cidr_block: str
    subnet_domain_name: str = ""
    route_table_id: str = ""
    security_list_ids: list[str] = field(default_factory=list)
    prohibit_public_ip_on_vnic: bool = True


@dataclass
class InternetGateway:
    id: int | None
    topology_id: int
    ocid: str
    vcn_id: str
    display_name: str
    is_enabled: bool = True


@dataclass
class NATGateway:
    id: int | None
    topology_id: int
    ocid: str
    vcn_id: str
    display_name: str
    public_ip: str = ""


@dataclass
class ServiceGateway:
    id: int | None
    topology_id: int
    ocid: str
    vcn_id: str
    display_name: str
    services: list[dict] = field(default_factory=list)


@dataclass
class DHCPOptions:
    id: int | None = None
    topology_id: int | None = None
    ocid: str = ""
    vcn_id: str = ""
    display_name: str = ""
    options: list = field(default_factory=list)


@dataclass
class PublicIP:
    id: int | None = None
    topology_id: int | None = None
    ocid: str = ""
    display_name: str = ""
    ip_address: str = ""
    lifetime: str = ""
    assigned_entity_id: str = ""
    assigned_entity_type: str = ""
    compartment_id: str = ""
