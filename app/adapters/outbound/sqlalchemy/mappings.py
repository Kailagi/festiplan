from app.domain.entities import Artist, Concert, ConcertStatus, Festival, FestivalStatus, Stage
from app.domain.value_objects import EquipmentSet, FestivalPeriod, TimeSlot
from app.models import Concert as ConcertModel
from app.models import Festival as FestivalModel
from app.models import Artist as ArtistModel
from app.models import Stage as StageModel


def _equipment_set(value: str) -> EquipmentSet:
    return EquipmentSet(frozenset(item.strip() for item in value.split(",") if item.strip()))


def to_domain_festival(model: FestivalModel) -> Festival:
    stages = [
        Stage(
            id=stage.id,
            festival_id=stage.festival_id,
            available_equipment=_equipment_set(stage.available_equipment),
            name=stage.name,
            capacity=stage.capacity,
        )
        for stage in model.stages
    ]
    concerts = [
        Concert(
            id=concert.id,
            artist_id=concert.artist_id,
            stage_id=concert.stage_id,
            time_slot=TimeSlot(concert.start_time, concert.end_time),
            required_equipment=_equipment_set(concert.artist.required_equipment),
            status=ConcertStatus(concert.status),
        )
        for concert in model.concerts
    ]
    return Festival(
        id=model.id,
        period=FestivalPeriod(model.start_date, model.end_date),
        stages=stages,
        concerts=concerts,
        name=model.name,
        location=model.location,
        status=FestivalStatus(model.status),
    )


def to_domain_artist(model: ArtistModel) -> Artist:
    return Artist(
        id=model.id,
        name=model.name,
        genre=model.genre,
        required_equipment=_equipment_set(model.required_equipment),
    )


def to_domain_stage(model: StageModel) -> Stage:
    return Stage(
        id=model.id,
        festival_id=model.festival_id,
        available_equipment=_equipment_set(model.available_equipment),
        name=model.name,
        capacity=model.capacity,
    )


def apply_domain_festival(
    festival: Festival,
    model: FestivalModel,
) -> list[tuple[Concert, ConcertModel]]:
    model.status = festival.status.value
    persistence_concerts: dict[int, ConcertModel] = {
        concert.id: concert
        for concert in model.concerts
        if concert.id is not None
    }
    new_concerts: list[tuple[Concert, ConcertModel]] = []
    for concert in festival.concerts:
        persistence_concert = (
            persistence_concerts.get(concert.id)
            if concert.id is not None
            else None
        )
        if persistence_concert is None:
            persistence_concert = ConcertModel(
                festival_id=festival.id,
                artist_id=concert.artist_id,
                stage_id=concert.stage_id,
                start_time=concert.time_slot.start,
                end_time=concert.time_slot.end,
                status=concert.status.value,
            )
            model.concerts.append(persistence_concert)
            new_concerts.append((concert, persistence_concert))
            continue
        persistence_concert.start_time = concert.time_slot.start
        persistence_concert.end_time = concert.time_slot.end
        persistence_concert.status = concert.status.value
    return new_concerts
