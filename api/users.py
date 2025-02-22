from fastapi import APIRouter, Depends, Response

from schemas.users import UserGetDTO, TokenDTO
import utils as auth_utils
from db.orm import create_user
from .dependencies import pre_reg_check, validate_auth_user, get_current_user


router = APIRouter(prefix="", tags=["Пользователь"])


# Регистрация
@router.post("/reg")
async def user_reg(user = Depends(pre_reg_check)):
    if await create_user(username=user['username'], hash_password=await auth_utils.hash_password(user['password'])): return {"status": "user was created"}
    else: return {"status": "user wasn't created"}


# Авторизация 
@router.post("/login", response_model=TokenDTO)
async def user_auth(response: Response, user: UserGetDTO = Depends(validate_auth_user)):
    token = await auth_utils.create_token(user_id=user.id, username=user.username, role=user.role)
    response.set_cookie("access_token", token)
    return TokenDTO(access_token=token, token_type="Bearer")

@router.get("/me") # only in dev
async def test_me(user: UserGetDTO = Depends(get_current_user)):
    return user


