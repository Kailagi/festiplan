from sqlalchemy.orm import Session, selectinload
from app.adapters.outbound.sqlalchemy.mappings import apply_domain_festival, to_domain_festival
from app.application.ports.outbound.festival_repository import FestivalRepository
from app.domain.entities import Festival
from app.domain.value_objects import FestivalPeriod
from app.models import Concert as ConcertModel
from app.models import Festival as FestivalModel


class SqlAlchemyFestivalRepository(FestivalRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_all(self) -> list[Festival]:
        models = (
            self._session.query(FestivalModel)
            .options(
                selectinload(FestivalModel.stages),
                selectinload(FestivalModel.concerts).selectinload(ConcertModel.artist),
            )
            .order_by(FestivalModel.id)
            .all()
        )
        return [to_domain_festival(model) for model in models]

    def create(self, name: str, location: str, period: FestivalPeriod) -> Festival:
        model = FestivalModel(
            name=name,
            location=location,
            start_date=period.start,
            end_date=period.end,
            status="preparation",
        )
        self._session.add(model)
        self._session.flush()
        return to_domain_festival(model)

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
        pending_concerts = apply_domain_festival(festival, model)
        self._session.flush()
        for concert, persistence_concert in pending_concerts:
            if persistence_concert.id is None:
                raise RuntimeError("La base n'a pas attribué d'identifiant au concert")
            concert.id = persistence_concert.id
