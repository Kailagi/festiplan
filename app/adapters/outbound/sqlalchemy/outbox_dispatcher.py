from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import OutboxEvent
from app.utils.email_sender import send_email


class SqlAlchemyOutboxDispatcher:
    def __init__(self, session: Session) -> None:
        self._session = session

    def dispatch_pending(self, limit: int = 100) -> int:
        pending_events = (
            self._session.query(OutboxEvent)
            .filter(OutboxEvent.processed_at.is_(None))
            .order_by(OutboxEvent.id)
            .limit(limit)
            .all()
        )
        dispatched = 0

        for event in pending_events:
            if event.event_type not in {
                "ConcertRescheduled",
                "ConcertScheduled",
                "ConcertCancelled",
                "FestivalPublished",
            }:
                raise ValueError(f"Type d'événement d'outbox non pris en charge : {event.event_type}")

            try:
                if event.event_type == "ConcertCancelled":
                    subject = f"Annulation du concert #{event.payload['concert_id']}"
                    body = f"Le concert #{event.payload['concert_id']} a été annulé."
                elif event.event_type == "FestivalPublished":
                    subject = f"Festival #{event.payload['festival_id']} publié"
                    body = f"Le festival {event.payload['festival_id']} a été publié."
                else:
                    action = "programmé" if event.event_type == "ConcertScheduled" else "déplacé"
                    event_time = (
                        event.payload["start"]
                        if event.event_type == "ConcertScheduled"
                        else event.payload["new_start"]
                    )
                    subject = f"Planning du concert #{event.payload['concert_id']}"
                    body = f"Concert {action} au {event_time}"
                send_email("production@festiplan.test", subject, body)
            except RuntimeError as exc:
                event.attempts += 1
                event.last_error = str(exc)
                self._session.commit()
                raise

            event.attempts += 1
            event.last_error = None
            event.processed_at = datetime.now(timezone.utc)
            self._session.commit()
            dispatched += 1

        return dispatched
