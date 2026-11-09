from app.application.commands import RescheduleConcertCommand
from app.application.exceptions import ConcertRescheduleRejected, FestivalNotFound
from app.application.ports.outbound.unit_of_work import UnitOfWork
from app.application.results import RescheduleConcertResult
from app.domain.errors import DomainError


class RescheduleConcertHandler:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    def execute(self, command: RescheduleConcertCommand) -> RescheduleConcertResult:
        with self._unit_of_work as unit_of_work:
            if command.festival_id is None:
                festival = unit_of_work.festivals.get_by_concert_id(command.concert_id)
            else:
                festival = unit_of_work.festivals.get_by_id(command.festival_id)
            if festival is None:
                raise FestivalNotFound(command.festival_id)

            try:
                concert = festival.reschedule_concert(
                    command.concert_id,
                    command.new_time_slot,
                )
            except DomainError as exc:
                raise ConcertRescheduleRejected(str(exc)) from exc

            events = festival.pull_domain_events()
            unit_of_work.festivals.save(festival)
            for event in events:
                unit_of_work.outbox.add(event)
            unit_of_work.commit()
            return RescheduleConcertResult(festival_id=festival.id, concert=concert)
