from dataclasses import dataclass
from datetime import datetime

from app.domain.value_objects import EquipmentSet, TimeSlot


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


@dataclass(frozen=True, slots=True)
class CreateFestivalCommand:
    name: str
    location: str
    start_date: datetime
    end_date: datetime


@dataclass(frozen=True, slots=True)
class CreateIncidentCommand:
    concert_id: int
    description: str
    occurred_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class ListIncidentsQuery:
    concert_id: int | None = None


@dataclass(frozen=True, slots=True)
class CreateArtistCommand:
    name: str
    genre: str
    required_equipment: EquipmentSet


@dataclass(frozen=True, slots=True)
class CreateStageCommand:
    festival_id: int
    name: str
    capacity: int
    available_equipment: EquipmentSet


@dataclass(frozen=True, slots=True)
class ListStagesQuery:
    festival_id: int
