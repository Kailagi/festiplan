import pytest

from app.database import SessionLocal
from app.adapters.outbound.sqlalchemy.outbox_dispatcher import SqlAlchemyOutboxDispatcher
from app.models import Concert, OutboxEvent


def test_concert_end_must_be_after_start(client):
 r=client.post("/concerts",json={
                                    "festival_id":1,
                                    "artist_id":1,
                                    "stage_id":1,
                                    "start_time":"2027-06-18T15:00:00",
                                    "end_time":"2027-06-18T14:00:00"
                                })
 assert r.status_code in (400,422)

def test_reschedule_rejects_stage_conflict(client):
 festival=client.post("/festivals",json={
     "name":"Test Festival",
     "location":"Clisson",
     "start_date":"2027-06-18T10:00:00",
     "end_date":"2027-06-20T23:59:00"
 })
 assert festival.status_code==201
 festival_id=festival.json()["id"]

 artists=[]
 for name in ("First Band","Second Band"):
  response=client.post("/artists",json={
      "name":name,
      "genre":"Metal",
      "required_equipment":[]
  })
  assert response.status_code==201
  artists.append(response.json()["id"])

 stage=client.post("/stages",json={
     "festival_id":festival_id,
     "name":"Mainstage",
     "capacity":1000,
     "available_equipment":[]
 })
 assert stage.status_code==201
 stage_id=stage.json()["id"]

 concerts=[]
 for artist_id,start_time,end_time in (
     (artists[0],"2027-06-18T15:00:00","2027-06-18T16:00:00"),
     (artists[1],"2027-06-18T16:00:00","2027-06-18T17:00:00"),
 ):
  response=client.post("/concerts",json={
      "festival_id":festival_id,
      "artist_id":artist_id,
      "stage_id":stage_id,
      "start_time":start_time,
      "end_time":end_time
  })
  assert response.status_code==201
  concerts.append(response.json()["id"])

 response=client.patch(f"/concerts/{concerts[0]}/reschedule",json={
     "start_time":"2027-06-18T15:30:00",
     "end_time":"2027-06-18T16:30:00"
 })

 assert response.status_code==400
 db=SessionLocal()
 try:
  stored_concert=db.query(Concert).filter(Concert.id==concerts[0]).first()
  assert stored_concert.start_time.isoformat()=="2027-06-18T15:00:00"
  assert db.query(OutboxEvent).count()==2
 finally:
  db.close()


def test_outbox_dispatch_failure_keeps_event_pending(client, monkeypatch):
 def fail_send(recipient, subject, body):
  raise RuntimeError("email unavailable")

 db=SessionLocal()
 db.add(OutboxEvent(
     event_type="ConcertRescheduled",
     payload={"concert_id":1,"new_start":"2027-06-18T17:00:00"},
 ))
 db.commit()
 monkeypatch.setattr(
     "app.adapters.outbound.sqlalchemy.outbox_dispatcher.send_email",
     fail_send,
 )

 try:
  with pytest.raises(RuntimeError,match="email unavailable"):
   SqlAlchemyOutboxDispatcher(db).dispatch_pending()
  event=db.query(OutboxEvent).filter(
      OutboxEvent.event_type=="ConcertRescheduled"
  ).one()
  assert event.processed_at is None
  assert event.attempts==1
  assert event.last_error=="email unavailable"
 finally:
  db.close()


def test_put_reschedule_persists_concert_and_outbox_event(client, monkeypatch):
 festival=client.post("/festivals",json={
     "name":"Test Festival",
     "location":"Clisson",
     "start_date":"2027-06-18T10:00:00",
     "end_date":"2027-06-20T23:59:00"
 })
 festival_id=festival.json()["id"]
 artist=client.post("/artists",json={
     "name":"First Band",
     "genre":"Metal",
     "required_equipment":[]
 })
 stage=client.post("/stages",json={
     "festival_id":festival_id,
     "name":"Mainstage",
     "capacity":1000,
     "available_equipment":[]
 })
 concert=client.post("/concerts",json={
     "festival_id":festival_id,
     "artist_id":artist.json()["id"],
     "stage_id":stage.json()["id"],
     "start_time":"2027-06-18T15:00:00",
     "end_time":"2027-06-18T16:00:00"
 })

 response=client.put(
     f"/festivals/{festival_id}/concerts/{concert.json()['id']}/reschedule",
     json={
         "start_time":"2027-06-18T17:00:00",
         "end_time":"2027-06-18T18:00:00"
     },
 )

 assert response.status_code==200
 assert response.json()["start_time"]=="2027-06-18T17:00:00"
 db=SessionLocal()
 try:
  event=db.query(OutboxEvent).filter(
      OutboxEvent.event_type=="ConcertRescheduled"
  ).one()
  assert event.event_type=="ConcertRescheduled"
  assert event.payload["concert_id"]==concert.json()["id"]
  stored_concert=db.query(Concert).filter(Concert.id==concert.json()["id"]).one()
  assert stored_concert.start_time.isoformat()=="2027-06-18T17:00:00"
 finally:
  db.close()

 sent=[]
 monkeypatch.setattr(
     "app.adapters.outbound.sqlalchemy.outbox_dispatcher.send_email",
     lambda recipient, subject, body: sent.append((recipient,subject,body)),
 )
 db=SessionLocal()
 try:
  dispatched=SqlAlchemyOutboxDispatcher(db).dispatch_pending()
  event=db.query(OutboxEvent).filter(
      OutboxEvent.event_type=="ConcertRescheduled"
  ).one()
  assert dispatched==2
  assert event.processed_at is not None
  assert event.attempts==1
  assert sent[1][2]=="Concert déplacé au 2027-06-18T17:00:00"
 finally:
  db.close()


def test_schedule_concert_through_festival_endpoint(client, monkeypatch):
 festival=client.post("/festivals",json={
     "name":"Test Festival",
     "location":"Clisson",
     "start_date":"2027-06-18T10:00:00",
     "end_date":"2027-06-20T23:59:00"
 })
 festival_id=festival.json()["id"]
 artist=client.post("/artists",json={
     "name":"Scheduled Band",
     "genre":"Metal",
     "required_equipment":["rigging"]
 })
 stage=client.post("/stages",json={
     "festival_id":festival_id,
     "name":"Mainstage",
     "capacity":1000,
     "available_equipment":["rigging"]
 })

 response=client.post(f"/festivals/{festival_id}/concerts",json={
     "artist_id":artist.json()["id"],
     "stage_id":stage.json()["id"],
     "start_time":"2027-06-18T15:00:00",
     "end_time":"2027-06-18T16:00:00"
 })

 assert response.status_code==201
 assert response.json()["festival_id"]==festival_id
 assert response.json()["artist_id"]==artist.json()["id"]
 assert response.json()["stage_id"]==stage.json()["id"]

 second_artist=client.post("/artists",json={
     "name":"Second Scheduled Band",
     "genre":"Metal",
     "required_equipment":["rigging"]
 })
 second_response=client.post(f"/festivals/{festival_id}/concerts",json={
     "artist_id":second_artist.json()["id"],
     "stage_id":stage.json()["id"],
     "start_time":"2027-06-18T16:00:00",
     "end_time":"2027-06-18T17:00:00"
 })
 assert second_response.status_code==201
 assert second_response.json()["id"] != response.json()["id"]

 db=SessionLocal()
 try:
  events=db.query(OutboxEvent).order_by(OutboxEvent.id).all()
  assert [event.event_type for event in events]==[
      "ConcertScheduled",
      "ConcertScheduled",
  ]
  assert [event.payload["concert_id"] for event in events]==[
      response.json()["id"],
      second_response.json()["id"],
  ]
  assert all(event.payload["festival_id"]==festival_id for event in events)
 finally:
  db.close()

 sent=[]
 monkeypatch.setattr(
     "app.adapters.outbound.sqlalchemy.outbox_dispatcher.send_email",
     lambda recipient, subject, body: sent.append((recipient,subject,body)),
 )
 db=SessionLocal()
 try:
  assert SqlAlchemyOutboxDispatcher(db).dispatch_pending()==2
  assert sent[0][2]=="Concert programmé au 2027-06-18T15:00:00"
  assert sent[1][2]=="Concert programmé au 2027-06-18T16:00:00"
 finally:
  db.close()


def test_schedule_concert_rejects_stage_conflict(client):
 festival=client.post("/festivals",json={
     "name":"Test Festival",
     "location":"Clisson",
     "start_date":"2027-06-18T10:00:00",
     "end_date":"2027-06-20T23:59:00"
 })
 festival_id=festival.json()["id"]
 artists=[]
 for name in ("First Band","Second Band"):
  artists.append(client.post("/artists",json={
      "name":name,
      "genre":"Metal",
      "required_equipment":[]
  }).json()["id"])
 stage=client.post("/stages",json={
     "festival_id":festival_id,
     "name":"Mainstage",
     "capacity":1000,
     "available_equipment":[]
 })
 first=client.post(f"/festivals/{festival_id}/concerts",json={
     "artist_id":artists[0],
     "stage_id":stage.json()["id"],
     "start_time":"2027-06-18T15:00:00",
     "end_time":"2027-06-18T16:00:00"
 })
 assert first.status_code==201

 response=client.post(f"/festivals/{festival_id}/concerts",json={
     "artist_id":artists[1],
     "stage_id":stage.json()["id"],
     "start_time":"2027-06-18T15:30:00",
     "end_time":"2027-06-18T16:30:00"
 })

 assert response.status_code==400
 db=SessionLocal()
 try:
  assert db.query(Concert).count()==1
  assert db.query(OutboxEvent).count()==1
 finally:
  db.close()


def test_cancel_concert_through_festival_endpoint(client, monkeypatch):
 festival=client.post("/festivals",json={
     "name":"Test Festival",
     "location":"Clisson",
     "start_date":"2027-06-18T10:00:00",
     "end_date":"2027-06-20T23:59:00"
 })
 festival_id=festival.json()["id"]
 artist=client.post("/artists",json={
     "name":"Cancellation Band",
     "genre":"Metal",
     "required_equipment":[]
 })
 stage=client.post("/stages",json={
     "festival_id":festival_id,
     "name":"Mainstage",
     "capacity":1000,
     "available_equipment":[]
 })
 concert=client.post("/concerts",json={
     "festival_id":festival_id,
     "artist_id":artist.json()["id"],
     "stage_id":stage.json()["id"],
     "start_time":"2027-06-18T15:00:00",
     "end_time":"2027-06-18T16:00:00"
 })

 response=client.post(f"/festivals/{festival_id}/concerts/{concert.json()['id']}/cancel")

 assert response.status_code==200
 assert response.json()["status"]=="cancelled"
 db=SessionLocal()
 try:
  stored_concert=db.query(Concert).one()
  event=db.query(OutboxEvent).filter(
      OutboxEvent.event_type=="ConcertCancelled"
  ).one()
  assert stored_concert.status=="cancelled"
  assert event.event_type=="ConcertCancelled"
  assert event.payload=={
      "festival_id":festival_id,
      "concert_id":concert.json()["id"],
  }
 finally:
  db.close()

 sent=[]
 monkeypatch.setattr(
     "app.adapters.outbound.sqlalchemy.outbox_dispatcher.send_email",
     lambda recipient, subject, body: sent.append((recipient,subject,body)),
 )
 db=SessionLocal()
 try:
  assert SqlAlchemyOutboxDispatcher(db).dispatch_pending()==2
  assert sent[1][2]=="Le concert #1 a été annulé."
 finally:
  db.close()

 repeated=client.post(f"/festivals/{festival_id}/concerts/{concert.json()['id']}/cancel")
 assert repeated.status_code==400
 db=SessionLocal()
 try:
  assert db.query(OutboxEvent).count()==2
 finally:
  db.close()


def test_cancel_unknown_concert_returns_not_found(client):
 festival=client.post("/festivals",json={
     "name":"Test Festival",
     "location":"Clisson",
     "start_date":"2027-06-18T10:00:00",
     "end_date":"2027-06-20T23:59:00"
 })

 response=client.post(f"/festivals/{festival.json()['id']}/concerts/999/cancel")

 assert response.status_code==404


def test_legacy_concert_routes_use_application_handlers(client):
 festival=client.post("/festivals",json={
     "name":"Legacy Route Festival",
     "location":"Clisson",
     "start_date":"2027-06-18T10:00:00",
     "end_date":"2027-06-20T23:59:00",
 })
 artist=client.post("/artists",json={
     "name":"Legacy Route Band",
     "genre":"Metal",
     "required_equipment":[],
 })
 stage=client.post("/stages",json={
     "festival_id":festival.json()["id"],
     "name":"Mainstage",
     "capacity":1000,
     "available_equipment":[],
 })

 concert=client.post("/concerts",json={
     "festival_id":festival.json()["id"],
     "artist_id":artist.json()["id"],
     "stage_id":stage.json()["id"],
     "start_time":"2027-06-18T15:00:00",
     "end_time":"2027-06-18T16:00:00",
 })

 assert concert.status_code==201
 assert client.get(f"/concerts/{concert.json()['id']}").status_code==200
 assert client.get("/concerts",params={"festival_id":festival.json()["id"]}).status_code==200
 assert client.get(f"/concerts/schedule/{festival.json()['id']}").status_code==200
 db=SessionLocal()
 try:
  event=db.query(OutboxEvent).one()
  assert event.event_type=="ConcertScheduled"
 finally:
  db.close()

 cancelled=client.post(f"/concerts/{concert.json()['id']}/cancel")
 assert cancelled.status_code==200
 assert cancelled.json()["status"]=="cancelled"
 assert client.get(
     "/concerts",
     params={"festival_id":festival.json()["id"]},
 ).json()==[]
 assert client.get(
     f"/concerts/schedule/{festival.json()['id']}"
 ).json()==[]
