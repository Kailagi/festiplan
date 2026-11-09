from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import (
    get_create_incident_handler,
    get_list_incidents_handler,
)
from app.application.commands import CreateIncidentCommand, ListIncidentsQuery
from app.application.exceptions import ConcertNotFound
from app.application.use_cases.manage_incidents import (
    CreateIncidentHandler,
    ListIncidentsHandler,
)
from app.domain.entities import Incident
from app.schemas import IncidentCreate, IncidentRead

router = APIRouter(prefix="/incidents", tags=["incidents"])

def _incident_response(incident: Incident) -> dict[str, object]:
    return {
        "id": incident.id,
        "concert_id": incident.concert_id,
        "description": incident.description,
        "occurred_at": incident.occurred_at,
        "resolved": incident.resolved,
    }


@router.post("", response_model=IncidentRead, status_code=201)
def create_incident(
    payload: IncidentCreate,
    handler: CreateIncidentHandler = Depends(get_create_incident_handler),
):
    try:
        incident = handler.execute(
            CreateIncidentCommand(
                concert_id=payload.concert_id,
                description=payload.description,
                occurred_at=payload.occurred_at,
            )
        )
    except ConcertNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _incident_response(incident)


@router.get("", response_model=list[IncidentRead])
def list_incidents(
    concert_id: int | None = None,
    handler: ListIncidentsHandler = Depends(get_list_incidents_handler),
):
    incidents = handler.execute(ListIncidentsQuery(concert_id=concert_id))
    return [_incident_response(incident) for incident in incidents]
