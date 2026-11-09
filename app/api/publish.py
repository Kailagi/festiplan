from fastapi import HTTPException

from app.application.commands import PublishFestivalCommand
from app.application.exceptions import FestivalNotFound, FestivalPublishRejected
from app.application.use_cases.publish_festival import PublishFestivalHandler


def publish_festival_response(
    handler: PublishFestivalHandler,
    festival_id: int,
) -> dict[str, object]:
    try:
        result = handler.execute(PublishFestivalCommand(festival_id))
    except FestivalNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except FestivalPublishRejected as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    festival = result.festival
    return {
        "id": festival.id,
        "name": festival.name,
        "location": festival.location,
        "start_date": festival.period.start,
        "end_date": festival.period.end,
        "status": festival.status.value,
    }
