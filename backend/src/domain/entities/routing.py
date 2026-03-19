from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RouteTable:
    id: int | None
    topology_id: int
    ocid: str
    vcn_id: str
    display_name: str


@dataclass
class RouteRule:
    id: int | None
    topology_id: int
    route_table_id: str
    destination: str
    destination_type: str
    network_entity_id: str
    description: str = ""


@dataclass
class DRGRouteTable:
    id: int | None
    topology_id: int
    ocid: str
    drg_id: str
    display_name: str
    is_ecmp_enabled: bool = False


@dataclass
class DRGRouteRule:
    id: int | None
    topology_id: int
    drg_route_table_id: str
    destination: str
    destination_type: str
    next_hop_drg_attachment_id: str
