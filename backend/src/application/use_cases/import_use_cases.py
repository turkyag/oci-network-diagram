from __future__ import annotations

from src.application.dto import ImportRequest, TopologyDetailResponse
from src.application.use_cases.topology_use_cases import GetTopologyUseCase
from src.domain.repositories import TopologyRepository


class ImportOCIDataUseCase:
    def __init__(self, repository: TopologyRepository) -> None:
        self._repository = repository

    async def execute(
        self, topology_id: int, request: ImportRequest
    ) -> TopologyDetailResponse | None:
        topology = await self._repository.get_by_id(topology_id)
        if not topology:
            return None

        data = request.model_dump()
        await self._repository.import_topology_data(topology_id, data)

        get_use_case = GetTopologyUseCase(self._repository)
        return await get_use_case.execute(topology_id)
