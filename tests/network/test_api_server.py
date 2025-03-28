from fastapi.testclient import TestClient
from src.network.api_server import app 

client = TestClient(app)

def test_receive_gossip():
    response = client.post("/gossip", json={"updates": [{"key": "key1", "value": "example", "timestamp": 0.0}]})
    assert response.status_code == 200
    assert response.json() == {"message": "Gossip received"}

def test_set_key():
    response = client.post("/set/key1", json={"value": "example"})
    assert response.status_code == 200
    assert response.json() == {"key": "key1", "value": "example"}

def test_get_key():
    client.post("/set/key2", json={"value": "test"})
    response = client.get("/get/key2")
    assert response.status_code == 200
    assert response.json() == {"key": "key2", "value": "test"}

def test_get_non_existing_key():
    response = client.get("/get/non_existing_key")
    assert response.status_code == 404
    assert response.json() == {"detail": "Key not found"}

def test_delete_key():
    client.post("/set/key3", json={"value": "delete_test"})
    response = client.delete("/delete/key3")
    assert response.status_code == 200
    assert response.json() == {"key": "key3"}

def test_get_keys():
    client.post("/set/key4", json={"value": "value4"})
    client.post("/set/key5", json={"value": "value5"})
    response = client.get("/keys")
    assert response.status_code == 200
    assert "key4" in response.json()["keys"]
    assert "key5" in response.json()["keys"]
