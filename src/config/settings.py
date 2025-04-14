from pydantic_settings import BaseSettings
from typing import List
import os

# class Settings(BaseSettings):
#     NODE_ID: str = os.getenv("NODE_ID", "1")
#     SHARD_ID: int = int(os.getenv("SHARD_ID", 0))
#     NODE_ADDRESS: str = os.getenv("NODE_ADDRESS", "http://localhost:8000")
#     ALL_PEERS: List[str] = os.getenv("ALL_PEERS", "http://node1:8000,http://node2:8000,http://node3:8000").split(",")
#     ALL_PEERS: List[str] = ("http://node1:8000,http://node2:8000,http://node3:8000").split(",")
#     ALL_PEERS_IDS: List[str] = os.getenv("ALL_PEERS_IDS", "1,2,3").split(",")
#     PEERS_NUMBER: int = len(os.getenv("ALL_PEERS", "").split(","))
#     GOSSIP_PEERS: List[str] = os.getenv("GOSSIP_PEERS", "").split(",")
#     STORAGE_AUTOSAVE_INTERVAL: int = 10
#     GOSSIP_INTERVAL: int = 3
#     HEARTBEAT_INTERVAL: int = 2

# settings = Settings()