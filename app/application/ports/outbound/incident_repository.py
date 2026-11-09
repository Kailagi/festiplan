from datetime import datetime
from typing import Protocol

from app.domain.entities import Incident


class IncidentRepository(Protocol):
    def concert_exists(self, concert_id: int) -> bool:
        """Return whether the referenced concert exists."""
        ...

    def add(
        self,
        concert_id: int,
        description: str,
        occurred_at: datetime | None,
    ) -> Incident:
        """Create and return an incident."""
        ...

    def list_for_concert(self, concert_id: int | None) -> list[Incident]:
        """Return incidents, optionally filtered by concert."""
        ...
