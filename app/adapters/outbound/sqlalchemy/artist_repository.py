from sqlalchemy.orm import Session

from app.adapters.outbound.sqlalchemy.mappings import to_domain_artist
from app.application.ports.outbound.artist_repository import ArtistRepository
from app.domain.entities import Artist
from app.models import Artist as ArtistModel


class SqlAlchemyArtistRepository(ArtistRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, artist_id: int) -> Artist | None:
        model = self._session.query(ArtistModel).filter(ArtistModel.id == artist_id).first()
        return to_domain_artist(model) if model is not None else None
