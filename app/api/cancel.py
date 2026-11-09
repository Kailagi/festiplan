from fastapi import HTTPException

from app.application.commands import CancelConcertCommand
from app.application.exceptions import (
    ConcertCancelRejected,
    ConcertNotFound,
    FestivalNotFound,
)
from app.application.use_cases.cancel_concert import CancelConcertHandler


def cancel_concert_response(
    handler: CancelConcertHandler,
    festival_id: int | None,
    concert_id: int,
) -> dict[str, object]:
    try:
        result = handler.execute(
            CancelConcertCommand(
                festival_id=festival_id,
                concert_id=concert_id,
            )
        )
    except (FestivalNotFound, ConcertNotFound) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ConcertCancelRejected as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    concert = result.concert
    return {
        "id": concert.id,
        "festival_id": result.festival_id,
        "artist_id": concert.artist_id,
        "stage_id": concert.stage_id,
        "start_time": concert.time_slot.start,
        "end_time": concert.time_slot.end,
        "status": concert.status.value,
    }
