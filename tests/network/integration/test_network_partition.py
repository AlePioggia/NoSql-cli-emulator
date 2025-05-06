import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from src.network.gossip import GossipManager
from src.network.heartbeat import Heartbeat
import pytest_asyncio

@pytest.fixture
def mock_heartbeat():
    heartbeat = AsyncMock()
    heartbeat.getActivePeers.return_value = [
        "http://peer1:8000", "http://peer3:8000"
    ]
    return heartbeat

@pytest_asyncio.fixture
async def gossip_manager(mock_heartbeat):
    peers = ["http://peer1:8000", "http://peer2:8000", "http://peer3:8000"]
    gm = GossipManager(peers=peers, interval=0.5, heartbeat=mock_heartbeat)
    await gm.start()
    yield gm
    await gm.stop()

@patch("httpx.AsyncClient.post", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_network_partition(mock_post, gossip_manager, mock_heartbeat):
    mock_post.return_value.status_code = 200

    update = {"id": "1", "key": "partition_key", "value": "test_value"}
    await gossip_manager.add_update(update)

    await asyncio.sleep(2.5) 
    active_peers = await mock_heartbeat.getActivePeers()
    for peer in active_peers:
        assert peer in ["http://peer1:8000", "http://peer3:8000"], "Inactive peer included"

    assert "1" in gossip_manager.sent_gossips, "Update not recorded"