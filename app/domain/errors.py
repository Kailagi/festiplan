class DomainError(Exception):
    """Raised when a domain invariant would be violated."""


class ConcertNotFound(DomainError):
    """Raised when a concert does not belong to the festival aggregate."""
