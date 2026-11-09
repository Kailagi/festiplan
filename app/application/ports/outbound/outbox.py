from typing import Protocol

from app.domain.events import DomainEvent


class Outbox(Protocol):
    def add(self, event: DomainEvent) -> None:
        """Add a domain event to the current transaction's outbox."""
        ...
