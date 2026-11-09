from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.domain.events import (
    ConcertCancelled,
    ConcertRescheduled,
    ConcertScheduled,
    DomainEvent,
    FestivalPublished,
)
from app.models import OutboxEvent


class SqlAlchemyOutbox:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, event: DomainEvent) -> None:
        if isinstance(event, ConcertScheduled):
            event_type = "ConcertScheduled"
            payload = {
                "festival_id": event.festival_id,
                "concert_id": event.concert_id,
                "stage_id": event.stage_id,
                "artist_id": event.artist_id,
                "start": event.time_slot.start.isoformat(),
                "end": event.time_slot.end.isoformat(),
            }
        elif isinstance(event, ConcertRescheduled):
            event_type = "ConcertRescheduled"
            payload = {
                "festival_id": event.festival_id,
                "concert_id": event.concert_id,
                "previous_start": event.previous_time_slot.start.isoformat(),
                "previous_end": event.previous_time_slot.end.isoformat(),
                "new_start": event.new_time_slot.start.isoformat(),
                "new_end": event.new_time_slot.end.isoformat(),
            }
        elif isinstance(event, ConcertCancelled):
            event_type = "ConcertCancelled"
            payload = {
                "festival_id": event.festival_id,
                "concert_id": event.concert_id,
            }
        elif isinstance(event, FestivalPublished):
            event_type = "FestivalPublished"
            payload = {"festival_id": event.festival_id}
        else:
            raise TypeError(f"Événement de domaine non pris en charge : {type(event).__name__}")

        self._session.add(
            OutboxEvent(
                event_type=event_type,
                payload=payload,
                occurred_at=datetime.now(timezone.utc),
            )
        )
