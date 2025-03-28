from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from persistance.in_memory_store import InMemoryStore
from network.gossip import GossipManager

app = FastAPI()
store = InMemoryStore()

class ValueModel(BaseModel):
    value: str

class GossipUpdate(BaseModel):
    key: str
    value: str
    timestamp: float

class GossipMessage(BaseModel):
    updates: list[GossipUpdate]

def get_gossip_manager():
    return app.state.gossip_manager

@app.post("/gossip")
async def receive_gossip(message: GossipMessage):
    for update in message.updates:
        store.set(update.key, update.value)
    return {"message": "Gossip received"}

@app.post("/set/{key}")
async def set_key(key: str, data: ValueModel, gossip_manager: GossipManager = Depends(get_gossip_manager)):
    store.set(key, data.value)
    gossip_manager.add_update({"key": key, "value": data.value})
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