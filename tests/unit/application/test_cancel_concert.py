from datetime import datetime

import pytest

from app.application.commands import CancelConcertCommand
from app.application.exceptions import ConcertCancelRejected, ConcertNotFound, FestivalNotFound
from app.application.use_cases.cancel_concert import CancelConcertHandler
from app.domain.entities import Concert, ConcertStatus, Festival, Stage
from app.domain.events import ConcertCancelled, DomainEvent
from app.domain.value_objects import FestivalPeriod, TimeSlot


def dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


class InMemoryFestivalRepository:
    def __init__(self, festival: Festival | None) -> None:
        self.festival = festival
        self.saved: list[Festival] = []

    def get_by_id(self, festival_id: int) -> Festival | None:
        return self.festival if self.festival and self.festival.id == festival_id else None

    def get_by_concert_id(self, concert_id: int) -> Festival | None:
        if self.festival and any(item.id == concert_id for item in self.festival.concerts):
            return self.festival
        return None

    def next_concert_id(self) -> int:
        return 1

    def save(self, festival: Festival) -> None:
        self.saved.append(festival)


class InMemoryOutbox:
    def __init__(self) -> None:
        self.events: list[DomainEvent] = []

    def add(self, event: DomainEvent) -> None:
        self.events.append(event)


class InMemoryUnitOfWork:
    def __init__(self, festival: Festival | None) -> None:
        self.festivals = InMemoryFestivalRepository(festival)
        self.outbox = InMemoryOutbox()
        self.committed = False

    def __enter__(self) -> "InMemoryUnitOfWork":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        return None

    def commit(self) -> None:
        self.committed = True


def make_festival() -> Festival:
    return Festival(
        id=1,
        period=FestivalPeriod(dt("2027-06-18T10:00:00"), dt("2027-06-20T23:59:00")),
        stages=[Stage(10, 1)],
        concerts=[
            Concert(100, 200, 10, TimeSlot(dt("2027-06-18T15:00:00"), dt("2027-06-18T16:00:00")))
        ],
    )


def test_handler_cancels_concert_and_commits_outbox_event() -> None:
    festival = make_festival()
    unit_of_work = InMemoryUnitOfWork(festival)
    handler = CancelConcertHandler(unit_of_work)

    result = handler.execute(CancelConcertCommand(1, 100))

    assert result.concert.status is ConcertStatus.CANCELLED
    assert unit_of_work.festivals.saved == [festival]
    assert unit_of_work.outbox.events == [ConcertCancelled(1, 100)]
    assert unit_of_work.committed


def test_handler_returns_not_found_when_concert_does_not_exist() -> None:
    unit_of_work = InMemoryUnitOfWork(make_festival())
    handler = CancelConcertHandler(unit_of_work)

    with pytest.raises(ConcertNotFound, match="introuvable"):
        handler.execute(CancelConcertCommand(1, 999))

    assert unit_of_work.festivals.saved == []
    assert unit_of_work.outbox.events == []
    assert not unit_of_work.committed


def test_handler_rejects_missing_festival() -> None:
    unit_of_work = InMemoryUnitOfWork(None)
    handler = CancelConcertHandler(unit_of_work)

    with pytest.raises(FestivalNotFound):
        handler.execute(CancelConcertCommand(1, 100))

    assert not unit_of_work.committed


def test_handler_rejects_cancelling_an_already_cancelled_concert() -> None:
    festival = make_festival()
    festival.concerts[0].status = ConcertStatus.CANCELLED
    unit_of_work = InMemoryUnitOfWork(festival)
    handler = CancelConcertHandler(unit_of_work)

    with pytest.raises(ConcertCancelRejected, match="déjà annulé"):
        handler.execute(CancelConcertCommand(1, 100))

    assert not unit_of_work.committed
