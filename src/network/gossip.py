import random
import asyncio
import httpx
import uuid
from src.model.Gossip import GossipNetwork
from src.network.heartbeat import Heartbeat
import os 
import time

class GossipManager:

    def __init__(self, peers, interval, heartbeat=None):
        self.heartbeat: Heartbeat = heartbeat
        self.peers = peers
        self.interval = interval
        self.future_updates = []
        self.isRunning = True
        self.lock = asyncio.Lock()
        self._main_task = None
        self.sent_gossips = {}
        self.gossip_network: GossipNetwork = GossipNetwork()
        self.node_id = os.getenv("NODE_ID", str(uuid.uuid4()))
        self.gossip_network.add_node(self.node_id)

    async def start(self):
        self._main_task = asyncio.create_task(self._main_loop())

    async def stop(self):
        self.isRunning = False
        if self._main_task:
            await self._main_task 

    async def add_update(self, update):
        async with self.lock:
            if update["id"] not in self.sent_gossips:
                update["timestamp"] = update.get("timestamp", time.time())
                self.future_updates.append(update)

    async def _main_loop(self):
        async with httpx.AsyncClient() as client:
            while self.isRunning:
                await asyncio.sleep(self.interval)

                if len(self.future_updates) > 0:
                    try:
                        for update in self.future_updates:
                            active_peers = await self.heartbeat.getActivePeers()
                            selected_peers = self.gossip_network.filter_peers(active_peers, update["id"], self.node_id)
                            if selected_peers:
                                payload = {
                                    "updates": [update],
                                    "gossip_network": self.gossip_network.serialize()
                                }
                                for selected_peer in selected_peers:
                                    response = await client.post(f"{selected_peer}/gossip", json=payload)
                                    if response.status_code == 200:
                                        self.sent_gossips[update["id"]] = update
                                        self.gossip_network.add_sent_gossip(self.node_id, update["id"], selected_peer)
                                        self.gossip_network.add_received_gossip(selected_peer, update["id"], self.node_id)
                        await self._clean_buffer()
                    except Exception as ex:
                        print(f"Error in gossip loop: {ex}")

    async def update_network(self, serialized_network: str):
        new_network = GossipNetwork.deserialize(serialized_network)
        self.gossip_network.update_network(new_network)

    async def _clean_buffer(self):
        async with self.lock:
            self.future_updates = []