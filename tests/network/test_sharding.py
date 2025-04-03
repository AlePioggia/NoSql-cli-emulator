import pytest
from src.network.sharding import ShardingManager
import xxhash

@pytest.mark.parametrize(
    "key, nodes_number, expected_shard",
    [
        ("test1", 10, xxhash.xxh64("test1").intdigest() % 10),
        ("test2", 10, xxhash.xxh64("test2").intdigest() % 10),
        ("test3", 10, xxhash.xxh64("test3").intdigest() % 10),
        ("another_key", 5, xxhash.xxh64("another_key").intdigest() % 5),
    ]
)
def test_sharding_single_key(key, nodes_number, expected_shard):
    sharding_manager = ShardingManager()
    shard = sharding_manager.getHashedShardNumber(key, nodes_number)
    assert shard == expected_shard, f"Key {key} should be assigned to shard {expected_shard}, but got {shard}"


def test_sharding_balanced_distribution():
    sharding_manager = ShardingManager()
    nodes_number = 10
    key_counts = {i: 0 for i in range(nodes_number)}

    for i in range(1000):
        shard = sharding_manager.getHashedShardNumber(f"key_{i}", nodes_number)
        key_counts[shard] += 1

    max_count = max(key_counts.values())
    min_count = min(key_counts.values())

    assert (max_count - min_count) <= 40, "shards are not evenly distributed"

def test_sharding_deterministic():
    sharding_manager = ShardingManager()
    nodes_number = 4

    key = "consistent_key"
    first_shard = sharding_manager.getHashedShardNumber(key, nodes_number)
    second_shard = sharding_manager.getHashedShardNumber(key, nodes_number)

    assert first_shard == second_shard, "sharding should be deterministic for the same key"
