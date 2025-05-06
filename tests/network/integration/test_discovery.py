import pytest
import asyncio
from src.network.discovery import PeerDiscovery
import socket

@pytest.mark.asyncio
async def test_broadcast_hello():
    discovery = PeerDiscovery(listen_port=9999, broadcast_port=9999)
    await discovery.start()
    
    await discovery.broadcast_hello(times=1, interval=0.1)
    
    assert discovery._bc_sock.getsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST) == 1
    
    await discovery.stop()

@pytest.mark.asyncio
async def test_get_peers():
    discovery = PeerDiscovery(listen_port=9999, broadcast_port=9999)
    await discovery.start()
    
    discovery.discovered.add("http://node1:8000")
    peers = discovery.get_peers()
    
    assert "http://node1:8000" in peers
    
    await discovery.stop()

@pytest.mark.asyncio
async def test_multiple_send():
    discovery = PeerDiscovery(listen_port=9999, broadcast_port=9999)
    await discovery.start()
    
    discovery.discovered.add("http://node1:8000")
    discovery.discovered.add("http://node2:8000")
    
    peers = discovery.get_peers()
    
    assert len(peers) == 2
    assert "http://node1:8000" in peers
    assert "http://node2:8000" in peers
    
    await discovery.stop()