import pytest
from fastapi.testclient import TestClient
from src.network.api_server import app
from types import SimpleNamespace

class ProxyStore:
    def __init__(self):
        self.data = {}
        self.vc = {}

    async def get(self, key):
        return self.data.get(key)

    async def set(self, key, value, vc):
        self.data[key] = value
        self.vc[key] = vc

    async def getVectorClock(self, key):
        return self.vc.get(key)

    async def delete(self, key):
        if key in self.data:
            del self.data[key]

    async def keys(self):
        return self.data.keys()

class ProxyGossip:
    async def add_update(self, update): pass

@pytest.fixture
def client():
    app.state.store = ProxyStore()
    app.state.gossip_manager = ProxyGossip()

    return TestClient(app)

def test_set_get_delete(client):
    headers = {"X-API-KEY": "abcd1234-admin-2099-12-31"}

    res = client.post('/set/foo', headers=headers, json={"value": "bar"})
    assert res.status_code == 200
    assert res.json() == {"key": "foo", "value": "bar"}

    res = client.get('/get/foo', headers=headers)
    assert res.status_code == 200
    assert res.json() == {"key": "foo", "value": "bar"}

    res = client.delete('/delete/foo', headers=headers)
    assert res.status_code == 200
    assert res.json() == {"key": "foo"}

def test_get_non_existent_key(client):
    headers = {"X-API-KEY": "abcd1234-admin-2099-12-31"}
    res = client.get('/get/non_existent_key', headers=headers)
    assert res.status_code == 404
    assert res.json() == {"detail": "Key not found"}