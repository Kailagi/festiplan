from sqlalchemy.orm import Session

from app.adapters.outbound.sqlalchemy.mappings import to_domain_artist
from app.application.ports.outbound.artist_repository import ArtistRepository
from app.domain.entities import Artist
from app.domain.value_objects import EquipmentSet
from app.models import Artist as ArtistModel


class SqlAlchemyArtistRepository(ArtistRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_all(self) -> list[Artist]:
        models = self._session.query(ArtistModel).order_by(ArtistModel.name).all()
        return [to_domain_artist(model) for model in models]

    def create(
        self,
        name: str,
        genre: str,
        required_equipment: EquipmentSet,
    ) -> Artist:
        model = ArtistModel(
            name=name,
            genre=genre,
            required_equipment=",".join(sorted(required_equipment.items)),
        )
        self._session.add(model)
        self._session.flush()
        return to_domain_artist(model)

    def get_by_id(self, artist_id: int) -> Artist | None:
        model = self._session.query(ArtistModel).filter(ArtistModel.id == artist_id).first()
        return to_domain_artist(model) if model is not None else None
