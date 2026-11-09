from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.domain.entities import Incident
from app.models import Concert, Incident as IncidentModel


class SqlAlchemyIncidentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def concert_exists(self, concert_id: int) -> bool:
        return (
            self._session.query(Concert.id)
            .filter(Concert.id == concert_id)
            .first()
            is not None
        )

    def add(
        self,
        concert_id: int,
        description: str,
        occurred_at: datetime | None,
    ) -> Incident:
        model = IncidentModel(
            concert_id=concert_id,
            description=description,
            occurred_at=occurred_at
            or datetime.now(timezone.utc).replace(tzinfo=None),
        )
        self._session.add(model)
        self._session.flush()
        return self._to_domain(model)

    def list_for_concert(self, concert_id: int | None) -> list[Incident]:
        query = self._session.query(IncidentModel)
        if concert_id is not None:
            query = query.filter(IncidentModel.concert_id == concert_id)
        models = query.order_by(IncidentModel.occurred_at.desc()).all()
        return [self._to_domain(model) for model in models]

    @staticmethod
    def _to_domain(model: IncidentModel) -> Incident:
        return Incident(
            id=model.id,
            concert_id=model.concert_id,
            description=model.description,
            occurred_at=model.occurred_at,
            resolved=model.resolved,
        )
