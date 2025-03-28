import json
import threading
import time

class InMemoryStore:
    def __init__(self, storage_file="data.json", autosave_interval=10):
        self.storage_file = storage_file
        self.data = {}
        self.lock = threading.Lock()

        self._load_data_from_disk()

        self.autosave_interval = autosave_interval
        self.autosave_thread = threading.Thread(target=self._autosave, daemon=True)
        self.autosave_thread.start()

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value):
        with self.lock:
            self.data[key] = value

    def delete(self, key):
        with self.lock:
            if key in self.data:
                del self.data[key]

    def keys(self):
        return self.data.keys()

    def dump(self):
        return json.dumps(self.data)

    def load(self, data):
        self.data = json.loads(data)

    def _load_data_from_disk(self):
        try:
            with open(self.storage_file, "r") as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {}
    
    def saveToDisk(self):
        with self.lock:
            with open(self.storage_file, "w") as f:
                json.dump(self.data, f)

    def _autosave(self):
        while True:
            time.sleep(self.autosave_interval)
            self.saveToDisk()
