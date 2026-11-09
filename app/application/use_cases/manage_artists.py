from app.application.commands import CreateArtistCommand
from app.application.ports.outbound.unit_of_work import UnitOfWork
from app.domain.entities import Artist


class CreateArtistHandler:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    def execute(self, command: CreateArtistCommand) -> Artist:
        with self._unit_of_work as unit_of_work:
            artist = unit_of_work.artists.create(
                name=command.name,
                genre=command.genre,
                required_equipment=command.required_equipment,
            )
            unit_of_work.commit()
            return artist


class ListArtistsHandler:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    def execute(self) -> list[Artist]:
        with self._unit_of_work as unit_of_work:
            return unit_of_work.artists.list_all()
