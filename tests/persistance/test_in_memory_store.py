import pytest
import asyncio
from src.persistance.in_memory_store import InMemoryStore
import pytest_asyncio

@pytest_asyncio.fixture
async def test_store(tmp_path):
    test_file = tmp_path / "data_test.json"
    store = InMemoryStore(storage_file=str(test_file), autosave_interval=1)
    await store._load_data_from_disk()
    yield store
    await store.saveToDisk()

@pytest.mark.asyncio
async def test_set_get(test_store):
    await test_store.set("key", "value")
    assert (await test_store.get("key")) == "value", "set/get failed"

@pytest.mark.asyncio
async def test_delete(test_store):
    await test_store.set("key", "value")
    await test_store.delete("key")
    assert (await test_store.get("key") is None), "delete failed"

@pytest.mark.asyncio
async def test_dump_load(test_store):
    await test_store.set("key", "value")
    dumped = await test_store.dump()
    await test_store.delete("key")
    await test_store.load(dumped)
    assert (await test_store.get("key")) == "value", "dump/load failed"