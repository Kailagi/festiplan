class ApplicationError(Exception):
    """Base class for application-level failures."""


class FestivalNotFound(ApplicationError):
    def __init__(self, festival_id: int | None) -> None:
        message = f"Festival introuvable : {festival_id}" if festival_id is not None else "Festival du concert introuvable"
        super().__init__(message)
        self.festival_id = festival_id


class ConcertRescheduleRejected(ApplicationError):
    """A domain invariant prevented a concert from being rescheduled."""


class ConcertScheduleRejected(ApplicationError):
    """A domain invariant prevented a concert from being scheduled."""


class ArtistNotFound(ApplicationError):
    def __init__(self, artist_id: int) -> None:
        super().__init__(f"Artiste introuvable : {artist_id}")
        self.artist_id = artist_id


class ConcertNotFound(ApplicationError):
    def __init__(self, concert_id: int) -> None:
        super().__init__(f"Concert introuvable : {concert_id}")
        self.concert_id = concert_id


class ConcertCancelRejected(ApplicationError):
    """A domain invariant prevented a concert from being cancelled."""


class FestivalPublishRejected(ApplicationError):
    """A domain invariant prevented a festival from being published."""
