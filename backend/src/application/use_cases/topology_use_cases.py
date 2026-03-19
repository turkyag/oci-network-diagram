from __future__ import annotations

from dataclasses import asdict

from src.application.dto import (
    AnalysisResponse,
    DiagramResponse,
    TopologyCreateRequest,
    TopologyDetailResponse,
    TopologySummaryResponse,
)
from src.domain.entities.topology import Topology
from src.domain.repositories import TopologyRepository
from src.domain.services.diagram_service import DiagramService
from src.domain.services.route_analyzer import RouteAnalyzer


class CreateTopologyUseCase:
    def __init__(self, repository: TopologyRepository) -> None:
        self._repository = repository

    async def execute(self, request: TopologyCreateRequest) -> TopologySummaryResponse:
        topology = Topology.create(name=request.name, description=request.description)
        saved = await self._repository.save(topology)
        return TopologySummaryResponse(
            id=saved.id,
            name=saved.name,
            description=saved.description,
            vcn_count=0,
            drg_count=0,
            created_at=saved.created_at,
        )


class ListTopologiesUseCase:
    def __init__(self, repository: TopologyRepository) -> None:
        self._repository = repository

    async def execute(self) -> list[TopologySummaryResponse]:
        topologies = await self._repository.list_all()
        return [
            TopologySummaryResponse(
                id=t.id,
                name=t.name,
                description=t.description,
                vcn_count=len(t.vcns),
                drg_count=len(t.drgs),
                created_at=t.created_at,
            )
            for t in topologies
        ]


class GetTopologyUseCase:
    def __init__(self, repository: TopologyRepository) -> None:
        self._repository = repository

    async def execute(self, topology_id: int) -> TopologyDetailResponse | None:
        topology = await self._repository.get_by_id(topology_id)
        if not topology:
            return None

        def _serialize(items: list) -> list[dict]:
            return [asdict(item) for item in items]

        return TopologyDetailResponse(
            id=topology.id,
            name=topology.name,
            description=topology.description,
            created_at=topology.created_at,
            updated_at=topology.updated_at,
            vcns=_serialize(topology.vcns),
            subnets=_serialize(topology.subnets),
            internet_gateways=_serialize(topology.internet_gateways),
            nat_gateways=_serialize(topology.nat_gateways),
            service_gateways=_serialize(topology.service_gateways),
            drgs=_serialize(topology.drgs),
            drg_attachments=_serialize(topology.drg_attachments),
            drg_route_tables=_serialize(topology.drg_route_tables),
            drg_route_rules=_serialize(topology.drg_route_rules),
            remote_peering_connections=_serialize(topology.remote_peering_connections),
            local_peering_gateways=_serialize(topology.local_peering_gateways),
            route_tables=_serialize(topology.route_tables),
            route_rules=_serialize(topology.route_rules),
            security_lists=_serialize(topology.security_lists),
            security_rules=_serialize(topology.security_rules),
            network_security_groups=_serialize(topology.network_security_groups),
            nsg_rules=_serialize(topology.nsg_rules),
            load_balancers=_serialize(topology.load_balancers),
            network_load_balancers=_serialize(topology.network_load_balancers),
            ipsec_connections=_serialize(topology.ipsec_connections),
            cpes=_serialize(topology.cpes),
            ipsec_tunnels=_serialize(topology.ipsec_tunnels),
            network_firewalls=_serialize(topology.network_firewalls),
            dhcp_options=_serialize(topology.dhcp_options),
            public_ips=_serialize(topology.public_ips),
            cross_connects=_serialize(topology.cross_connects),
            virtual_circuits=_serialize(topology.virtual_circuits),
            drg_route_distributions=_serialize(topology.drg_route_distributions),
        )


class DeleteTopologyUseCase:
    def __init__(self, repository: TopologyRepository) -> None:
        self._repository = repository

    async def execute(self, topology_id: int) -> bool:
        return await self._repository.delete(topology_id)


class GetDiagramUseCase:
    def __init__(self, repository: TopologyRepository) -> None:
        self._repository = repository
        self._diagram_service = DiagramService()

    async def execute(self, topology_id: int) -> DiagramResponse | None:
        topology = await self._repository.get_by_id(topology_id)
        if not topology:
            return None
        result = self._diagram_service.generate(topology)
        return DiagramResponse(nodes=result["nodes"], edges=result["edges"])


class GetAnalysisUseCase:
    def __init__(self, repository: TopologyRepository) -> None:
        self._repository = repository
        self._analyzer = RouteAnalyzer()

    async def execute(self, topology_id: int) -> AnalysisResponse | None:
        topology = await self._repository.get_by_id(topology_id)
        if not topology:
            return None
        result = self._analyzer.analyze(topology)
        return AnalysisResponse(
            flows=[asdict(f) for f in result.flows],
            drg_flows=[asdict(f) for f in result.drg_flows],
            warnings=[asdict(w) for w in result.warnings],
            subnet_to_route_table=result.subnet_to_route_table,
            route_table_to_subnets=result.route_table_to_subnets,
            gateway_to_route_rules=result.gateway_to_route_rules,
        )
