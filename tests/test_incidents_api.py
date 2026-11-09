from app.database import SessionLocal
from app.models import Incident


def _create_concert(client):
    festival = client.post(
        "/festivals",
        json={
            "name": "Incident Test Festival",
            "location": "Clisson",
            "start_date": "2027-06-18T10:00:00",
            "end_date": "2027-06-20T23:59:00",
        },
    )
    artist = client.post(
        "/artists",
        json={
            "name": "Incident Test Artist",
            "genre": "Metal",
            "required_equipment": [],
        },
    )
    stage = client.post(
        "/stages",
        json={
            "festival_id": festival.json()["id"],
            "name": "Mainstage",
            "capacity": 1000,
            "available_equipment": [],
        },
    )
    concert = client.post(
        f"/festivals/{festival.json()['id']}/concerts",
        json={
            "artist_id": artist.json()["id"],
            "stage_id": stage.json()["id"],
            "start_time": "2027-06-18T15:00:00",
            "end_time": "2027-06-18T16:00:00",
        },
    )
    return concert.json()["id"]


def test_create_incident_and_filter_by_concert(client):
    concert_id = _create_concert(client)
    response = client.post(
        "/incidents",
        json={
            "concert_id": concert_id,
            "description": "Un problème technique",
            "occurred_at": "2027-06-18T15:30:00",
        },
    )

    assert response.status_code == 201
    assert response.json()["concert_id"] == concert_id
    assert response.json()["description"] == "Un problème technique"
    assert response.json()["occurred_at"] == "2027-06-18T15:30:00"
    assert response.json()["resolved"] is False
    assert client.get("/incidents", params={"concert_id": concert_id}).json() == [
        response.json()
    ]

    db = SessionLocal()
    try:
        stored = db.query(Incident).one()
        assert stored.description == "Un problème technique"
    finally:
        db.close()


def test_create_incident_for_missing_concert_returns_404(client):
    response = client.post(
        "/incidents",
        json={"concert_id": 999, "description": "Concert inexistant"},
    )

    assert response.status_code == 404
    assert client.get("/incidents").json() == []


def test_list_festivals_uses_application_route(client):
    created = client.post(
        "/festivals",
        json={
            "name": "Listed Festival",
            "location": "Clisson",
            "start_date": "2027-06-18T10:00:00",
            "end_date": "2027-06-20T23:59:00",
        },
    )

    response = client.get("/festivals")

    assert response.status_code == 200
    assert response.json() == [created.json()]
