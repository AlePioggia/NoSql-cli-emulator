import os
import json
import pytest
import time
from src.persistance.in_memory_store import InMemoryStore

@pytest.fixture
def test_store(tmp_path):
    test_file = tmp_path / "data_test.json"
    store = InMemoryStore(storage_file=str(test_file), autosave_interval=1)
    yield store

def test_set_get(test_store):
    test_store.set("key", "value")
    assert test_store.get("key") == "value", "set/get failed"

def test_delete(test_store):
    test_store.set("key", "value")
    test_store.delete("key")
    assert test_store.get("key") is None, "delete failed"

def test_dump_load(test_store):
    test_store.set("key", "value")
    dumped = test_store.dump()
    test_store.delete("key")
    test_store.load(dumped)
    assert test_store.get("key") == "value", "dump/load failed"

def test_autosave(test_store):
    test_store.set("key", "value")
    time.sleep(2)
    assert os.path.exists(test_store.storage_file), "autosave failed"