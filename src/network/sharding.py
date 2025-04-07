import xxhash
from src.config import settings

class ShardingManager:
    def __init__(self):
        pass

    def getHashedShardNumber(self, key: str, nodes_number:int = None) -> int:
        if nodes_number is None:
            nodes_number = settings.Settings.PEERS_NUMBER
        
        key_hash = xxhash.xxh64(key.encode()).intdigest()
        destination_node = key_hash % nodes_number
        return destination_node

