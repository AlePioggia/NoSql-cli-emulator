import asyncio
import httpx
import uuid
from src.model.Gossip import GossipNetwork
from src.network.heartbeat import Heartbeat
from src.network.sharding import ShardingManager
import os 
import time
from src.clocks.vector_clock import VectorClock

class GossipManager:

    def __init__(self, peers, interval, heartbeat = None, shardManager: ShardingManager = None):
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
        self.node_address = os.getenv("NODE_ADDRESS", "http://localhost:8000")
        self.shardManager = shardManager
        self.vector_clock = VectorClock()
        self.unsent_updates: dict[str, list] = {}

    async def start(self):
        self._main_task = asyncio.create_task(self._main_loop())

    async def stop(self):
        self.isRunning = False
        if self._main_task:
            await self._main_task 

    async def add_update(self, update):
        async with self.lock:
            if self.shardManager is not None:
                correct_node = self.shardManager.getHashedShardNumber(update["key"])
                if correct_node != self.node_address:
                    return

            if update["id"] not in self.sent_gossips:
                self.future_updates.append(update)

    async def _main_loop(self):
        async with httpx.AsyncClient() as client:
            while self.isRunning:
                await asyncio.sleep(self.interval)
                try:
                    active_peers = await self.heartbeat.getActivePeers()
                    
                    # Retry pending updates
                    for peer in list(self.unsent_updates.keys()):
                        if peer not in active_peers:
                            continue
                        updates = self.unsent_updates.get(peer, [])
                        successful = []
                        for update in updates:
                            success = await self._send_gossip_to_peer(client, peer, update)
                            if success:
                                successful.append(update)
                        # remove old updates
                        self.unsent_updates[peer] = [u for u in updates if u not in successful]
                        if not self.unsent_updates[peer]:
                            del self.unsent_updates[peer]

                    # Send new updates
                    updates_copy = self.future_updates.copy()
                    for update in updates_copy:
                        selected_peers = self.gossip_network.filter_peers(active_peers, update["id"], self.node_id)
                        if not selected_peers:
                            continue
                        sent_to_all = True
                        for peer in selected_peers:
                            success = await self._send_gossip_to_peer(client, peer, update)
                            if not success:
                                sent_to_all = False
                                if peer not in self.unsent_updates:
                                    self.unsent_updates[peer] = []
                                if update not in self.unsent_updates[peer]:
                                    self.unsent_updates[peer].append(update)
                        if sent_to_all:
                            self.future_updates.remove(update)

                except Exception as ex:
                    print(f"Error in gossip loop: {ex}")


    async def _send_gossip_to_peer(self, client, peer, update):
        try:
            payload = {
                "updates": [update],
                "gossip_network": self.gossip_network.serialize()
            }
            response = await client.post(f"{peer}/gossip", json=payload)
            if response.status_code == 200:
                self.sent_gossips[update["id"]] = update
                self.gossip_network.add_sent_gossip(self.node_id, update["id"], peer)
                self.gossip_network.add_received_gossip(peer, update["id"], self.node_id)
            else:
                if peer not in self.unsent_updates:
                    self.unsent_updates.push(peer, update)
                else:
                    self.unsent_updates[peer].append(update)
        except Exception as ex:
            print(f"Error sending gossip to {peer}: {ex}") 

    async def update_network(self, serialized_network: str):
        new_network = GossipNetwork.deserialize(serialized_network)
        self.gossip_network.update_network(new_network)

    async def _clean_buffer(self):
        async with self.lock:
            self.future_updates = []