from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TopologyCreateRequest(BaseModel):
    name: str
    description: str = ""


class TopologySummaryResponse(BaseModel):
    id: int
    name: str
    description: str
    vcn_count: int = 0
    drg_count: int = 0
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class VCNResponse(BaseModel):
    id: int | None = None
    ocid: str
    display_name: str
    cidr_blocks: list[str] = []
    dns_label: str = ""
    compartment_id: str = ""

    model_config = {"from_attributes": True}


class SubnetResponse(BaseModel):
    id: int | None = None
    ocid: str
    vcn_id: str
    display_name: str
    cidr_block: str
    subnet_domain_name: str = ""
    route_table_id: str = ""
    security_list_ids: list[str] = []

    model_config = {"from_attributes": True}


class ResourceResponse(BaseModel):
    """Generic response for simple OCI resources."""

    model_config = {"from_attributes": True}


class TopologyDetailResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    vcns: list[dict[str, Any]] = []
    subnets: list[dict[str, Any]] = []
    internet_gateways: list[dict[str, Any]] = []
    nat_gateways: list[dict[str, Any]] = []
    service_gateways: list[dict[str, Any]] = []
    drgs: list[dict[str, Any]] = []
    drg_attachments: list[dict[str, Any]] = []
    drg_route_tables: list[dict[str, Any]] = []
    drg_route_rules: list[dict[str, Any]] = []
    remote_peering_connections: list[dict[str, Any]] = []
    local_peering_gateways: list[dict[str, Any]] = []
    route_tables: list[dict[str, Any]] = []
    route_rules: list[dict[str, Any]] = []
    security_lists: list[dict[str, Any]] = []
    security_rules: list[dict[str, Any]] = []
    network_security_groups: list[dict[str, Any]] = []
    nsg_rules: list[dict[str, Any]] = []
    load_balancers: list[dict[str, Any]] = []
    network_load_balancers: list[dict[str, Any]] = []
    ipsec_connections: list[dict[str, Any]] = []
    cpes: list[dict[str, Any]] = []
    ipsec_tunnels: list[dict[str, Any]] = []
    network_firewalls: list[dict[str, Any]] = []
    dhcp_options: list[dict[str, Any]] = []
    public_ips: list[dict[str, Any]] = []
    cross_connects: list[dict[str, Any]] = []
    virtual_circuits: list[dict[str, Any]] = []
    drg_route_distributions: list[dict[str, Any]] = []

    model_config = {"from_attributes": True}


class DiagramResponse(BaseModel):
    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]
    warnings: list[dict[str, Any]] = []


class AnalysisResponse(BaseModel):
    flows: list[dict[str, Any]]
    drg_flows: list[dict[str, Any]]
    warnings: list[dict[str, Any]]
    subnet_to_route_table: dict[str, str]
    route_table_to_subnets: dict[str, list[str]]
    gateway_to_route_rules: dict[str, list[str]]


class ImportRequest(BaseModel):
    vcns: list[dict[str, Any]] = Field(default_factory=list)
    subnets: list[dict[str, Any]] = Field(default_factory=list)
    internet_gateways: list[dict[str, Any]] = Field(default_factory=list)
    nat_gateways: list[dict[str, Any]] = Field(default_factory=list)
    service_gateways: list[dict[str, Any]] = Field(default_factory=list)
    drgs: list[dict[str, Any]] = Field(default_factory=list)
    drg_attachments: list[dict[str, Any]] = Field(default_factory=list)
    drg_route_tables: list[dict[str, Any]] = Field(default_factory=list)
    drg_route_rules: list[dict[str, Any]] = Field(default_factory=list)
    remote_peering_connections: list[dict[str, Any]] = Field(default_factory=list)
    local_peering_gateways: list[dict[str, Any]] = Field(default_factory=list)
    route_tables: list[dict[str, Any]] = Field(default_factory=list)
    route_rules: list[dict[str, Any]] = Field(default_factory=list)
    security_lists: list[dict[str, Any]] = Field(default_factory=list)
    security_rules: list[dict[str, Any]] = Field(default_factory=list)
    network_security_groups: list[dict[str, Any]] = Field(default_factory=list)
    nsg_rules: list[dict[str, Any]] = Field(default_factory=list)
    load_balancers: list[dict[str, Any]] = Field(default_factory=list)
    network_load_balancers: list[dict[str, Any]] = Field(default_factory=list)
    ipsec_connections: list[dict[str, Any]] = Field(default_factory=list)
    cpes: list[dict[str, Any]] = Field(default_factory=list)
    ipsec_tunnels: list[dict[str, Any]] = Field(default_factory=list)
    network_firewalls: list[dict[str, Any]] = Field(default_factory=list)
    dhcp_options: list[dict[str, Any]] = Field(default_factory=list)
    public_ips: list[dict[str, Any]] = Field(default_factory=list)
    cross_connects: list[dict[str, Any]] = Field(default_factory=list)
    virtual_circuits: list[dict[str, Any]] = Field(default_factory=list)
    drg_route_distributions: list[dict[str, Any]] = Field(default_factory=list)
