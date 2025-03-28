from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from persistance.in_memory_store import InMemoryStore

app = FastAPI()
store = InMemoryStore()

class ValueModel(BaseModel):
    value: str

@app.post("/set/{key}")
async def set_key(key: str, data: ValueModel):
    store.set(key, data.value)
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