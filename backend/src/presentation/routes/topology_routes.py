from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dto import (
    AnalysisResponse,
    DiagramResponse,
    ImportRequest,
    TopologyCreateRequest,
    TopologyDetailResponse,
    TopologySummaryResponse,
)
from src.application.use_cases.import_use_cases import ImportOCIDataUseCase
from src.application.use_cases.topology_use_cases import (
    CreateTopologyUseCase,
    DeleteTopologyUseCase,
    GetAnalysisUseCase,
    GetDiagramUseCase,
    GetTopologyUseCase,
    ListTopologiesUseCase,
)
from src.infrastructure.database.connection import get_session
from src.infrastructure.repositories.sql_topology_repository import SqlTopologyRepository

router = APIRouter(prefix="/api/topologies", tags=["topologies"])


def _repo(session: AsyncSession) -> SqlTopologyRepository:
    return SqlTopologyRepository(session)


@router.get("", response_model=list[TopologySummaryResponse])
async def list_topologies(
    session: AsyncSession = Depends(get_session),
) -> list[TopologySummaryResponse]:
    use_case = ListTopologiesUseCase(_repo(session))
    return await use_case.execute()


@router.post("", response_model=TopologySummaryResponse, status_code=201)
async def create_topology(
    request: TopologyCreateRequest,
    session: AsyncSession = Depends(get_session),
) -> TopologySummaryResponse:
    use_case = CreateTopologyUseCase(_repo(session))
    return await use_case.execute(request)


@router.get("/{topology_id}", response_model=TopologyDetailResponse)
async def get_topology(
    topology_id: int,
    session: AsyncSession = Depends(get_session),
) -> TopologyDetailResponse:
    use_case = GetTopologyUseCase(_repo(session))
    result = await use_case.execute(topology_id)
    if not result:
        raise HTTPException(status_code=404, detail="Topology not found")
    return result


@router.delete("/{topology_id}", status_code=204, response_class=Response)
async def delete_topology(
    topology_id: int,
    session: AsyncSession = Depends(get_session),
) -> Response:
    use_case = DeleteTopologyUseCase(_repo(session))
    deleted = await use_case.execute(topology_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Topology not found")
    return Response(status_code=204)


@router.post("/{topology_id}/import", response_model=TopologyDetailResponse)
async def import_topology_data(
    topology_id: int,
    request: ImportRequest,
    session: AsyncSession = Depends(get_session),
) -> TopologyDetailResponse:
    use_case = ImportOCIDataUseCase(_repo(session))
    result = await use_case.execute(topology_id, request)
    if not result:
        raise HTTPException(status_code=404, detail="Topology not found")
    return result


@router.get("/{topology_id}/diagram", response_model=DiagramResponse)
async def get_diagram(
    topology_id: int,
    session: AsyncSession = Depends(get_session),
) -> DiagramResponse:
    use_case = GetDiagramUseCase(_repo(session))
    result = await use_case.execute(topology_id)
    if not result:
        raise HTTPException(status_code=404, detail="Topology not found")
    return result


@router.get("/{topology_id}/analysis", response_model=AnalysisResponse)
async def get_analysis(
    topology_id: int,
    session: AsyncSession = Depends(get_session),
) -> AnalysisResponse:
    use_case = GetAnalysisUseCase(_repo(session))
    result = await use_case.execute(topology_id)
    if not result:
        raise HTTPException(status_code=404, detail="Topology not found")
    return result
