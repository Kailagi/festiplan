from dataclasses import dataclass
from datetime import datetime


def _is_aware(value: datetime) -> bool:
    return value.utcoffset() is not None


def _validate_datetime_range(start: datetime, end: datetime) -> None:
    if _is_aware(start) != _is_aware(end):
        raise ValueError("Les dates doivent être toutes deux avec ou sans fuseau horaire")
    if start >= end:
        raise ValueError("La date de fin doit être postérieure à la date de début")


def _validate_compatible_timezones(first: datetime, second: datetime) -> None:
    if _is_aware(first) != _is_aware(second):
        raise ValueError("Les dates doivent être toutes deux avec ou sans fuseau horaire")


@dataclass(frozen=True, slots=True)
class TimeSlot:
    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        _validate_datetime_range(self.start, self.end)

    def overlaps_with(self, other: "TimeSlot") -> bool:
        _validate_compatible_timezones(self.start, other.start)
        return self.start < other.end and other.start < self.end


@dataclass(frozen=True, slots=True)
class FestivalPeriod:
    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        _validate_datetime_range(self.start, self.end)

    def contains(self, slot: TimeSlot) -> bool:
        _validate_compatible_timezones(self.start, slot.start)
        return self.start <= slot.start and slot.end <= self.end


@dataclass(frozen=True, slots=True)
class EquipmentSet:
    items: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        normalized = frozenset(item.strip() for item in self.items if item.strip())
        object.__setattr__(self, "items", normalized)

    def is_subset_of(self, other: "EquipmentSet") -> bool:
        return self.items.issubset(other.items)
