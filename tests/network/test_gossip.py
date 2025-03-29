import pytest
from src.network.gossip import GossipManager
import pytest_asyncio
import asyncio

@pytest_asyncio.fixture
async def test_gossip():
    peers = ["http://peer1:5000/gossip", "http://peer2:5000/gossip"]
    gossip = GossipManager(peers=peers, interval=1)
    await gossip.start()
    yield gossip
    await gossip.stop()

@pytest.mark.asyncio
async def test_add_update():
    peers = ["http://peer1:5000/gossip", "http://peer2:5000/gossip"]
    gossip = GossipManager(peers=peers, interval=1)
    await gossip.add_update({"key": "test", "value": "123"})
    assert gossip.future_updates == [{"key": "test", "value": "123"}], "add_update failed"

@pytest.mark.asyncio
async def test_concurrent_add_update():
    peers = ["http://peer1:5000/gossip", "http://peer2:5000/gossip"]
    gossip = GossipManager(peers=peers, interval=1)

    async def add_updates():
        for _ in range(25):
            await gossip.add_update({"key": "test", "value": "123"})

    await asyncio.gather(add_updates(), add_updates())

    assert len(gossip.future_updates) == 50, "concurrent add_update failed"

@pytest.mark.asyncio
async def test_clean_buffer(test_gossip):
    test_gossip.future_updates = [{"key": "test", "value": "123"}]
    await test_gossip._clean_buffer()
    assert test_gossip.future_updates == [], "_clean_buffer failed"