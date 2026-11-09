from sqlalchemy.orm import Session

from app.adapters.outbound.sqlalchemy.concert_reader import SqlAlchemyConcertReader
from app.adapters.outbound.sqlalchemy.unit_of_work import SqlAlchemyUnitOfWork
from app.application.use_cases.manage_artists import (
    CreateArtistHandler,
    ListArtistsHandler,
)
from app.application.use_cases.cancel_concert import CancelConcertHandler
from app.application.use_cases.publish_festival import PublishFestivalHandler
from app.application.use_cases.read_concerts import ReadConcertsHandler
from app.application.use_cases.manage_festivals import (
    CreateFestivalHandler,
    ListFestivalsHandler,
)
from app.application.use_cases.manage_incidents import (
    CreateIncidentHandler,
    ListIncidentsHandler,
)
from app.application.use_cases.manage_stages import (
    CreateStageHandler,
    ListStagesHandler,
)

def build_read_concerts_handler(session: Session) -> ReadConcertsHandler:
    return ReadConcertsHandler(SqlAlchemyConcertReader(session))


def build_create_artist_handler(session: Session) -> CreateArtistHandler:
    return CreateArtistHandler(SqlAlchemyUnitOfWork(session))


def build_list_artists_handler(session: Session) -> ListArtistsHandler:
    return ListArtistsHandler(SqlAlchemyUnitOfWork(session))


def build_create_stage_handler(session: Session) -> CreateStageHandler:
    return CreateStageHandler(SqlAlchemyUnitOfWork(session))


def build_list_stages_handler(session: Session) -> ListStagesHandler:
    return ListStagesHandler(SqlAlchemyUnitOfWork(session))


def build_list_festivals_handler(session: Session) -> ListFestivalsHandler:
    return ListFestivalsHandler(SqlAlchemyUnitOfWork(session))


def build_create_festival_handler(session: Session) -> CreateFestivalHandler:
    return CreateFestivalHandler(SqlAlchemyUnitOfWork(session))


def build_create_incident_handler(session: Session) -> CreateIncidentHandler:
    return CreateIncidentHandler(SqlAlchemyUnitOfWork(session))


def build_list_incidents_handler(session: Session) -> ListIncidentsHandler:
    return ListIncidentsHandler(SqlAlchemyUnitOfWork(session))
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
