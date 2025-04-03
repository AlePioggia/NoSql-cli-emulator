import pytest
import asyncio
import time
from unittest.mock import AsyncMock, patch
from src.persistance.in_memory_store import InMemoryStore
from src.network.gossip import GossipManager
from src.network.heartbeat import Heartbeat
import uuid
import pytest_asyncio

@pytest.fixture
def in_memory_store():
    return InMemoryStore()

@pytest_asyncio.fixture
async def gossip_manager():
    heartbeat = AsyncMock()
    heartbeat.getActivePeers.return_value = ["http://peer1:8000", "http://peer2:8000"]
    gm = GossipManager(peers=["http://peer1:8000", "http://peer2:8000"], interval=0.5, heartbeat=heartbeat)
    await gm.start()
    try:
        yield gm
    finally:
        await gm.stop()

@pytest.mark.asyncio
async def test_lww_persistence(in_memory_store):
    key = "test_key"
    await in_memory_store.set(key, "old_value", timestamp=1000)
    await in_memory_store.set(key, "new_value", timestamp=2000)

    value = await in_memory_store.get(key)
    assert value == "new_value", "LWW didn't overwrite the old value"

@pytest.mark.asyncio
async def test_lww_gossip_propagation(in_memory_store, gossip_manager):
    key = "test_gossip_key"
    old_update = {"id": "1", "key": key, "value": "old_value", "timestamp": 1000}
    new_update = {"id": "2", "key": key, "value": "new_value", "timestamp": 2000}

    await gossip_manager.add_update(old_update)
    await in_memory_store.set(old_update["key"], old_update["value"], old_update["timestamp"])

    await gossip_manager.add_update(new_update)
    await in_memory_store.set(new_update["key"], new_update["value"], new_update["timestamp"])

    value = await in_memory_store.get(key)
    assert value == "new_value", "LWW didn't propagate the new value correctly"

@pytest.mark.asyncio
async def test_key_management(in_memory_store):
    key = "sample_key"
    await in_memory_store.set(key, "some_value")
    
    value = await in_memory_store.get(key)
    assert value == "some_value", "value wasn't overwritten correctly"

    await in_memory_store.delete(key)
    value = await in_memory_store.get(key)
    assert value is None, "key wasn't eliminated correctly"