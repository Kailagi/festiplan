from typing import Protocol

from app.domain.entities import Festival


class FestivalRepository(Protocol):
    def next_concert_id(self) -> int:
        """Allocate an identifier for a new concert."""
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
