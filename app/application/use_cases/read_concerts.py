from app.application.ports.outbound.concert_reader import ConcertReader, ConcertView


class ReadConcertsHandler:
    def __init__(self, reader: ConcertReader) -> None:
        self._reader = reader

    def list_for_festival(self, festival_id: int) -> list[ConcertView]:
        return self._reader.list_for_festival(festival_id)

    def get_by_id(self, concert_id: int) -> ConcertView | None:
        return self._reader.get_by_id(concert_id)
