import pytest
from httpx import AsyncClient

from config import settings
from .conftest import TestSessionLocal


@pytest.mark.asyncio(loop_scope="module")
async def test_get_all_users(async_client: AsyncClient, monkeypatch):
    monkeypatch.setattr("db.orm.new_session", TestSessionLocal)

    response = await async_client.get("/admins/users", headers={"authorization": f"Bearer {settings.ADM_TOKEN_TEST}"})  # Запрашиваем список пользователей
    assert response.status_code == 200
    assert isinstance(response.json(), list)  # Проверяем, что возвращается список

@pytest.mark.asyncio(loop_scope="module")
async def test_get_all_clients(async_client: AsyncClient, monkeypatch, mock_redis):
    monkeypatch.setattr("db.orm.new_session", TestSessionLocal)

    monkeypatch.setattr("api.admins.redis", mock_redis)  # Подменяем Redis
    response = await async_client.get("/admins/clients", headers={"authorization": f"Bearer {settings.ADM_TOKEN_TEST}"})  # Запрос списка клиентов
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio(loop_scope="module")
async def test_get_all_orders(async_client: AsyncClient, monkeypatch):
    monkeypatch.setattr("db.orm.new_session", TestSessionLocal)

    response = await async_client.get("/admins/orders", headers={"authorization": f"Bearer {settings.ADM_TOKEN_TEST}"})  # Запрашиваем список пользователей
    assert response.status_code == 200
    assert isinstance(response.json(), list)  # Проверяем, что возвращается список

@pytest.mark.asyncio(loop_scope="module")
async def test_create_new_order(async_client: AsyncClient, monkeypatch, mock_redis):
    monkeypatch.setattr("db.orm.new_session", TestSessionLocal)
    monkeypatch.setattr("api.admins.redis", mock_redis)  # Подменяем Redis
    new_order = {"client_id": 1, "name": "Тестовый заказ", "status": "new"}

    response = await async_client.post("/admins/orders", json=new_order, headers={"authorization": f"Bearer {settings.ADM_TOKEN_TEST}"})
    
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio(loop_scope="module")
async def test_delete_order(async_client: AsyncClient, monkeypatch, mock_redis):
    monkeypatch.setattr("db.orm.new_session", TestSessionLocal)
    monkeypatch.setattr("api.admins.redis", mock_redis)  # Подменяем Redis

    order_id = 38
    response = await async_client.delete(f"/admins/orders/{order_id}", headers={"authorization": f"Bearer {settings.ADM_TOKEN_TEST}"})
    
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

