from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from src.persistance.in_memory_store import InMemoryStore
from src.network.gossip import GossipManager
from src.network.heartbeat import Heartbeat
import os
from contextlib import asynccontextmanager
import uuid

app = FastAPI()

class ValueModel(BaseModel):
    value: str

class GossipUpdate(BaseModel):
    id: str
    key: str
    value: str

class GossipMessage(BaseModel):
    updates: list[GossipUpdate]
    gossip_network: str

class KeyValueResponse(BaseModel):
    key: str
    value: str

@app.on_event("startup")
async def startup_event():
    peers_env = os.getenv("GOSSIP_PEERS", "")
    peers = peers_env.split(",") if peers_env else []
    heartbeat = Heartbeat(peers, 10)
    await heartbeat.start()

    gossip_manager = GossipManager(peers=peers, interval=1, heartbeat=heartbeat)
    app.state.gossip_manager = gossip_manager
    
    await app.state.gossip_manager.start()
    
    store = InMemoryStore()
    app.state.store = store 
    
    await app.state.store._load_data_from_disk()
    
    await app.state.store.start_autosave()

@app.post("/gossip")
async def receive_gossip(message: GossipMessage):
    for update in message.updates:
        await app.state.store.set(update.key, update.value)
        await app.state.gossip_manager.add_update({"id": update.id, "key": update.key, "value": update.value})
    serialized_network = message.gossip_network
    await app.state.gossip_manager.update_network(serialized_network)
    return ValueModel(value="Gossip received")

@app.post("/set/{key}")
async def set_key(key: str, data: ValueModel):
    await app.state.store.set(key, data.value)
    gossip_id = str(uuid.uuid4())
    await app.state.gossip_manager.add_update({"id": gossip_id, "key": key, "value": data.value})
    return {"key": key, "value": data.value}

@app.get("/get/{key}")
async def get_key(key: str):
    value = await app.state.store.get(key)
    if value is None:
        raise HTTPException(status_code=404, detail="Key not found")
    return {"key": key, "value": value}

@app.delete("/delete/{key}")
async def delete_key(key: str):
    await app.state.store.delete(key)
    return {"key": key}

@app.get("/keys")
async def get_keys():
    return {"keys": list(await app.state.store.keys())}

# add heartbeat method
@app.get("/heartbeat")
async def heartbeat():
    return {"status": "alive"}

@app.on_event("shutdown")
async def shutdown_event():
    if app.state.gossip_manager.isRunning:
        await app.state.gossip_manager.stop()
