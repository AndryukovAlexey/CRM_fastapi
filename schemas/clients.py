from pydantic import BaseModel
import datetime

from models import OrderStatus


class OrderDTO(BaseModel):
    name: str
    status: OrderStatus
    
class ShowOrderDTO(OrderDTO):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

class ClientDTO(BaseModel):
    id: int
    username: str
    user_id: int
    manager_id: int|None

class ClientRelDTO(ClientDTO):
    orders: list["ShowOrderDTO"]