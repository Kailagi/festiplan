from dataclasses import dataclass

from app.domain.value_objects import TimeSlot


@dataclass(frozen=True, slots=True)
class ConcertRescheduled:
    festival_id: int
    concert_id: int
    previous_time_slot: TimeSlot
    new_time_slot: TimeSlot


@dataclass(frozen=True, slots=True)
class ConcertScheduled:
    festival_id: int
    concert_id: int
    stage_id: int
    artist_id: int
    time_slot: TimeSlot


@dataclass(frozen=True, slots=True)
class ConcertCancelled:
    festival_id: int
    concert_id: int


@dataclass(frozen=True, slots=True)
class FestivalPublished:
    festival_id: int


DomainEvent = ConcertRescheduled | ConcertScheduled | ConcertCancelled | FestivalPublished
