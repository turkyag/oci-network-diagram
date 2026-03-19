from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.entities.topology import Topology


class TopologyRepository(ABC):
    """Abstract repository for topology aggregate."""

    @abstractmethod
    async def get_by_id(self, topology_id: int) -> Topology | None:
        """Fetch a topology with all related resources."""

    @abstractmethod
    async def list_all(self) -> list[Topology]:
        """List all topologies (summary only, no nested resources)."""

    @abstractmethod
    async def save(self, topology: Topology) -> Topology:
        """Create or update a topology."""

    @abstractmethod
    async def delete(self, topology_id: int) -> bool:
        """Delete a topology and all related resources. Returns True if found."""

    @abstractmethod
    async def import_topology_data(self, topology_id: int, data: dict) -> Topology:
        """Import all OCI resources into a topology."""
