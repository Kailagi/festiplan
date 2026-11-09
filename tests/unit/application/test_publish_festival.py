from datetime import datetime

import pytest

from app.application.commands import PublishFestivalCommand
from app.application.exceptions import FestivalNotFound, FestivalPublishRejected
from app.application.use_cases.publish_festival import PublishFestivalHandler
from app.domain.entities import Concert, Festival, FestivalStatus, Stage
from app.domain.events import DomainEvent, FestivalPublished
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


def test_handler_publishes_and_commits_outbox_event() -> None:
    festival = make_festival()
    unit_of_work = InMemoryUnitOfWork(festival)
    handler = PublishFestivalHandler(unit_of_work)

    result = handler.execute(PublishFestivalCommand(1))

    assert result.festival.status is FestivalStatus.PUBLISHED
    assert unit_of_work.festivals.saved == [festival]
    assert unit_of_work.outbox.events == [FestivalPublished(1)]
    assert unit_of_work.committed


def test_handler_translates_double_publication_and_does_not_commit() -> None:
    festival = make_festival()
    festival.publish()
    festival.pull_domain_events()
    unit_of_work = InMemoryUnitOfWork(festival)
    handler = PublishFestivalHandler(unit_of_work)

    with pytest.raises(FestivalPublishRejected, match="déjà publié"):
        handler.execute(PublishFestivalCommand(1))

    assert unit_of_work.festivals.saved == []
    assert unit_of_work.outbox.events == []
    assert not unit_of_work.committed


def test_handler_rejects_missing_festival() -> None:
    unit_of_work = InMemoryUnitOfWork(None)
    handler = PublishFestivalHandler(unit_of_work)

    with pytest.raises(FestivalNotFound):
        handler.execute(PublishFestivalCommand(999))

    assert not unit_of_work.committed
