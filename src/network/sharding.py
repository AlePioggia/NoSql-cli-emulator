import xxhash

class ShardingManager:
    def __init__(self):
        pass

    def getHashedShardNumber(self, key: str, nodes_number: int) -> int:
        key_hash = xxhash.xxh64(key.encode()).intdigest()
        destination_node = key_hash % nodes_number
        return destination_node
