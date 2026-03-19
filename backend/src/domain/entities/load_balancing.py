from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class LoadBalancer:
    id: int | None
    topology_id: int
    ocid: str
    display_name: str
    ip_addresses: list[dict] = field(default_factory=list)
    shape: str = ""
    subnet_ids: list[str] = field(default_factory=list)
    is_private: bool = False


@dataclass
class NetworkLoadBalancer:
    id: int | None
    topology_id: int
    ocid: str
    display_name: str
    ip_addresses: list[dict] = field(default_factory=list)
    subnet_ids: list[str] = field(default_factory=list)
    is_private: bool = False
    is_preserve_source: bool = False
