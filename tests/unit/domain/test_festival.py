from datetime import datetime

import pytest

from app.domain.entities import Concert, ConcertStatus, Festival, Stage
from app.domain.errors import DomainError
from app.domain.value_objects import EquipmentSet, FestivalPeriod, TimeSlot


def dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


def make_festival(
    *,
    concerts: list[Concert] | None = None,
    stages: list[Stage] | None = None,
) -> Festival:
    return Festival(
        id=1,
        period=FestivalPeriod(dt("2027-06-18T10:00:00"), dt("2027-06-20T23:59:00")),
        stages=stages if stages is not None else [Stage(id=10, festival_id=1)],
        concerts=concerts if concerts is not None else [
            Concert(
                id=100,
                artist_id=200,
                stage_id=10,
                time_slot=TimeSlot(dt("2027-06-18T15:00:00"), dt("2027-06-18T16:00:00")),
            )
        ],
    )


def test_time_slot_detects_partial_overlap() -> None:
    first = TimeSlot(dt("2027-06-18T15:00:00"), dt("2027-06-18T16:00:00"))
    second = TimeSlot(dt("2027-06-18T15:30:00"), dt("2027-06-18T16:30:00"))

    assert first.overlaps_with(second)
    assert second.overlaps_with(first)


def test_time_slot_allows_adjacent_slots() -> None:
    first = TimeSlot(dt("2027-06-18T15:00:00"), dt("2027-06-18T16:00:00"))
    second = TimeSlot(dt("2027-06-18T16:00:00"), dt("2027-06-18T17:00:00"))

    assert not first.overlaps_with(second)


def test_time_slot_rejects_non_positive_duration() -> None:
    with pytest.raises(ValueError, match="postérieure"):
        TimeSlot(dt("2027-06-18T16:00:00"), dt("2027-06-18T16:00:00"))


def test_festival_reschedules_concert_when_invariants_hold() -> None:
    festival = make_festival()
    new_slot = TimeSlot(dt("2027-06-18T17:00:00"), dt("2027-06-18T18:00:00"))

    result = festival.reschedule_concert(100, new_slot)

    assert result.time_slot == new_slot


def test_festival_rejects_same_stage_conflict() -> None:
    festival = make_festival(concerts=[
        Concert(100, 200, 10, TimeSlot(dt("2027-06-18T15:00:00"), dt("2027-06-18T16:00:00"))),
        Concert(101, 201, 10, TimeSlot(dt("2027-06-18T16:00:00"), dt("2027-06-18T17:00:00"))),
    ])

    with pytest.raises(DomainError, match="scène est déjà occupée"):
        festival.reschedule_concert(
            100,
            TimeSlot(dt("2027-06-18T15:30:00"), dt("2027-06-18T16:30:00")),
        )


def test_festival_rejects_artist_conflict_on_another_stage() -> None:
    festival = make_festival(
        stages=[Stage(10, 1), Stage(11, 1)],
        concerts=[
            Concert(100, 200, 10, TimeSlot(dt("2027-06-18T15:00:00"), dt("2027-06-18T16:00:00"))),
            Concert(101, 200, 11, TimeSlot(dt("2027-06-18T16:00:00"), dt("2027-06-18T17:00:00"))),
        ],
    )

    with pytest.raises(DomainError, match="artiste est déjà programmé"):
        festival.reschedule_concert(
            100,
            TimeSlot(dt("2027-06-18T15:30:00"), dt("2027-06-18T16:30:00")),
        )


def test_festival_rejects_slot_outside_its_period() -> None:
    festival = make_festival()

    with pytest.raises(DomainError, match="pendant le festival"):
        festival.reschedule_concert(
            100,
            TimeSlot(dt("2027-06-17T15:00:00"), dt("2027-06-17T16:00:00")),
        )


def test_festival_rejects_stage_from_another_festival() -> None:
    festival = make_festival(stages=[Stage(10, festival_id=2)])

    with pytest.raises(DomainError, match="n'appartient pas"):
        festival.reschedule_concert(
            100,
            TimeSlot(dt("2027-06-18T17:00:00"), dt("2027-06-18T18:00:00")),
        )


def test_festival_rejects_missing_equipment() -> None:
    festival = make_festival(
        stages=[Stage(10, 1, EquipmentSet(frozenset({"lighting"})))],
        concerts=[
            Concert(
                100,
                200,
                10,
                TimeSlot(dt("2027-06-18T15:00:00"), dt("2027-06-18T16:00:00")),
                required_equipment=EquipmentSet(frozenset({"rigging"})),
            )
        ],
    )

    with pytest.raises(DomainError, match="équipements requis"):
        festival.reschedule_concert(
            100,
            TimeSlot(dt("2027-06-18T17:00:00"), dt("2027-06-18T18:00:00")),
        )


def test_festival_rejects_rescheduling_cancelled_concert() -> None:
    festival = make_festival(concerts=[
        Concert(
            100,
            200,
            10,
            TimeSlot(dt("2027-06-18T15:00:00"), dt("2027-06-18T16:00:00")),
            status=ConcertStatus.CANCELLED,
        )
    ])

    with pytest.raises(DomainError, match="annulé"):
        festival.reschedule_concert(
            100,
            TimeSlot(dt("2027-06-18T17:00:00"), dt("2027-06-18T18:00:00")),
        )


def test_festival_schedules_concert_and_records_event() -> None:
    festival = make_festival(concerts=[])
    slot = TimeSlot(dt("2027-06-18T15:00:00"), dt("2027-06-18T16:00:00"))

    concert = festival.schedule_concert(100, 200, 10, slot, EquipmentSet())

    assert festival.concerts == [concert]
    assert concert.time_slot == slot
    event, = festival.pull_domain_events()
    assert event.festival_id == festival.id
    assert event.concert_id == concert.id
    assert event.artist_id == concert.artist_id
    assert event.stage_id == concert.stage_id
    assert event.time_slot == slot


def test_festival_rejects_duplicate_concert_id() -> None:
    festival = make_festival()

    with pytest.raises(DomainError, match="existe déjà"):
        festival.schedule_concert(
            100, 201, 10,
            TimeSlot(dt("2027-06-18T17:00:00"), dt("2027-06-18T18:00:00")),
            EquipmentSet(),
        )


def test_festival_rejects_scheduled_concert_outside_period() -> None:
    festival = make_festival(concerts=[])

    with pytest.raises(DomainError, match="pendant le festival"):
        festival.schedule_concert(
            100, 200, 10,
            TimeSlot(dt("2027-06-17T15:00:00"), dt("2027-06-17T16:00:00")),
            EquipmentSet(),
        )


def test_festival_rejects_scheduling_on_another_festivals_stage() -> None:
    festival = make_festival(stages=[Stage(10, festival_id=2)], concerts=[])

    with pytest.raises(DomainError, match="n'appartient pas"):
        festival.schedule_concert(
            100, 200, 10,
            TimeSlot(dt("2027-06-18T15:00:00"), dt("2027-06-18T16:00:00")),
            EquipmentSet(),
        )


def test_festival_rejects_scheduling_without_required_equipment() -> None:
    festival = make_festival(
        stages=[Stage(10, 1, EquipmentSet(frozenset({"lighting"})))],
        concerts=[],
    )

    with pytest.raises(DomainError, match="équipements requis"):
        festival.schedule_concert(
            100, 200, 10,
            TimeSlot(dt("2027-06-18T15:00:00"), dt("2027-06-18T16:00:00")),
            EquipmentSet(frozenset({"rigging"})),
        )


def test_festival_rejects_stage_conflict_when_scheduling() -> None:
    festival = make_festival()

    with pytest.raises(DomainError, match="scène est déjà occupée"):
        festival.schedule_concert(
            101, 201, 10,
            TimeSlot(dt("2027-06-18T15:30:00"), dt("2027-06-18T16:30:00")),
            EquipmentSet(),
        )


def test_festival_rejects_artist_conflict_when_scheduling() -> None:
    festival = make_festival(stages=[Stage(10, 1), Stage(11, 1)])

    with pytest.raises(DomainError, match="artiste est déjà programmé"):
        festival.schedule_concert(
            101, 200, 11,
            TimeSlot(dt("2027-06-18T15:30:00"), dt("2027-06-18T16:30:00")),
            EquipmentSet(),
        )


def test_festival_ignores_cancelled_concerts_when_scheduling() -> None:
    cancelled = Concert(
        101, 201, 10,
        TimeSlot(dt("2027-06-18T15:00:00"), dt("2027-06-18T16:00:00")),
        status=ConcertStatus.CANCELLED,
    )
    festival = make_festival(concerts=[cancelled])

    scheduled = festival.schedule_concert(
        102, 202, 10,
        TimeSlot(dt("2027-06-18T15:30:00"), dt("2027-06-18T16:30:00")),
        EquipmentSet(),
    )

    assert scheduled in festival.concerts


def test_festival_cancels_concert_and_records_event() -> None:
    festival = make_festival()

    cancelled = festival.cancel_concert(100)

    assert cancelled.status is ConcertStatus.CANCELLED
    event, = festival.pull_domain_events()
    assert event.festival_id == festival.id
    assert event.concert_id == cancelled.id


def test_festival_rejects_cancelling_unknown_concert() -> None:
    festival = make_festival()

    with pytest.raises(DomainError, match="introuvable"):
        festival.cancel_concert(999)


def test_festival_rejects_cancelling_already_cancelled_concert() -> None:
    festival = make_festival(concerts=[
        Concert(
            100,
            200,
            10,
            TimeSlot(dt("2027-06-18T15:00:00"), dt("2027-06-18T16:00:00")),
            status=ConcertStatus.CANCELLED,
        )
    ])

    with pytest.raises(DomainError, match="déjà annulé"):
        festival.cancel_concert(100)


def test_festival_publishes_and_records_event() -> None:
    festival = make_festival()

    festival.publish()

    assert festival.status.value == "published"
    event, = festival.pull_domain_events()
    assert event.festival_id == festival.id


def test_festival_rejects_double_publication() -> None:
    festival = make_festival()
    festival.publish()

    with pytest.raises(DomainError, match="déjà publié"):
        festival.publish()


def test_festival_rejects_publication_without_active_concerts() -> None:
    festival = make_festival(concerts=[])

    with pytest.raises(DomainError, match="concert"):
        festival.publish()
