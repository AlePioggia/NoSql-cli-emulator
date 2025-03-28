from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from src.persistance.in_memory_store import InMemoryStore
from src.network.gossip import GossipManager
import os

app = FastAPI()
store = InMemoryStore()

class ValueModel(BaseModel):
    value: str

class GossipUpdate(BaseModel):
    key: str
    value: str

class GossipMessage(BaseModel):
    updates: list[GossipUpdate]

# def get_gossip_manager():
#     return app.state.gossip_manager

@app.on_event("startup")
async def startup_event():
    peers_env = os.getenv("GOSSIP_PEERS", "")
    peers = peers_env.split(",") if peers_env else []
    app.state.gossip_manager = GossipManager(peers=peers, interval=5)
    app.state.gossip_manager.start()

@app.post("/gossip")
async def receive_gossip(message: GossipMessage):
    for update in message.updates:
        store.set(update.key, update.value)
    return {"message": "Gossip received"}

@app.post("/set/{key}")
async def set_key(key: str, data: ValueModel):
    store.set(key, data.value)
    app.state.gossip_manager.add_update({"key": key, "value": data.value})
    return {"key": key, "value": data.value}

@app.get("/get/{key}")
async def get_key(key: str):
    value = store.get(key)
    if value is None:
        raise HTTPException(status_code=404, detail="Key not found")
    return {"key": key, "value": value}

@app.delete("/delete/{key}")
async def delete_key(key: str):
    store.delete(key)
    return {"key": key}

@app.get("/keys")
async def get_keys():
    return {"keys": list(store.keys())}