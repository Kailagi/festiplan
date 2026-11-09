from dataclasses import dataclass

from app.domain.value_objects import TimeSlot


@dataclass(frozen=True, slots=True)
class RescheduleConcertCommand:
    festival_id: int | None
    concert_id: int
    new_time_slot: TimeSlot


@dataclass(frozen=True, slots=True)
class ScheduleConcertCommand:
    festival_id: int
    artist_id: int
    stage_id: int
    time_slot: TimeSlot


@dataclass(frozen=True, slots=True)
class CancelConcertCommand:
    festival_id: int | None
    concert_id: int


@dataclass(frozen=True, slots=True)
class PublishFestivalCommand:
    festival_id: int
