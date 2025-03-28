import threading
import time
import random
import requests

class GossipManager:

    def __init__(self, peers, interval):
        self.peers = peers
        self.interval = interval
        self.future_updates = []
        self.isRunning = True
        self.lock = threading.Lock()

    def start(self):
        thread = threading.Thread(target=self._main_loop, daemon=True)
        thread.start()

    def stop(self):
        self.isRunning = False

    def add_update(self, update):
        with self.lock:
            self.future_updates.append(update)

    def _main_loop(self):
        while True:
            time.sleep(self.interval)
            with self.lock:
                if len(self.future_updates) > 0:
                    try:
                        selected_peer = random.choice(self.peers)
                        payload = {"updates": self.future_updates}
                        response = requests.post(selected_peer + "/gossip", json=payload)
                        if response.status_code == 200:
                            with self.lock:
                                self._clean_buffer(self)
                    except Exception as ex:
                        print(ex)

    def _clean_buffer(self):
        with self.lock:
            self.future_updates = []