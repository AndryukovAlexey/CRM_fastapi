from pydantic import BaseModel


class UserPostDTO(BaseModel):
    username: str
    password: str

class UserGetDTO(BaseModel):
    id: int
    username: str
    role: str
    hashed_password: bytes

class TokenDTO(BaseModel):
    access_token: str
    token_type: str
