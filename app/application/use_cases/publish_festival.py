from app.application.commands import PublishFestivalCommand
from app.application.exceptions import FestivalNotFound, FestivalPublishRejected
from app.application.ports.outbound.unit_of_work import UnitOfWork
from app.application.results import PublishFestivalResult
from app.domain.errors import DomainError


class PublishFestivalHandler:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    def execute(self, command: PublishFestivalCommand) -> PublishFestivalResult:
        with self._unit_of_work as unit_of_work:
            festival = unit_of_work.festivals.get_by_id(command.festival_id)
            if festival is None:
                raise FestivalNotFound(command.festival_id)

            try:
                festival.publish()
            except DomainError as exc:
                raise FestivalPublishRejected(str(exc)) from exc

            events = festival.pull_domain_events()
            unit_of_work.festivals.save(festival)
            for event in events:
                unit_of_work.outbox.add(event)
            unit_of_work.commit()
            return PublishFestivalResult(festival=festival)
