def test_artist_name_must_be_a_string(client):
 r=client.post("/artists",json={
                                    "name":123,
                                    "genre":"Metal",
                                    "required_equipment":[]
                                })
 assert r.status_code==422


def test_create_and_list_artists(client):
 created=client.post("/artists",json={
     "name":"Test Artist",
     "genre":"Metal",
     "required_equipment":["rigging","lighting"],
 })

 assert created.status_code==201
 assert created.json()["name"]=="Test Artist"
 assert created.json()["required_equipment"]==["lighting","rigging"]

 listed=client.get("/artists")
 assert listed.status_code==200
 assert listed.json()==[created.json()]
