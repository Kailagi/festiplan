from typing import Protocol

from app.domain.entities import Artist


class ArtistRepository(Protocol):
    def get_by_id(self, artist_id: int) -> Artist | None:
        """Return the artist, or None when it does not exist."""
        ...
