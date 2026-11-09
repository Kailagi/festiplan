from sqlalchemy.orm import Session

from app.adapters.outbound.sqlalchemy.unit_of_work import SqlAlchemyUnitOfWork
from app.application.use_cases.cancel_concert import CancelConcertHandler
from app.application.use_cases.publish_festival import PublishFestivalHandler
from app.application.use_cases.reschedule_concert import RescheduleConcertHandler
from app.application.use_cases.schedule_concert import ScheduleConcertHandler


def build_reschedule_concert_handler(session: Session) -> RescheduleConcertHandler:
    return RescheduleConcertHandler(SqlAlchemyUnitOfWork(session))


def build_schedule_concert_handler(session: Session) -> ScheduleConcertHandler:
    return ScheduleConcertHandler(SqlAlchemyUnitOfWork(session))


def build_cancel_concert_handler(session: Session) -> CancelConcertHandler:
    return CancelConcertHandler(SqlAlchemyUnitOfWork(session))


def build_publish_festival_handler(session: Session) -> PublishFestivalHandler:
    return PublishFestivalHandler(SqlAlchemyUnitOfWork(session))
