from pydantic import BaseModel

from models import UserRole, OrderStatus
from .clients import ShowOrderDTO


class NewOrder(BaseModel):
    client_id: int
    name: str
    status: OrderStatus

class ClientsDTO(BaseModel):
    id: int
    username: str
    manager_id: int
    orders: list[ShowOrderDTO]

class UsersDTO(BaseModel):
    id: int
    username: str
    role: UserRole
    clients: list["ClientsDTO"]

class CUserRole(BaseModel):
    user_id: int
    user_role: UserRole
