import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
import hashlib

from config import settings


async def encode_jwt(payload: dict, key: str = settings.auth_jwt.private_key_path.read_text(), algorithm: str = settings.auth_jwt.algorithm,
                    expire_minutes: int = settings.auth_jwt.access_token_expire_minutes):
    now = datetime.now(tz=timezone.utc)
    to_encode = payload.copy()
    to_encode.update(exp=now + timedelta(minutes=expire_minutes), iat=now)
    encoded = jwt.encode(payload=to_encode, key=key, algorithm=algorithm)
    return encoded

async def decode_jwt(token: str|bytes, key: str = settings.auth_jwt.public_key_path.read_text(), algorithm: str = settings.auth_jwt.algorithm):
    decoded = jwt.decode(jwt=token, key=key, algorithms=[algorithm])
    return decoded


async def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt)

async def validate_password(password:str, hashed_password: bytes) -> bool:
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode() 
    return bcrypt.checkpw(password=password.encode(), hashed_password=hashed_password)

async def create_token(user_id: int, username: str, role: str):
    payload = {
        "sub": user_id,
        "id": user_id,
        "username": username,
        "role": role
    }
    token = await encode_jwt(payload)
    return token


def iterfile(client_id: int, filename: str):
    with open(f"media/{client_id}_{filename}", "rb") as file:
        while chunk := file.read(1024 * 1024):
            yield chunk

def get_file_etag(file_path: str) -> str:
    """Генерируем ETag (хеш файла)"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
