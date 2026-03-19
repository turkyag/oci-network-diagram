from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class OCID(str):
    """OCI Resource Identifier wrapper."""

    def __new__(cls, value: str) -> OCID:
        if not value:
            raise ValueError("OCID cannot be empty")
        return super().__new__(cls, value)


@dataclass(frozen=True)
class CidrBlock:
    """Validated CIDR block."""

    value: str

    def __post_init__(self) -> None:
        pattern = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}$"
        if not re.match(pattern, self.value):
            raise ValueError(f"Invalid CIDR block: {self.value}")


@dataclass(frozen=True)
class PortRange:
    """Port range with min and max."""

    min_port: int
    max_port: int

    def __post_init__(self) -> None:
        if not (0 <= self.min_port <= 65535):
            raise ValueError(f"Invalid min_port: {self.min_port}")
        if not (0 <= self.max_port <= 65535):
            raise ValueError(f"Invalid max_port: {self.max_port}")
        if self.min_port > self.max_port:
            raise ValueError("min_port cannot exceed max_port")


@dataclass(frozen=True)
class IPAddress:
    """IP address wrapper."""

    value: str

    def __post_init__(self) -> None:
        pattern = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"
        if not re.match(pattern, self.value):
            raise ValueError(f"Invalid IP address: {self.value}")


class PeeringStatus(str, Enum):
    INVALID = "INVALID"
    NEW = "NEW"
    PENDING = "PENDING"
    PEERED = "PEERED"
    REVOKED = "REVOKED"


class ResourceType(str, Enum):
    VCN = "VCN"
    SUBNET = "SUBNET"
    INTERNET_GATEWAY = "INTERNET_GATEWAY"
    NAT_GATEWAY = "NAT_GATEWAY"
    SERVICE_GATEWAY = "SERVICE_GATEWAY"
    DRG = "DRG"
    DRG_ATTACHMENT = "DRG_ATTACHMENT"
    DRG_ROUTE_TABLE = "DRG_ROUTE_TABLE"
    DRG_ROUTE_RULE = "DRG_ROUTE_RULE"
    REMOTE_PEERING_CONNECTION = "REMOTE_PEERING_CONNECTION"
    LOCAL_PEERING_GATEWAY = "LOCAL_PEERING_GATEWAY"
    ROUTE_TABLE = "ROUTE_TABLE"
    ROUTE_RULE = "ROUTE_RULE"
    SECURITY_LIST = "SECURITY_LIST"
    SECURITY_RULE = "SECURITY_RULE"
    NETWORK_SECURITY_GROUP = "NETWORK_SECURITY_GROUP"
    NSG_RULE = "NSG_RULE"
    LOAD_BALANCER = "LOAD_BALANCER"
    NETWORK_LOAD_BALANCER = "NETWORK_LOAD_BALANCER"
    IPSEC_CONNECTION = "IPSEC_CONNECTION"
    CPE = "CPE"
    IPSEC_TUNNEL = "IPSEC_TUNNEL"


class LifecycleState(str, Enum):
    PROVISIONING = "PROVISIONING"
    AVAILABLE = "AVAILABLE"
    TERMINATING = "TERMINATING"
    TERMINATED = "TERMINATED"
    UPDATING = "UPDATING"
    FAULTY = "FAULTY"
