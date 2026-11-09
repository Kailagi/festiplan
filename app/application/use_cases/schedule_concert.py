from app.application.commands import ScheduleConcertCommand
from app.application.exceptions import (
    ArtistNotFound,
    ConcertScheduleRejected,
    FestivalNotFound,
)
from app.application.ports.outbound.unit_of_work import UnitOfWork
from app.application.results import ScheduleConcertResult
from app.domain.errors import DomainError


class ScheduleConcertHandler:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    def execute(self, command: ScheduleConcertCommand) -> ScheduleConcertResult:
        with self._unit_of_work as unit_of_work:
            festival = unit_of_work.festivals.get_by_id(command.festival_id)
            if festival is None:
                raise FestivalNotFound(command.festival_id)

            artist = unit_of_work.artists.get_by_id(command.artist_id)
            if artist is None:
                raise ArtistNotFound(command.artist_id)

            concert_id = unit_of_work.festivals.next_concert_id()
            try:
                concert = festival.schedule_concert(
                    concert_id=concert_id,
                    artist_id=artist.id,
                    stage_id=command.stage_id,
                    time_slot=command.time_slot,
                    required_equipment=artist.required_equipment,
                )
            except DomainError as exc:
                raise ConcertScheduleRejected(str(exc)) from exc

            events = festival.pull_domain_events()
            unit_of_work.festivals.save(festival)
            for event in events:
                unit_of_work.outbox.add(event)
            unit_of_work.commit()
            return ScheduleConcertResult(festival_id=festival.id, concert=concert)
