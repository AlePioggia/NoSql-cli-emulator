import json
import asyncio
import aiofiles
import time

class InMemoryStore:
    def __init__(self, storage_file="data.json", autosave_interval=10):
        self.storage_file = storage_file
        self.data = {}
        self.lock = asyncio.Lock()
        self.autosave_interval = autosave_interval

    async def start_autosave(self):
        asyncio.create_task(self._autosave())

    async def get(self, key):
        async with self.lock:
            if key in self.data:
                return self.data[key]["value"]
            return None

    async def set(self, key, value, timestamp=None):
        async with self.lock:
            current_time = timestamp or time.time()
            if key not in self.data or self.data[key]["timestamp"] < current_time:
                self.data[key] = {"value": value, "timestamp": current_time}

    async def delete(self, key):
        async with self.lock:
            if key in self.data:
                del self.data[key]

    async def keys(self):
        async with self.lock:
            return self.data.keys()

    async def dump(self):
        async with self.lock:
            return json.dumps(self.data)

    async def load(self, data):
        async with self.lock:
            self.data = json.loads(data)

    async def _load_data_from_disk(self):
        try:
            async with aiofiles.open(self.storage_file, "r") as f:
                content = await f.read()
                self.data = json.load(content)
        except FileNotFoundError:
            self.data = {}
    
    async def saveToDisk(self):
        async with self.lock:
            async with aiofiles.open(self.storage_file, "w") as f:
                await f.write(json.dumps(self.data))

    async def _autosave(self):
        while True:
            await asyncio.sleep(self.autosave_interval)
            await self.saveToDisk()