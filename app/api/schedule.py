from fastapi import HTTPException

from app.application.commands import ScheduleConcertCommand
from app.application.exceptions import ArtistNotFound, ConcertScheduleRejected, FestivalNotFound
from app.application.use_cases.schedule_concert import ScheduleConcertHandler
from app.domain.value_objects import TimeSlot
from app.schemas import FestivalConcertCreate


def schedule_concert_response(
    handler: ScheduleConcertHandler,
    festival_id: int,
    payload: FestivalConcertCreate,
) -> dict[str, object]:
    try:
        result = handler.execute(
            ScheduleConcertCommand(
                festival_id=festival_id,
                artist_id=payload.artist_id,
                stage_id=payload.stage_id,
                time_slot=TimeSlot(payload.start_time, payload.end_time),
            )
        )
    except (FestivalNotFound, ArtistNotFound) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ConcertScheduleRejected as exc:
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
