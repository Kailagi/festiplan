from app.application.commands import CancelConcertCommand
from app.application.exceptions import ConcertCancelRejected, ConcertNotFound, FestivalNotFound
from app.application.ports.outbound.unit_of_work import UnitOfWork
from app.application.results import CancelConcertResult
from app.domain.errors import ConcertNotFound as DomainConcertNotFound
from app.domain.errors import DomainError


class CancelConcertHandler:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    def execute(self, command: CancelConcertCommand) -> CancelConcertResult:
        with self._unit_of_work as unit_of_work:
            if command.festival_id is None:
                festival = unit_of_work.festivals.get_by_concert_id(command.concert_id)
            else:
                festival = unit_of_work.festivals.get_by_id(command.festival_id)
            if festival is None:
                raise FestivalNotFound(command.festival_id)

            try:
                concert = festival.cancel_concert(command.concert_id)
            except DomainConcertNotFound as exc:
                raise ConcertNotFound(command.concert_id) from exc
            except DomainError as exc:
                raise ConcertCancelRejected(str(exc)) from exc

            events = festival.pull_domain_events()
            unit_of_work.festivals.save(festival)
            for event in events:
                unit_of_work.outbox.add(event)
            unit_of_work.commit()
            return CancelConcertResult(festival_id=festival.id, concert=concert)
