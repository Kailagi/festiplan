from app.application.commands import CreateStageCommand
from app.application.exceptions import FestivalNotFound
from app.application.ports.outbound.unit_of_work import UnitOfWork
from app.domain.entities import Stage


class CreateStageHandler:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    def execute(self, command: CreateStageCommand) -> Stage:
        with self._unit_of_work as unit_of_work:
            festival = unit_of_work.festivals.get_by_id(command.festival_id)
            if festival is None:
                raise FestivalNotFound(command.festival_id)
            stage = unit_of_work.stages.create(
                festival_id=command.festival_id,
                name=command.name,
                capacity=command.capacity,
                available_equipment=command.available_equipment,
            )
            unit_of_work.commit()
            return stage


class ListStagesHandler:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    def execute(self, festival_id: int) -> list[Stage]:
        with self._unit_of_work as unit_of_work:
            return unit_of_work.stages.list_for_festival(festival_id)
