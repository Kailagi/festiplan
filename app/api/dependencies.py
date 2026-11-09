from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.use_cases.cancel_concert import CancelConcertHandler
from app.application.use_cases.publish_festival import PublishFestivalHandler
from app.application.use_cases.reschedule_concert import RescheduleConcertHandler
from app.application.use_cases.schedule_concert import ScheduleConcertHandler
from app.bootstrap.container import (
    build_cancel_concert_handler,
    build_publish_festival_handler,
    build_reschedule_concert_handler,
    build_schedule_concert_handler,
)
from app.database import get_db


def get_reschedule_concert_handler(
    session: Session = Depends(get_db),
) -> RescheduleConcertHandler:
    return build_reschedule_concert_handler(session)


def get_schedule_concert_handler(
    session: Session = Depends(get_db),
) -> ScheduleConcertHandler:
    return build_schedule_concert_handler(session)


def get_cancel_concert_handler(
    session: Session = Depends(get_db),
) -> CancelConcertHandler:
    return build_cancel_concert_handler(session)


def get_publish_festival_handler(
    session: Session = Depends(get_db),
) -> PublishFestivalHandler:
    return build_publish_festival_handler(session)
