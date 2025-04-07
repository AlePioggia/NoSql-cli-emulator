from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    NODE_ID: str = os.getenv("NODE_ID", "default_node_id")
    SHARD_ID: int = int(os.getenv("SHARD_ID", 0))
    NODE_ADDRESS: str = os.getenv("NODE_ADDRESS", "http://localhost:8000")
    ALL_PEERS: str = os.getenv("ALL_PEERS", "").split(",")
    PEERS_NUMBER: int = len(os.getenv("ALL_PEERS", "").split(","))
    GOSSIP_PEERS: List[str] = os.getenv("GOSSIP_PEERS", "").split(",")
    STORAGE_AUTOSAVE_INTERVAL: int = 10
    GOSSIP_INTERVAL: int = 3
    HEARTBEAT_INTERVAL: int = 2



