import asyncio
import httpx
import os
import uuid

class Heartbeat:
    def __init__(self, peers, interval):
        self.peers = peers
        self.interval = interval
        self.active_peers = set(peers)
        self.node_id = os.getenv("NODE_ID", str(uuid.uuid4()))
        self.isActive = True

    async def start(self):
        asyncio.create_task(self._check_peer_health())
        self.isActive = True

    async def _check_peer_health(self):
        while self.isActive:
            peers_copy = self.active_peers.copy()
            for peer in peers_copy:
                is_alive = await self._send_heartbeat(peer)
                if not is_alive:
                    print(f"Peer {peer} is down, removing from active peers.")
                    self.active_peers.remove(peer)
            await asyncio.sleep(self.interval)
    
    async def _send_heartbeat(self, peer):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{peer}/heartbeat")
                if response.status_code == 200:
                    return True
        except Exception as ex:
            print(f"Error sending heartbeat to {peer}: {ex}")
        return False
    
    async def getActivePeers(self):
        return list(self.active_peers)

    async def stop(self):
        self.isActive = False
        await asyncio.sleep(1)
        self.active_peers.clear()
        print("Heartbeat stopped and active peers cleared.")

