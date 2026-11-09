from fastapi import APIRouter, Depends, HTTPException
from app.schemas import (
    ConcertCreate,
    ConcertRead,
    ConcertReschedule,
    FestivalConcertCreate,
)
from app.api.dependencies import (
    get_cancel_concert_handler,
    get_read_concerts_handler,
    get_reschedule_concert_handler,
    get_schedule_concert_handler,
)
from app.api.schedule import schedule_concert_response
from app.api.reschedule import reschedule_concert_response
from app.api.cancel import cancel_concert_response
from app.application.use_cases.read_concerts import ReadConcertsHandler
from app.application.use_cases.schedule_concert import ScheduleConcertHandler
from app.application.use_cases.cancel_concert import CancelConcertHandler
from app.application.use_cases.reschedule_concert import RescheduleConcertHandler
from app.application.ports.outbound.concert_reader import ConcertView

router = APIRouter(prefix="/concerts", tags=["concerts"])


def _concert_response(concert: ConcertView) -> dict[str, object]:
    return {
        "id": concert.id,
        "festival_id": concert.festival_id,
        "artist_id": concert.artist_id,
        "stage_id": concert.stage_id,
        "start_time": concert.start_time,
        "end_time": concert.end_time,
        "status": concert.status,
    }


@router.get("", response_model=list[ConcertRead])
def list_concerts(
    festival_id: int,
    handler: ReadConcertsHandler = Depends(get_read_concerts_handler),
):
    return [_concert_response(concert) for concert in handler.list_for_festival(festival_id)]


@router.get("/schedule/{festival_id}", response_model=list[ConcertRead])
def get_schedule(
    festival_id: int,
    handler: ReadConcertsHandler = Depends(get_read_concerts_handler),
):
    return list_concerts(festival_id, handler)


@router.get("/{concert_id}", response_model=ConcertRead)
def get_concert(
    concert_id: int,
    handler: ReadConcertsHandler = Depends(get_read_concerts_handler),
):
    concert = handler.get_by_id(concert_id)
    if concert is None:
        raise HTTPException(status_code=404, detail="Concert introuvable")
    return _concert_response(concert)


@router.post("", response_model=ConcertRead, status_code=201)
def create_concert(
    payload: ConcertCreate,
    handler: ScheduleConcertHandler = Depends(get_schedule_concert_handler),
):
    return schedule_concert_response(
        handler,
        payload.festival_id,
        FestivalConcertCreate(
            artist_id=payload.artist_id,
            stage_id=payload.stage_id,
            start_time=payload.start_time,
            end_time=payload.end_time,
        ),
    )

@router.patch("/{concert_id}/reschedule", response_model=ConcertRead)
def reschedule_concert(
    concert_id:int,
    payload:ConcertReschedule,
    handler:RescheduleConcertHandler=Depends(get_reschedule_concert_handler),
):
    return reschedule_concert_response(handler,None,concert_id,payload)

@router.post("/{concert_id}/cancel", response_model=ConcertRead)
def cancel_concert(
    concert_id:int,
    handler:CancelConcertHandler=Depends(get_cancel_concert_handler),
):
    return cancel_concert_response(handler,None,concert_id)
