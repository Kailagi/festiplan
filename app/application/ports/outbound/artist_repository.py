from typing import Protocol

from app.domain.entities import Artist
from app.domain.value_objects import EquipmentSet


class ArtistRepository(Protocol):
    def list_all(self) -> list[Artist]:
        """Return all artists."""
        ...

    def create(
        self,
        name: str,
        genre: str,
        required_equipment: EquipmentSet,
    ) -> Artist:
        """Create and return an artist."""
        ...

    def get_by_id(self, artist_id: int) -> Artist | None:
        """Return the artist, or None when it does not exist."""
        ...
