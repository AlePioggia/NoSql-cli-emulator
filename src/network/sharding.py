class ShardingManager:
    def __init__(self):
        pass

    def getHashedShardNumber(self, key: str, nodes_number: int) -> int:
        key = hash(key)
        destination_node = key % nodes_number
        return destination_node

