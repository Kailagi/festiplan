def test_stage_capacity_must_be_positive(client):
 r=client.post("/stages",json={
                                "festival_id":1,
                                "name":"Mainstage",
                                "capacity":0,
                                "available_equipment":[]
                               })
 assert r.status_code==422


def test_create_and_list_stages(client):
 festival=client.post("/festivals",json={
     "name":"Stage Test Festival",
     "location":"Clisson",
     "start_date":"2027-06-18T10:00:00",
     "end_date":"2027-06-20T23:59:00",
 })
 festival_id=festival.json()["id"]

 created=client.post("/stages",json={
     "festival_id":festival_id,
     "name":"Mainstage",
     "capacity":1000,
     "available_equipment":["rigging","lighting"],
 })

 assert created.status_code==201
 assert created.json()["festival_id"]==festival_id
 assert created.json()["available_equipment"]==["lighting","rigging"]

 listed=client.get("/stages",params={"festival_id":festival_id})
 assert listed.status_code==200
 assert listed.json()==[created.json()]


def test_create_stage_for_unknown_festival_returns_404(client):
 response=client.post("/stages",json={
     "festival_id":999,
     "name":"Mainstage",
     "capacity":1000,
     "available_equipment":[],
 })

 assert response.status_code==404
