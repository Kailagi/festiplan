from datetime import datetime

import pytest

from app.application.commands import ScheduleConcertCommand
from app.application.exceptions import ConcertScheduleRejected, FestivalNotFound
from app.application.use_cases.schedule_concert import ScheduleConcertHandler
from app.domain.entities import Artist, Concert, Festival, Stage
from app.domain.events import ConcertScheduled, DomainEvent
from app.domain.value_objects import EquipmentSet, FestivalPeriod, TimeSlot


def dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


class InMemoryFestivalRepository:
    def __init__(self, festival: Festival | None) -> None:
        self.festival = festival
        self.saved: list[Festival] = []

    def get_by_id(self, festival_id: int) -> Festival | None:
        return self.festival if self.festival and self.festival.id == festival_id else None

    def get_by_concert_id(self, concert_id: int) -> Festival | None:
        return None

    def next_concert_id(self) -> int:
        return max((concert.id for concert in self.festival.concerts), default=0) + 1

    def save(self, festival: Festival) -> None:
        self.saved.append(festival)


class InMemoryArtistRepository:
    def get_by_id(self, artist_id: int) -> Artist | None:
        if artist_id == 200:
            return Artist(200, "Test Artist", "Metal", EquipmentSet())
        return None


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


def make_festival() -> Festival:
    return Festival(
        id=1,
        period=FestivalPeriod(dt("2027-06-18T10:00:00"), dt("2027-06-20T23:59:00")),
        stages=[Stage(10, 1)],
        concerts=[],
    )


def test_handler_schedules_concert_and_commits_outbox_event() -> None:
    festival = make_festival()
    unit_of_work = InMemoryUnitOfWork(festival)
    handler = ScheduleConcertHandler(unit_of_work)
    slot = TimeSlot(dt("2027-06-18T15:00:00"), dt("2027-06-18T16:00:00"))

    result = handler.execute(ScheduleConcertCommand(1, 200, 10, slot))

    assert result.concert in festival.concerts
    assert result.concert.time_slot == slot
    assert unit_of_work.festivals.saved == [festival]
    assert unit_of_work.outbox.events[0].concert_id == result.concert.id
    assert unit_of_work.committed


def test_handler_does_not_commit_when_domain_rejects_conflict() -> None:
    festival = make_festival()
    festival.concerts.append(
        Concert(1, 201, 10, TimeSlot(dt("2027-06-18T15:00:00"), dt("2027-06-18T16:00:00")))
    )
    unit_of_work = InMemoryUnitOfWork(festival)
    handler = ScheduleConcertHandler(unit_of_work)

    with pytest.raises(ConcertScheduleRejected, match="scène est déjà occupée"):
        handler.execute(
            ScheduleConcertCommand(
                1, 200, 10,
                TimeSlot(dt("2027-06-18T15:30:00"), dt("2027-06-18T16:30:00")),
            )
        )

    assert unit_of_work.festivals.saved == []
    assert unit_of_work.outbox.events == []
    assert not unit_of_work.committed


def test_handler_rejects_missing_festival() -> None:
    unit_of_work = InMemoryUnitOfWork(None)
    handler = ScheduleConcertHandler(unit_of_work)

    with pytest.raises(FestivalNotFound):
        handler.execute(
            ScheduleConcertCommand(
                1, 200, 10,
                TimeSlot(dt("2027-06-18T15:00:00"), dt("2027-06-18T16:00:00")),
            )
        )

    assert not unit_of_work.committed
