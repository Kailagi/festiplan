from typing import Protocol

from app.domain.entities import Festival
from app.domain.value_objects import FestivalPeriod


class FestivalRepository(Protocol):
    def list_all(self) -> list[Festival]:
        """Return all festival aggregates."""
        ...

    def create(
        self,
        name: str,
        location: str,
        period: FestivalPeriod,
    ) -> Festival:
        """Create and return a festival aggregate."""
        ...

    def get_by_id(self, festival_id: int) -> Festival | None:
        """Return the festival aggregate, or None when it does not exist."""
        ...

    def get_by_concert_id(self, concert_id: int) -> Festival | None:
        """Return the festival containing the concert, if it exists."""
        ...

    def save(self, festival: Festival) -> None:
        """Persist the changed festival aggregate."""
        ...
