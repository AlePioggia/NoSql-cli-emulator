import asyncio
import json
import socket
import os

class PeerDiscovery:
    def __init__(self, listen_port: int = 9999, broadcast_port: int = 9999):
        self.listen_port = listen_port
        self.broadcast_port = broadcast_port
        self.node_id = os.getenv("NODE_ID", "default_node_id")
        self.node_addr = os.getenv("NODE_ADDRESS", "")
        self.running = False
        self.discovered: set[str] = set()
        # socket to send broadcast messages
        self._bc_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._bc_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # socket to receive broadcast messages
        self._rcv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._rcv_sock.bind(("", self.listen_port))
        self._rcv_sock.setblocking(False)
        
    async def start(self):
        self.running = True
        asyncio.create_task(self._listener())
        
    async def stop(self):
        self.running = False
        self._rcv_sock.close()
        self._bc_sock.close()
        
    async def _listener(self):
        loop = asyncio.get_event_loop()
        while self.running:
            data, (ip, _) = await loop.sock_recvfrom(self._rcv_sock, 1024)
            try:
                message = json.loads(data.decode())
                peer_id = message["node_id"]
                peer_addr = message["node_addr"]
                if peer_id != self.node_id:
                    self.discovered.add(peer_addr)
            except:
                pass

    async def broadcast_hello(self, times: int = 3, interval: float = 1.0):
        packet = json.dumps({
            "node_id": self.node_id,
            "node_addr": self.node_addr
        }).encode()
        
        for _ in range(times):
            self._bc_sock.sendto(packet, ("255.255.255.255", self.broadcast_port))
            await asyncio.sleep(interval)
    
    def get_peers(self) -> list[str]:
        return self.discovered.copy()