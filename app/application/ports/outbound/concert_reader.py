from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True, slots=True)
class ConcertView:
    id: int
    festival_id: int
    artist_id: int
    stage_id: int
    start_time: datetime
    end_time: datetime
    status: str


class ConcertReader(Protocol):
    def list_for_festival(self, festival_id: int) -> list[ConcertView]:
        """Return the concerts scheduled for a festival."""
        ...

    def get_by_id(self, concert_id: int) -> ConcertView | None:
        """Return a concert by identifier, or None when it does not exist."""
        ...
