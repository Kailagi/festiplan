from fastapi import APIRouter, Depends

from app.api.dependencies import (
    get_create_artist_handler,
    get_list_artists_handler,
)
from app.application.commands import CreateArtistCommand
from app.application.use_cases.manage_artists import (
    CreateArtistHandler,
    ListArtistsHandler,
)
from app.domain.entities import Artist
from app.domain.value_objects import EquipmentSet
from app.schemas import ArtistCreate, ArtistRead

router = APIRouter(prefix="/artists", tags=["artists"])


def _artist_response(artist: Artist) -> dict[str, object]:
    return {
        "id": artist.id,
        "name": artist.name,
        "genre": artist.genre,
        "required_equipment": sorted(artist.required_equipment.items),
    }


@router.get("", response_model=list[ArtistRead])
def list_artists(
    handler: ListArtistsHandler = Depends(get_list_artists_handler),
):
    return [_artist_response(artist) for artist in handler.execute()]


@router.post("", response_model=ArtistRead, status_code=201)
def create_artist(
    payload: ArtistCreate,
    handler: CreateArtistHandler = Depends(get_create_artist_handler),
):
    artist = handler.execute(
        CreateArtistCommand(
            name=payload.name,
            genre=payload.genre,
            required_equipment=EquipmentSet(frozenset(payload.required_equipment)),
        )
    )
    return _artist_response(artist)
