from src.network.heartbeat import Heartbeat
import pytest_asyncio
import asyncio
import pytest
from pytest_httpx import HTTPXMock

@pytest_asyncio.fixture
async def heartbeat_instance():
    peers = ["http://localhost:8000", "http://localhost:8001"]
    interval = 1
    heartbeat = Heartbeat(peers, interval)
    yield heartbeat
    await heartbeat.stop()

@pytest.mark.asyncio
async def test_start_stop(heartbeat_instance):
    await heartbeat_instance.start()
    assert heartbeat_instance.isActive is True, "Heartbeat did not start correctly"
    await heartbeat_instance.stop()
    assert heartbeat_instance.isActive is False, "Heartbeat did not stop correctly"

@pytest.mark.asyncio
async def test_send_heartbeat(heartbeat_instance, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url="http://localhost:8000/heartbeat", status_code=200)
    await heartbeat_instance.start()
    result = await heartbeat_instance._send_heartbeat("http://localhost:8000")
    assert result is True, "_send_heartbeat failed"
    await heartbeat_instance.stop()

@pytest.mark.asyncio
async def test_send_heartbeat_peer_down(heartbeat_instance, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url="http://localhost:8000/heartbeat", status_code=500)
    await heartbeat_instance.start()
    result = await heartbeat_instance._send_heartbeat("http://localhost:8000")
    assert result is False, "_send_heartbeat failed for down peer"
    await heartbeat_instance.stop()

@pytest.mark.asyncio
async def test_send_heartbeat_error(heartbeat_instance, httpx_mock: HTTPXMock):
    httpx_mock.add_response(url="http://localhost:8000/heartbeat", status_code=400)
    await heartbeat_instance.start()
    result = await heartbeat_instance._send_heartbeat("http://localhost:8000")
    assert result is False, "_send_heartbeat failed for error response"
    await heartbeat_instance.stop()

@pytest.mark.asyncio
async def test_add_peer(heartbeat_instance):
    new_peer = "http://localhost:8002"
    await heartbeat_instance.add_peer(new_peer)
    assert new_peer in heartbeat_instance.peers, "Failed to add new peer"
    assert len(heartbeat_instance.peers) == 3, "Peer list length is incorrect after adding a new peer"