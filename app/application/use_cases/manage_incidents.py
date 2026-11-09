from app.application.commands import CreateIncidentCommand, ListIncidentsQuery
from app.application.exceptions import ConcertNotFound
from app.application.ports.outbound.unit_of_work import UnitOfWork
from app.domain.entities import Incident


class CreateIncidentHandler:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    def execute(self, command: CreateIncidentCommand) -> Incident:
        with self._unit_of_work as unit_of_work:
            if not unit_of_work.incidents.concert_exists(command.concert_id):
                raise ConcertNotFound(command.concert_id)
            incident = unit_of_work.incidents.add(
                concert_id=command.concert_id,
                description=command.description,
                occurred_at=command.occurred_at,
            )
            unit_of_work.commit()
            return incident


class ListIncidentsHandler:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    def execute(self, query: ListIncidentsQuery) -> list[Incident]:
        with self._unit_of_work as unit_of_work:
            return unit_of_work.incidents.list_for_concert(query.concert_id)
