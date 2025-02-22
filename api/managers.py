from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated

from schemas.managers import ManagerDTO, ShowOrdersClientsDTO
from schemas.clients import ClientRelDTO
from db.orm import get_clients, get_client, appoint_manager, unassignment_manager, get_orders
from .dependencies import get_current_manager
from redis import redis


router = APIRouter(prefix="/manager", tags=["Менеджеры"])

CurrentManager = Annotated[ManagerDTO, Depends(get_current_manager)]

@router.get("/clients") 
async def get_m_clients(manager: CurrentManager) -> list[ClientRelDTO]|None:
    res = await get_clients(manager.id)
    return res

@router.post("/clients/{client_id}")
async def start_manage_client(client_id: int, manager: CurrentManager):
    if client := await get_client(client_id=client_id):
        if client.manager_id==None:
            await appoint_manager(client_id=client_id, manager_id=manager.id)
            await redis.delete("clients_cache")
            return {'status': 'ok'}
        else: raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='client already has manager')
    else: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='client is not exist')

@router.delete("/clients/{client_id}") 
async def leave_m_client(client_id: int, manager: CurrentManager):
    if client := await get_client(client_id=client_id):
        if client.manager_id==manager.id:
            await unassignment_manager(client_id=client_id)
            await redis.delete("clients_cache")
            return {'status': 'ok'}
        else: raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='it is not your client')
    else: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='client is not exist')

@router.get("/orders") 
async def get_clients_orders(manager: CurrentManager) -> list[ShowOrdersClientsDTO]|None:
    res = await get_orders(manager_id=manager.id)
    return res
