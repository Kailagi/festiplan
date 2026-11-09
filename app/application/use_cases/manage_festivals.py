from app.application.commands import CreateFestivalCommand
from app.application.exceptions import FestivalCreationRejected
from app.application.ports.outbound.unit_of_work import UnitOfWork
from app.domain.entities import Festival
from app.domain.value_objects import FestivalPeriod


class ListFestivalsHandler:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    def execute(self) -> list[Festival]:
        with self._unit_of_work as unit_of_work:
            return unit_of_work.festivals.list_all()


class CreateFestivalHandler:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    def execute(self, command: CreateFestivalCommand) -> Festival:
        try:
            period = FestivalPeriod(command.start_date, command.end_date)
        except ValueError as exc:
            raise FestivalCreationRejected(str(exc)) from exc

        with self._unit_of_work as unit_of_work:
            festival = unit_of_work.festivals.create(
                name=command.name,
                location=command.location,
                period=period,
            )
            unit_of_work.commit()
            return festival
