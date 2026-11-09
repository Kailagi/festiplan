def test_publish_unknown_festival_returns_404(client):
 assert client.post("/festivals/999/publish").status_code==404


def test_publish_festival_persists_status_and_outbox_event(client, monkeypatch):
 from app.adapters.outbound.sqlalchemy.outbox_dispatcher import SqlAlchemyOutboxDispatcher
 from app.database import SessionLocal
 from app.models import OutboxEvent

 festival=client.post("/festivals",json={
     "name":"Publish Test",
     "location":"Clisson",
     "start_date":"2027-06-18T10:00:00",
     "end_date":"2027-06-20T23:59:00",
 })
 festival_id=festival.json()["id"]
 artist=client.post("/artists",json={
     "name":"Publish Band",
     "genre":"Metal",
     "required_equipment":[],
 })
 stage=client.post("/stages",json={
     "festival_id":festival_id,
     "name":"Mainstage",
     "capacity":1000,
     "available_equipment":[],
 })
 concert=client.post("/concerts",json={
     "festival_id":festival_id,
     "artist_id":artist.json()["id"],
     "stage_id":stage.json()["id"],
     "start_time":"2027-06-18T15:00:00",
     "end_time":"2027-06-18T16:00:00",
 })
 assert concert.status_code==201

 response=client.post(f"/festivals/{festival_id}/publish")

 assert response.status_code==200
 assert response.json()["status"]=="published"
 db=SessionLocal()
 try:
  event=db.query(OutboxEvent).filter(
      OutboxEvent.event_type=="FestivalPublished"
  ).one()
  assert event.event_type=="FestivalPublished"
  assert event.payload=={"festival_id":festival_id}
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
  assert sent[1][2]==f"Le festival {festival_id} a été publié."
 finally:
  db.close()

 repeated=client.post(f"/festivals/{festival_id}/publish")
 assert repeated.status_code==400
