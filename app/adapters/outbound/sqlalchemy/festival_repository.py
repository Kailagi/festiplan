from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func

from app.adapters.outbound.sqlalchemy.mappings import apply_domain_festival, to_domain_festival
from app.application.ports.outbound.festival_repository import FestivalRepository
from app.domain.entities import Festival
from app.models import Concert as ConcertModel
from app.models import Festival as FestivalModel
from app.models import Concert as ConcertTable


class SqlAlchemyFestivalRepository(FestivalRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def next_concert_id(self) -> int:
        highest_id = self._session.query(func.max(ConcertTable.id)).scalar()
        return (highest_id or 0) + 1

    def get_by_id(self, festival_id: int) -> Festival | None:
        model = (
            self._session.query(FestivalModel)
            .options(
                selectinload(FestivalModel.stages),
                selectinload(FestivalModel.concerts).selectinload(ConcertModel.artist),
            )
            .filter(FestivalModel.id == festival_id)
            .first()
        )
        return to_domain_festival(model) if model is not None else None

    def get_by_concert_id(self, concert_id: int) -> Festival | None:
        festival_id = (
            self._session.query(ConcertModel.festival_id)
            .filter(ConcertModel.id == concert_id)
            .scalar()
        )
        return self.get_by_id(festival_id) if festival_id is not None else None

    def save(self, festival: Festival) -> None:
        model = (
            self._session.query(FestivalModel)
            .options(selectinload(FestivalModel.concerts))
            .filter(FestivalModel.id == festival.id)
            .first()
        )
        if model is None:
            raise ValueError(f"Festival {festival.id} absent lors de la sauvegarde")
        apply_domain_festival(festival, model)
