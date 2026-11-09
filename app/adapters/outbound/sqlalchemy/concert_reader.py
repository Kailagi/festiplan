from sqlalchemy.orm import Session

from app.application.ports.outbound.concert_reader import ConcertView
from app.models import Concert


class SqlAlchemyConcertReader:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_for_festival(self, festival_id: int) -> list[ConcertView]:
        concerts = (
            self._session.query(Concert)
            .filter(
                Concert.festival_id == festival_id,
                Concert.status != "cancelled",
            )
            .order_by(Concert.start_time, Concert.id)
            .all()
        )
        return [self._to_view(concert) for concert in concerts]

    def get_by_id(self, concert_id: int) -> ConcertView | None:
        concert = (
            self._session.query(Concert)
            .filter(Concert.id == concert_id)
            .first()
        )
        return self._to_view(concert) if concert is not None else None

    @staticmethod
    def _to_view(concert: Concert) -> ConcertView:
        return ConcertView(
            id=concert.id,
            festival_id=concert.festival_id,
            artist_id=concert.artist_id,
            stage_id=concert.stage_id,
            start_time=concert.start_time,
            end_time=concert.end_time,
            status=concert.status,
        )
