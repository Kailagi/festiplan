from typing import Protocol

from app.domain.entities import Stage
from app.domain.value_objects import EquipmentSet


class StageRepository(Protocol):
    def list_for_festival(self, festival_id: int) -> list[Stage]:
        """Return the stages belonging to a festival."""
        ...

    def create(
        self,
        festival_id: int,
        name: str,
        capacity: int,
        available_equipment: EquipmentSet,
    ) -> Stage:
        """Create and return a stage."""
        ...
