import pytest
import threading
from src.network.gossip import GossipManager
import requests

@pytest.fixture
def test_gossip():
    peers = ["http://peer1:5000/gossip", "http://peer2:5000/gossip"]
    gossip = GossipManager(peers=peers, interval=1)
    yield gossip

def test_add_update():
    peers = ["http://peer1:5000/gossip", "http://peer2:5000/gossip"]
    gossip = GossipManager(peers=peers, interval=1)
    gossip.add_update({"key": "test", "value": "123"})
    assert gossip.future_updates == [{"key": "test", "value": "123"}], "add_update failed"

def test_concurrent_add_update():
    peers = ["http://peer1:5000/gossip", "http://peer2:5000/gossip"]
    gossip = GossipManager(peers=peers, interval=1)

    def add_updates():
        for _ in range(25):
            gossip.add_update({"key": "test", "value": "123"})

    thread1 = threading.Thread(target=add_updates)
    thread2 = threading.Thread(target=add_updates)

    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    assert len(gossip.future_updates) == 50, "concurrent add_update failed"

def test_clean_buffer(test_gossip):
    test_gossip.future_updates = [{"key": "test", "value": "123"}]
    test_gossip._clean_buffer()
    assert test_gossip.future_updates == [], "_clean_buffer failed"