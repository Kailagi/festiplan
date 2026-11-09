from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from app.domain.errors import ConcertNotFound, DomainError
from app.domain.events import (
    ConcertCancelled,
    ConcertRescheduled,
    ConcertScheduled,
    DomainEvent,
    FestivalPublished,
)
from app.domain.value_objects import EquipmentSet, FestivalPeriod, TimeSlot


class ConcertStatus(str, Enum):
    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"


class FestivalStatus(str, Enum):
    PREPARATION = "preparation"
    PUBLISHED = "published"


@dataclass(eq=False)
class Stage:
    id: int
    festival_id: int
    available_equipment: EquipmentSet = field(default_factory=EquipmentSet)
    name: str = ""
    capacity: int = 1


@dataclass(eq=False)
class Artist:
    id: int
    name: str
    genre: str
    required_equipment: EquipmentSet = field(default_factory=EquipmentSet)


@dataclass(frozen=True, slots=True)
class Incident:
    id: int
    concert_id: int
    description: str
    occurred_at: datetime
    resolved: bool = False


@dataclass(eq=False)
class Concert:
    id: int | None
    artist_id: int
    stage_id: int
    time_slot: TimeSlot
    required_equipment: EquipmentSet = field(default_factory=EquipmentSet)
    status: ConcertStatus = ConcertStatus.SCHEDULED

    def reschedule(self, new_time_slot: TimeSlot) -> None:
        if self.status is ConcertStatus.CANCELLED:
            raise DomainError("Un concert annulé ne peut pas être déplacé")
        self.time_slot = new_time_slot


@dataclass(eq=False)
class Festival:
    id: int
    period: FestivalPeriod
    stages: list[Stage] = field(default_factory=list)
    concerts: list[Concert] = field(default_factory=list)
    name: str = ""
    location: str = ""
    status: FestivalStatus = FestivalStatus.PREPARATION
    _domain_events: list[DomainEvent] = field(default_factory=list, init=False, repr=False)

    def schedule_concert(
        self,
        concert_id: int | None,
        artist_id: int,
        stage_id: int,
        time_slot: TimeSlot,
        required_equipment: EquipmentSet,
    ) -> Concert:
        if concert_id is not None and any(
            concert.id == concert_id for concert in self.concerts
        ):
            raise DomainError(f"Un concert avec l'identifiant {concert_id} existe déjà")
        if not self.period.contains(time_slot):
            raise DomainError("Le concert doit se dérouler pendant le festival")

        stage = next((item for item in self.stages if item.id == stage_id), None)
        if stage is None or stage.festival_id != self.id:
            raise DomainError("La scène n'appartient pas à ce festival")
        if not required_equipment.is_subset_of(stage.available_equipment):
            raise DomainError("La scène ne dispose pas de tous les équipements requis")

        for other in self.concerts:
            if other.status is ConcertStatus.CANCELLED:
                continue
            if not time_slot.overlaps_with(other.time_slot):
                continue
            if other.stage_id == stage_id:
                raise DomainError("Conflit : la scène est déjà occupée")
            if other.artist_id == artist_id:
                raise DomainError("Conflit : l'artiste est déjà programmé")

        concert = Concert(
            id=concert_id,
            artist_id=artist_id,
            stage_id=stage_id,
            time_slot=time_slot,
            required_equipment=required_equipment,
        )
        self.concerts.append(concert)
        if concert.id is not None:
            self.record_concert_scheduled(concert)
        return concert

    def record_concert_scheduled(self, concert: Concert) -> None:
        if concert not in self.concerts:
            raise DomainError("Le concert ne fait pas partie de ce festival")
        if concert.id is None:
            raise DomainError("Le concert doit avoir un identifiant avant émission")

        self._domain_events.append(
            ConcertScheduled(
                festival_id=self.id,
                concert_id=concert.id,
                stage_id=concert.stage_id,
                artist_id=concert.artist_id,
                time_slot=concert.time_slot,
            )
        )

    def reschedule_concert(self, concert_id: int, new_time_slot: TimeSlot) -> Concert:
        concert = next((item for item in self.concerts if item.id == concert_id), None)
        if concert is None:
            raise DomainError("Concert introuvable dans ce festival")
        if concert.status is ConcertStatus.CANCELLED:
            raise DomainError("Un concert annulé ne peut pas être déplacé")
        if not self.period.contains(new_time_slot):
            raise DomainError("Le concert doit se dérouler pendant le festival")

        stage = next((item for item in self.stages if item.id == concert.stage_id), None)
        if stage is None or stage.festival_id != self.id:
            raise DomainError("La scène du concert n'appartient pas à ce festival")
        if not concert.required_equipment.is_subset_of(stage.available_equipment):
            raise DomainError("La scène ne dispose pas de tous les équipements requis")

        for other in self.concerts:
            if other.id == concert.id or other.status is ConcertStatus.CANCELLED:
                continue
            if not new_time_slot.overlaps_with(other.time_slot):
                continue
            if other.stage_id == concert.stage_id:
                raise DomainError("Conflit : la scène est déjà occupée")
            if other.artist_id == concert.artist_id:
                raise DomainError("Conflit : l'artiste est déjà programmé")

        previous_time_slot = concert.time_slot
        concert.reschedule(new_time_slot)
        self._domain_events.append(
            ConcertRescheduled(
                festival_id=self.id,
                concert_id=concert.id,
                previous_time_slot=previous_time_slot,
                new_time_slot=new_time_slot,
            )
        )
        return concert

    def cancel_concert(self, concert_id: int) -> Concert:
        concert = next((item for item in self.concerts if item.id == concert_id), None)
        if concert is None:
            raise ConcertNotFound(f"Concert {concert_id} introuvable dans ce festival")
        if concert.status is ConcertStatus.CANCELLED:
            raise DomainError("Ce concert est déjà annulé")

        concert.status = ConcertStatus.CANCELLED
        self._domain_events.append(
            ConcertCancelled(festival_id=self.id, concert_id=concert.id)
        )
        return concert

    def publish(self) -> None:
        if self.status is FestivalStatus.PUBLISHED:
            raise DomainError("Le festival est déjà publié")
        if not any(concert.status is not ConcertStatus.CANCELLED for concert in self.concerts):
            raise DomainError("Le festival doit contenir au moins un concert actif pour être publié")

        self.status = FestivalStatus.PUBLISHED
        self._domain_events.append(FestivalPublished(festival_id=self.id))

    def pull_domain_events(self) -> list[DomainEvent]:
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events
