from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import (
    get_create_stage_handler,
    get_list_stages_handler,
)
from app.application.commands import CreateStageCommand
from app.application.exceptions import FestivalNotFound
from app.application.use_cases.manage_stages import (
    CreateStageHandler,
    ListStagesHandler,
)
from app.domain.entities import Stage
from app.domain.value_objects import EquipmentSet
from app.schemas import StageCreate, StageRead

router = APIRouter(prefix="/stages", tags=["stages"])


def _stage_response(stage: Stage) -> dict[str, object]:
    return {
        "id": stage.id,
        "festival_id": stage.festival_id,
        "name": stage.name,
        "capacity": stage.capacity,
        "available_equipment": sorted(stage.available_equipment.items),
    }


@router.get("", response_model=list[StageRead])
def list_stages(
    festival_id: int,
    handler: ListStagesHandler = Depends(get_list_stages_handler),
):
    return [
        _stage_response(stage)
        for stage in handler.execute(festival_id)
    ]


@router.post("", response_model=StageRead, status_code=201)
def create_stage(
    payload: StageCreate,
    handler: CreateStageHandler = Depends(get_create_stage_handler),
):
    try:
        stage = handler.execute(
            CreateStageCommand(
                festival_id=payload.festival_id,
                name=payload.name,
                capacity=payload.capacity,
                available_equipment=EquipmentSet(
                    frozenset(payload.available_equipment)
                ),
            )
        )
    except FestivalNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _stage_response(stage)
