from types import TracebackType

from sqlalchemy.orm import Session

from app.adapters.outbound.sqlalchemy.artist_repository import SqlAlchemyArtistRepository
from app.adapters.outbound.sqlalchemy.festival_repository import SqlAlchemyFestivalRepository
from app.adapters.outbound.sqlalchemy.incident_repository import SqlAlchemyIncidentRepository
from app.adapters.outbound.sqlalchemy.stage_repository import SqlAlchemyStageRepository
from app.adapters.outbound.sqlalchemy.outbox import SqlAlchemyOutbox


class SqlAlchemyUnitOfWork:
    def __init__(self, session: Session) -> None:
        self._session = session
        self.festivals = SqlAlchemyFestivalRepository(session)
        self.incidents = SqlAlchemyIncidentRepository(session)
        self.stages = SqlAlchemyStageRepository(session)
        self.artists = SqlAlchemyArtistRepository(session)
        self.outbox = SqlAlchemyOutbox(session)
        self._transaction = None

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        self._transaction = self._session.begin()
        return self

    def __exit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_value: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        if self._transaction is not None and self._transaction.is_active:
            self._transaction.rollback()

    def commit(self) -> None:
        if self._transaction is None:
            raise RuntimeError("L'unité de travail doit être ouverte avant le commit")
        self._transaction.commit()
