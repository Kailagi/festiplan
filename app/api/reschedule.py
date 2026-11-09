from fastapi import HTTPException

from app.application.commands import RescheduleConcertCommand
from app.application.exceptions import ConcertRescheduleRejected, FestivalNotFound
from app.application.use_cases.reschedule_concert import RescheduleConcertHandler
from app.domain.value_objects import TimeSlot
from app.schemas import ConcertReschedule


def reschedule_concert_response(
    handler: RescheduleConcertHandler,
    festival_id: int | None,
    concert_id: int,
    payload: ConcertReschedule,
) -> dict[str, object]:
    try:
        result = handler.execute(
            RescheduleConcertCommand(
                festival_id=festival_id,
                concert_id=concert_id,
                new_time_slot=TimeSlot(payload.start_time, payload.end_time),
            )
        )
    except FestivalNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ConcertRescheduleRejected as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
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
