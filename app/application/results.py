from dataclasses import dataclass

from app.domain.entities import Concert, Festival


@dataclass(frozen=True, slots=True)
class RescheduleConcertResult:
    festival_id: int
    concert: Concert


@dataclass(frozen=True, slots=True)
class ScheduleConcertResult:
    festival_id: int
    concert: Concert


@dataclass(frozen=True, slots=True)
class CancelConcertResult:
    festival_id: int
    concert: Concert


@dataclass(frozen=True, slots=True)
class PublishFestivalResult:
    festival: Festival
