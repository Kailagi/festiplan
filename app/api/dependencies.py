from fastapi import Depends
from sqlalchemy.orm import Session

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
from app.application.use_cases.manage_artists import (
    CreateArtistHandler,
    ListArtistsHandler,
)
from app.application.use_cases.manage_stages import (
    CreateStageHandler,
    ListStagesHandler,
)
from app.application.use_cases.reschedule_concert import RescheduleConcertHandler
from app.application.use_cases.schedule_concert import ScheduleConcertHandler
from app.bootstrap.container import (
    build_cancel_concert_handler,
    build_publish_festival_handler,
    build_read_concerts_handler,
    build_create_festival_handler,
    build_list_festivals_handler,
    build_create_incident_handler,
    build_list_incidents_handler,
    build_create_artist_handler,
    build_list_artists_handler,
    build_create_stage_handler,
    build_list_stages_handler,
    build_reschedule_concert_handler,
    build_schedule_concert_handler,
)
from app.database import get_db


def get_create_artist_handler(
    session: Session = Depends(get_db),
) -> CreateArtistHandler:
    return build_create_artist_handler(session)


def get_list_artists_handler(
    session: Session = Depends(get_db),
) -> ListArtistsHandler:
    return build_list_artists_handler(session)


def get_create_stage_handler(
    session: Session = Depends(get_db),
) -> CreateStageHandler:
    return build_create_stage_handler(session)


def get_list_stages_handler(
    session: Session = Depends(get_db),
) -> ListStagesHandler:
    return build_list_stages_handler(session)


def get_list_festivals_handler(
    session: Session = Depends(get_db),
) -> ListFestivalsHandler:
    return build_list_festivals_handler(session)


def get_create_festival_handler(
    session: Session = Depends(get_db),
) -> CreateFestivalHandler:
    return build_create_festival_handler(session)


def get_create_incident_handler(
    session: Session = Depends(get_db),
) -> CreateIncidentHandler:
    return build_create_incident_handler(session)


def get_list_incidents_handler(
    session: Session = Depends(get_db),
) -> ListIncidentsHandler:
    return build_list_incidents_handler(session)


def get_read_concerts_handler(
    session: Session = Depends(get_db),
) -> ReadConcertsHandler:
    return build_read_concerts_handler(session)


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
