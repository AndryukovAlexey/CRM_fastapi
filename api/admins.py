from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
import json

from schemas.admins import NewOrder, UsersDTO, CUserRole
from schemas.managers import ManagerDTO, ShowOrdersClientsDTO
from schemas.clients import ClientRelDTO
from .dependencies import get_current_admin
from db.orm import get_users, get_clients, get_orders, create_order, del_order, get_client
from redis import redis
from db.database import engine


router = APIRouter(prefix="/admins", tags=["Админы"])

CurrentAdmin = Annotated[ManagerDTO, Depends(get_current_admin)]


@router.get("/users")
async def get_all_users(admin: CurrentAdmin) -> list[UsersDTO]:
    res = await get_users()
    return res

@router.get("/clients")
async def get_all_clients(admin: CurrentAdmin) -> list[ClientRelDTO]:
    cached_data = await redis.get("clients_cache")
    if cached_data:
        clients_list = json.loads(cached_data)
        return [ClientRelDTO.model_validate(client) for client in clients_list]
    
    res = await get_clients()

    res_dump = [client.model_dump(mode="json") for client in res]
    await redis.set("clients_cache", json.dumps(res_dump), ex=3600)

    return res

@router.get("/orders")
async def get_all_orders(admin: CurrentAdmin) -> list[ShowOrdersClientsDTO]:
    res = await get_orders()
    return res

@router.post("/orders")
async def create_new_order(order: NewOrder, admin: CurrentAdmin):
    client = await get_client(client_id=order.client_id)
    if not client: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    await create_order(client_id=order.client_id, name=order.name, status=order.status)
    await redis.delete("clients_cache")
    return {'status': 'ok'}


@router.delete("/orders/{order_id}")
async def delete_order(order_id: int, admin: CurrentAdmin):
    res = await del_order(order_id=order_id)
    if not res: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="order not found")
    await redis.delete("clients_cache")
    return {'status': 'ok'}

