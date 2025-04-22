from fastapi import FastAPI, HTTPException, Depends, Header, Request
from pydantic import BaseModel
from src.persistance.in_memory_store import InMemoryStore
from src.network.gossip import GossipManager
from src.network.heartbeat import Heartbeat
import os
from contextlib import asynccontextmanager
import uuid
from typing import Dict
import time
from src.clocks.conflict_resolver import LWW_resolve_conflict
from src.utils.VectorClockResponsState import VectorClockResponseState
from src.clocks.vector_clock import VectorClock
import traceback
from src.network.sharding import ShardingManager
from src.security.api_key_validator import APIKeyValidator

app = FastAPI()

class ValueModel(BaseModel):
    value: str

class GossipUpdate(BaseModel):
    id: str
    key: str
    value: str
    vector_clock: Dict[str, int]

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
    heartbeat = Heartbeat(peers, interval=2)
    await heartbeat.start()

    enable_sharding: bool = os.getenv("ENABLE_SHARDING", "false").lower() == "true"    
    gossip_manager = GossipManager(peers=peers, interval=3, heartbeat=heartbeat, shardManager=None if not enable_sharding else ShardingManager())
    app.state.gossip_manager = gossip_manager
    
    await app.state.gossip_manager.start()
    
    store = InMemoryStore()
    app.state.store = store 
    
    await app.state.store._load_data_from_disk()
    
    await app.state.store.start_autosave()

@app.post("/gossip")
async def receive_gossip(message: GossipMessage):
    try:
        for update in message.updates:
            local_value = await app.state.store.get(update.key)
            local_vc = VectorClock()
            local_vc.clock = await app.state.store.getVectorClock(update.key)
            remote_value = update.value
            remote_vc = VectorClock()
            remote_vc.clock = update.vector_clock.copy()

            if local_vc is None or local_value is None:
                await app.state.store.set(update.key, update.value, remote_vc.clock)
                await app.state.gossip_manager.add_update({"id": update.id, "key": update.key, "value": update.value, "vector_clock": remote_vc.clock})
            else:
                lww = LWW_resolve_conflict(local_vc, remote_vc.clock, local_value, remote_value)
                if lww == VectorClockResponseState.ACCEPT:
                    await app.state.store.set(update.key, update.value, remote_vc.clock)
                    await app.state.gossip_manager.add_update({"id": update.id, "key": update.key, "value": update.value, "vector_clock": remote_vc.clock})

        serialized_network = message.gossip_network
        await app.state.gossip_manager.update_network(serialized_network)
        return ValueModel(value="Gossip received")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing gossip: {str(e)}")

def get_api_key(api_key: str = Header(...)):
    return api_key

@app.post("/set/{key}")
async def set_key(key: str, data: ValueModel, request:Request):
    try:
        api_key = request.headers.get("X-API-KEY")
        api_key_validator = APIKeyValidator(api_key)
        if not api_key_validator.validate_api_key():
            raise HTTPException(status_code=403, detail="Invalid API Key")
        if not api_key_validator.has_permission("admin"):
            raise HTTPException(status_code=403, detail="Permission denied")
        
        current_vc: VectorClock = VectorClock()
        clock = await app.state.store.getVectorClock(key)
        if clock is not None:
            current_vc.clock = clock.copy()
        current_vc.increment()
        await app.state.store.set(key, data.value, current_vc.clock)
        gossip_id = str(uuid.uuid4())
        await app.state.gossip_manager.add_update({"id": gossip_id, "key": key, "value": data.value, "vector_clock": current_vc.clock})
        return {"key": key, "value": data.value}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing gossip: {str(e)}")

@app.get("/get/{key}")
async def get_key(key: str, request: Request):
    api_key = request.headers.get("X-API-KEY")
    api_key_validator = APIKeyValidator(api_key)
    if not api_key_validator.validate_api_key():
        raise HTTPException(status_code=403, detail="Invalid API Key")
    if not api_key_validator.has_permission("user") or not api_key_validator.has_permission("admin"):
        raise HTTPException(status_code=403, detail="Permission denied")
    value = await app.state.store.get(key)
    if value is None:
        raise HTTPException(status_code=404, detail="Key not found")
    return {"key": key, "value": value}

@app.delete("/delete/{key}")
async def delete_key(key: str, request: Request):
    api_key = request.headers.get("X-API-KEY")
    api_key_validator = APIKeyValidator(api_key)
    if not api_key_validator.validate_api_key():
        raise HTTPException(status_code=403, detail="Invalid API Key")
    if not api_key_validator.has_permission("admin"):
        raise HTTPException(status_code=403, detail="Permission denied")
    await app.state.store.delete(key)
    return {"key": key}

@app.get("/keys")
async def get_keys(request: Request):
    api_key = request.headers.get("X-API-KEY")
    api_key_validator = APIKeyValidator(api_key)
    if not api_key_validator.validate_api_key():
        raise HTTPException(status_code=403, detail="Invalid API Key")
    if not api_key_validator.has_permission("admin") or not api_key_validator.has_permission("user"):
        raise HTTPException(status_code=403, detail="Permission denied")
    return {"keys": list(await app.state.store.keys())}

@app.get("/heartbeat")
async def heartbeat():
    return {"status": "alive"}

@app.on_event("shutdown")
async def shutdown_event():
    if app.state.gossip_manager.isRunning:
        await app.state.gossip_manager.stop()
