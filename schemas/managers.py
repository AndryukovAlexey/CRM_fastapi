from pydantic import BaseModel

from .clients import ShowOrderDTO
from models import UserRole


class ShowOrdersClientsDTO(ShowOrderDTO):
    client_id: int

class ManagerDTO(BaseModel):
    id: int
    username: str
