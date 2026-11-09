from fastapi import APIRouter, Depends, HTTPException
from app.domain.entities import Festival
from app.schemas import FestivalCreate, FestivalRead
from app.api.dependencies import (
    get_create_festival_handler,
    get_list_festivals_handler,
    get_reschedule_concert_handler,
    get_schedule_concert_handler,
    get_cancel_concert_handler,
    get_publish_festival_handler,
)
from app.api.reschedule import reschedule_concert_response
from app.application.use_cases.reschedule_concert import RescheduleConcertHandler
from app.schemas import ConcertRead, ConcertReschedule
from app.api.schedule import schedule_concert_response
from app.application.use_cases.schedule_concert import ScheduleConcertHandler
from app.schemas import FestivalConcertCreate
from app.api.cancel import cancel_concert_response
from app.application.use_cases.cancel_concert import CancelConcertHandler
from app.api.publish import publish_festival_response
from app.application.use_cases.publish_festival import PublishFestivalHandler
from app.application.commands import CreateFestivalCommand
from app.application.exceptions import FestivalCreationRejected
from app.application.use_cases.manage_festivals import (
    CreateFestivalHandler,
    ListFestivalsHandler,
)

router = APIRouter(prefix="/festivals", tags=["festivals"])


def _festival_response(festival: Festival) -> dict[str, object]:
    return {
        "id": festival.id,
        "name": festival.name,
        "location": festival.location,
        "start_date": festival.period.start,
        "end_date": festival.period.end,
        "status": festival.status.value,
    }


@router.get("", response_model=list[FestivalRead])
def list_festivals(
    handler: ListFestivalsHandler = Depends(get_list_festivals_handler),
):
    return [_festival_response(festival) for festival in handler.execute()]


@router.post("", response_model=FestivalRead, status_code=201)
def create_festival(
    payload: FestivalCreate,
    handler: CreateFestivalHandler = Depends(get_create_festival_handler),
):
    try:
        festival = handler.execute(
            CreateFestivalCommand(
                name=payload.name,
                location=payload.location,
                start_date=payload.start_date,
                end_date=payload.end_date,
            )
        )
    except FestivalCreationRejected as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _festival_response(festival)

@router.post("/{festival_id}/publish",response_model=FestivalRead)
def publish_festival(
    festival_id:int,
    handler:PublishFestivalHandler=Depends(get_publish_festival_handler),
):
    return publish_festival_response(handler,festival_id)

@router.put("/{festival_id}/concerts/{concert_id}/reschedule",response_model=ConcertRead)
def reschedule_festival_concert(
    festival_id:int,
    concert_id:int,
    payload:ConcertReschedule,
    handler:RescheduleConcertHandler=Depends(get_reschedule_concert_handler),
):
    return reschedule_concert_response(handler,festival_id,concert_id,payload)

@router.post("/{festival_id}/concerts",response_model=ConcertRead,status_code=201)
def schedule_festival_concert(
    festival_id:int,
    payload:FestivalConcertCreate,
    handler:ScheduleConcertHandler=Depends(get_schedule_concert_handler),
):
    return schedule_concert_response(handler,festival_id,payload)

@router.post("/{festival_id}/concerts/{concert_id}/cancel",response_model=ConcertRead)
def cancel_festival_concert(
    festival_id:int,
    concert_id:int,
    handler:CancelConcertHandler=Depends(get_cancel_concert_handler),
):
    return cancel_concert_response(handler,festival_id,concert_id)