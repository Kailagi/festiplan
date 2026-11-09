from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import FestivalCreate, FestivalRead
from app.services.festival_service import FestivalService
from app.api.dependencies import get_reschedule_concert_handler
from app.api.reschedule import reschedule_concert_response
from app.application.use_cases.reschedule_concert import RescheduleConcertHandler
from app.schemas import ConcertRead, ConcertReschedule
from app.api.schedule import schedule_concert_response
from app.api.dependencies import get_schedule_concert_handler
from app.application.use_cases.schedule_concert import ScheduleConcertHandler
from app.schemas import FestivalConcertCreate
from app.api.cancel import cancel_concert_response
from app.api.dependencies import get_cancel_concert_handler
from app.application.use_cases.cancel_concert import CancelConcertHandler
from app.api.publish import publish_festival_response
from app.api.dependencies import get_publish_festival_handler
from app.application.use_cases.publish_festival import PublishFestivalHandler

router=APIRouter(prefix="/festivals",tags=["festivals"])

@router.get("",response_model=list[FestivalRead])
def list_festivals(db:Session=Depends(get_db)): 
    return FestivalService(db).list_festivals()

@router.post("",response_model=FestivalRead,status_code=201)
def create_festival(payload:FestivalCreate,db:Session=Depends(get_db)):
    try:
        return FestivalService(db).create_festival(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400,detail=str(exc))

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