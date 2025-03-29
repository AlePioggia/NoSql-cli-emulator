# import pytest
# from httpx import AsyncClient, ASGITransport
# from main import app

# @pytest.fixture(autouse=True)
# async def setup_and_teardown():
#     await app.router.startup()
#     yield
#     await app.router.shutdown()

# @pytest.mark.asyncio
# async def test_set_key():
#     async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
#         response = await ac.post("/set/foo", json={"value": "bar"})
#     assert response.status_code == 200
#     assert response.json() == {"key": "foo", "value": "bar"}

# @pytest.mark.asyncio
# async def test_get_key():
#     async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
#         await ac.post("/set/foo", json={"value": "bar"})
#         response = await ac.get("/get/foo")
#     assert response.status_code == 200
#     assert response.json() == {"key": "foo", "value": "bar"}

# @pytest.mark.asyncio
# async def test_delete_key():
#     async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
#         await ac.post("/set/foo", json={"value": "bar"})
#         response = await ac.delete("/delete/foo")
#     assert response.status_code == 200
#     assert response.json() == {"key": "foo"}
