from sqlalchemy.orm import Session

from app.adapters.outbound.sqlalchemy.mappings import to_domain_stage
from app.application.ports.outbound.stage_repository import StageRepository
from app.domain.entities import Stage
from app.domain.value_objects import EquipmentSet
from app.models import Stage as StageModel


class SqlAlchemyStageRepository(StageRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_for_festival(self, festival_id: int) -> list[Stage]:
        models = (
            self._session.query(StageModel)
            .filter(StageModel.festival_id == festival_id)
            .order_by(StageModel.id)
            .all()
        )
        return [to_domain_stage(model) for model in models]

    def create(
        self,
        festival_id: int,
        name: str,
        capacity: int,
        available_equipment: EquipmentSet,
    ) -> Stage:
        model = StageModel(
            festival_id=festival_id,
            name=name,
            capacity=capacity,
            available_equipment=",".join(sorted(available_equipment.items)),
        )
        self._session.add(model)
        self._session.flush()
        return to_domain_stage(model)
