from fastapi import APIRouter, Depends, HTTPException, status, Response, UploadFile, Request
from fastapi.responses import StreamingResponse
from typing import Annotated
import mimetypes

from schemas.users import UserGetDTO
from schemas.clients import OrderDTO, ShowOrderDTO, ClientDTO
from .dependencies import get_current_client, get_current_user
from db.orm import create_order, change_order, del_order, change_role, create_client, delete_client, get_client_orders, add_file, get_file
from models import UserRole
from utils import create_token, iterfile, get_file_etag
from redis import redis


router = APIRouter(prefix="", tags=["Клиенты"])

CurrentClient = Annotated[ClientDTO, Depends(get_current_client)]


@router.get("/orders")
async def get_orders(client: CurrentClient) -> list[ShowOrderDTO]:
    orders = await get_client_orders(client_id=client.id)
    return orders

@router.post("/orders")
async def add_order(order: OrderDTO, client: CurrentClient) -> int:
    res = await create_order(client_id=client.id, name=order.name, status=order.status)
    await redis.delete("clients_cache")
    return res

@router.put("/orders/{order_id}")
async def update_order(order_id: int, order: OrderDTO, client: CurrentClient) -> ShowOrderDTO:
    res = await change_order(client_id=client.id, name=order.name, status=order.status, order_id=order_id)
    if res:
        await redis.delete("clients_cache")
        return res
    else: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have no order with that id")

@router.delete("/orders/{order_id}")
async def delete_order(order_id: int, client: CurrentClient):
    res = await del_order(order_id=order_id, client_id=client.id)
    if res: 
        await redis.delete("clients_cache")
        return {'status': 'ok'}
    else: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have no order with that id")

@router.post("/start")
async def become_client(response: Response, user: UserGetDTO = Depends(get_current_user)):
    if user.role!='user': raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't become client")
    await change_role(user_id=user.id, role=UserRole.CLIENT)
    res = await create_client(username=user.username, user_id=user.id)
    if res:
        response.delete_cookie(key="access_token")
        token = await create_token(user_id=user.id, username=user.username, role='client')
        response.set_cookie("access_token", token)
        await redis.delete("clients_cache")
        return {"status": "ok"}

@router.post("/end")
async def unbecome_client(response: Response, client: CurrentClient):
    await change_role(user_id=client.user_id, role=UserRole.USER)
    res = await delete_client(client_id=client.id)
    if res:
        response.delete_cookie(key="access_token")
        token = await create_token(user_id=client.user_id, username=client.username, role='user')
        response.set_cookie("access_token", token)
        await redis.delete("clients_cache")
        return {"status": "ok"}


@router.post("/files")
async def upload_files(uploaded_files: list[UploadFile], client: CurrentClient):
    for uploaded_file in uploaded_files:
        file = uploaded_file.file
        filename = uploaded_file.filename
        with open(f"media/{client.id}_{filename}", "wb") as f:
            f.write(file.read())
            await add_file(client_id=client.id, filename=filename)
    return {'status': 'ok'}

# без кэширование
# @router.get("/files")
# async def get_streaming_file(client: CurrentClient, filename: str):
#     file = await get_file(filename=filename, client_id=client.id)
#     if not file: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="file not found")
#     mime_type, _ = mimetypes.guess_type(file.filename)
#     media_type = mime_type or "application/octet-stream"
#     return StreamingResponse(iterfile(filename=file.filename, client_id=client.id), media_type=media_type)

# с кэшированием
@router.get("/files")
async def get_streaming_file(client: CurrentClient, filename: str, request: Request):
    file = await get_file(filename=filename, client_id=client.id)
    if not file: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="file not found")
    mime_type, _ = mimetypes.guess_type(file.filename)
    media_type = mime_type or "application/octet-stream"
    
    file_path = f"media/{client.id}_{filename}"
    etag = get_file_etag(file_path)
    request_etag = request.headers.get("If-None-Match")
    if request_etag == etag:
        return Response(status_code=304)
    headers = {
        "ETag": etag,
        "Cache-Control": "private, max-age=86400",  # 24 часа кэша
    }

    return StreamingResponse(iterfile(filename=file.filename, client_id=client.id), media_type=media_type, headers=headers)
