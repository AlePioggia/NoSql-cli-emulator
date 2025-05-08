import xxhash
import os

class ShardingManager:
    def __init__(self):
        pass

    def getHashedShardNumber(self, key: str, nodes_number:int = None) -> int:
        if nodes_number is None:
            nodes_number = len(os.getenv("ALL_PEERS", "").split(","))
        
        key_hash = xxhash.xxh64(key.encode()).intdigest()
        destination_node = key_hash % nodes_number
        return destination_node