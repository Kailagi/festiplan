from datetime import datetime

import pytest

from app.application.commands import RescheduleConcertCommand
from app.application.exceptions import ConcertRescheduleRejected, FestivalNotFound
from app.application.use_cases.reschedule_concert import RescheduleConcertHandler
from app.domain.entities import Artist, Concert, Festival, Stage
from app.domain.value_objects import EquipmentSet
from app.domain.errors import DomainError
from app.domain.events import ConcertRescheduled, DomainEvent
from app.domain.value_objects import FestivalPeriod, TimeSlot


def dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


class InMemoryFestivalRepository:
    def __init__(self, festival: Festival | None) -> None:
        self.festival = festival
        self.saved: list[Festival] = []

    def get_by_id(self, festival_id: int) -> Festival | None:
        if self.festival is not None and self.festival.id == festival_id:
            return self.festival
        return None

    def next_concert_id(self) -> int:
        if self.festival is None or not self.festival.concerts:
            return 1
        return max(concert.id for concert in self.festival.concerts) + 1

    def get_by_concert_id(self, concert_id: int) -> Festival | None:
        if self.festival is not None and any(
            concert.id == concert_id for concert in self.festival.concerts
        ):
            return self.festival
        return None

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
        self.artists = InMemoryArtistRepository()
        self.outbox = InMemoryOutbox()
        self.committed = False

    def __enter__(self) -> "InMemoryUnitOfWork":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        return None

    def commit(self) -> None:
        self.committed = True


class InMemoryArtistRepository:
    def get_by_id(self, artist_id: int) -> Artist | None:
        if artist_id == 200:
            return Artist(200, "Test Artist", "Metal", EquipmentSet())
        return None


def make_festival() -> Festival:
    return Festival(
        id=1,
        period=FestivalPeriod(dt("2027-06-18T10:00:00"), dt("2027-06-20T23:59:00")),
        stages=[Stage(id=10, festival_id=1)],
        concerts=[
            Concert(
                id=100,
                artist_id=200,
                stage_id=10,
                time_slot=TimeSlot(dt("2027-06-18T15:00:00"), dt("2027-06-18T16:00:00")),
            )
        ],
    )


def test_handler_reschedules_and_saves_festival() -> None:
    festival = make_festival()
    unit_of_work = InMemoryUnitOfWork(festival)
    handler = RescheduleConcertHandler(unit_of_work)
    new_slot = TimeSlot(dt("2027-06-18T17:00:00"), dt("2027-06-18T18:00:00"))

    result = handler.execute(RescheduleConcertCommand(1, 100, new_slot))

    assert result.concert.time_slot == new_slot
    assert unit_of_work.festivals.saved == [festival]
    assert unit_of_work.outbox.events[0].new_time_slot == new_slot
    assert unit_of_work.committed


def test_handler_does_not_save_when_domain_rejects_reschedule() -> None:
    festival = make_festival()
    unit_of_work = InMemoryUnitOfWork(festival)
    handler = RescheduleConcertHandler(unit_of_work)
    occupied_slot = TimeSlot(dt("2027-06-18T15:30:00"), dt("2027-06-18T16:30:00"))
    festival.concerts.append(
        Concert(101, 201, 10, TimeSlot(dt("2027-06-18T16:00:00"), dt("2027-06-18T17:00:00")))
    )

    with pytest.raises(ConcertRescheduleRejected) as exc_info:
        handler.execute(RescheduleConcertCommand(1, 100, occupied_slot))

    assert isinstance(exc_info.value.__cause__, DomainError)
    assert unit_of_work.festivals.saved == []
    assert unit_of_work.outbox.events == []
    assert not unit_of_work.committed


def test_handler_rejects_missing_festival() -> None:
    unit_of_work = InMemoryUnitOfWork(None)
    handler = RescheduleConcertHandler(unit_of_work)
    command = RescheduleConcertCommand(
        999,
        100,
        TimeSlot(dt("2027-06-18T17:00:00"), dt("2027-06-18T18:00:00")),
    )

    with pytest.raises(FestivalNotFound):
        handler.execute(command)

    assert unit_of_work.festivals.saved == []
    assert not unit_of_work.committed
