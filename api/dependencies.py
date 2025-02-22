from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt.exceptions import InvalidTokenError

from schemas.users import UserPostDTO, UserGetDTO
from schemas.clients import ClientDTO
from schemas.managers import ManagerDTO
import utils as auth_utils
from db.orm import get_user, get_client, get_superuser


http_bearer = HTTPBearer(auto_error=False)


async def get_token_payload_or_cookie(request: Request, credentials: HTTPAuthorizationCredentials = Depends(http_bearer)):
    token = request.cookies.get("access_token")
    if not token and credentials:
        token = credentials.credentials
    elif not token and not credentials:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authenticated")
    try:
        payload = await auth_utils.decode_jwt(token=token)
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token error")
    return payload

async def get_current_client(payload: dict = Depends(get_token_payload_or_cookie)) -> ClientDTO:
    user_id = payload.get("id")
    user_role = payload.get("role")
    if user_role!="client": raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not client")
    if client := await get_client(user_id=user_id): return client
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token invalid")

async def get_current_admin(payload: dict = Depends(get_token_payload_or_cookie)) -> ManagerDTO:
    user_id = payload.get("id")
    user_role = payload.get("role")
    if user_role!="admin": raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not admin")
    if admin := await get_superuser(user_id=user_id): return admin
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token invalid")

async def get_current_manager(payload: dict = Depends(get_token_payload_or_cookie)) -> ManagerDTO:
    user_id = payload.get("id")
    user_role = payload.get("role")
    if user_role!="manager": raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not manager")
    if manager := await get_superuser(user_id=user_id): return manager
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token invalid")

async def get_current_user(payload: dict = Depends(get_token_payload_or_cookie)) -> UserGetDTO:
    user_id = payload.get("id")
    if user := await get_user(id=user_id): return user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token invalid")

async def pre_reg_check(user: UserPostDTO):
    if await get_user(username=user.username): raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="user already exist")
    return {'username': user.username, 'password': user.password}


async def validate_auth_user(user: UserPostDTO):
    unauth_exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid username or password")
    user_db = await get_user(username=user.username)
    if not(user_db): raise unauth_exc
    if await auth_utils.validate_password(password=user.password, hashed_password=user_db.hashed_password):
        return user_db
    raise unauth_exc
