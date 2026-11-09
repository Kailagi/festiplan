from types import TracebackType
from typing import Protocol, Self

from app.application.ports.outbound.festival_repository import FestivalRepository
from app.application.ports.outbound.outbox import Outbox
from app.application.ports.outbound.artist_repository import ArtistRepository
from app.application.ports.outbound.incident_repository import IncidentRepository
from app.application.ports.outbound.stage_repository import StageRepository


class UnitOfWork(Protocol):
    festivals: FestivalRepository
    artists: ArtistRepository
    outbox: Outbox
    incidents: IncidentRepository
    stages: StageRepository

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...

    def commit(self) -> None: ...
