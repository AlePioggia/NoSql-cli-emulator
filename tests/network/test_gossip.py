import pytest
from src.network.gossip import GossipManager
from src.network.heartbeat import Heartbeat
import pytest_asyncio
import asyncio
from unittest.mock import AsyncMock, patch
import time

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
    await gossip.add_update({"id": "1", "key": "test", "value": "123"})
    assert gossip.future_updates == [{"id": "1", "key": "test", "value": "123"}], "add_update failed"

@pytest.mark.asyncio
async def test_concurrent_add_update():
    peers = ["http://peer1:5000/gossip", "http://peer2:5000/gossip"]
    gossip = GossipManager(peers=peers, interval=1)

    async def add_updates():
        for _ in range(25):
            await gossip.add_update({"id": str(_), "key": "test", "value": "123"})

    await asyncio.gather(add_updates(), add_updates())

    assert len(gossip.future_updates) == 50, "concurrent add_update failed"

@pytest.mark.asyncio
async def test_clean_buffer(test_gossip):
    test_gossip.future_updates = [{"key": "test", "value": "123"}]
    await test_gossip._clean_buffer()
    assert test_gossip.future_updates == [], "_clean_buffer failed"

@pytest.fixture
def mock_heartbeat():
    heartbeat = AsyncMock(spec=Heartbeat)
    heartbeat.getActivePeers.return_value = [
        "http://peer1:5000",
        "http://peer3:5000"
    ]
    return heartbeat

@pytest_asyncio.fixture
async def gossip_manager(mock_heartbeat):
    peers = ["http://peer1:5000", "http://peer2:5000", "http://peer3:5000"]
    gossip = GossipManager(peers=peers, interval=1, heartbeat=mock_heartbeat)
    await gossip.start()
    yield gossip
    await gossip.stop()

@pytest.mark.asyncio
async def test_gossip_uses_active_peers(gossip_manager, mock_heartbeat):
    update = {"id": "1", "key": "test", "value": "123"}
    await gossip_manager.add_update(update)

    active_peers = await mock_heartbeat.getActivePeers()
    
    assert "http://peer2:5000" not in active_peers, "inactive peer selected"
    assert len(active_peers) == 2, "wrong number of active peers"