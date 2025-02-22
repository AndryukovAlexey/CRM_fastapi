from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy.sql import func, text
from typing import Optional, Annotated
import enum
import datetime


intpk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
updated_at = Annotated[datetime.datetime, mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=datetime.datetime.utcnow,
    )]


class UserRole(enum.Enum):
    ADMIN = 'admin'
    MANAGER = 'manager'
    CLIENT = 'client'
    USER =  'user'

class OrderStatus(enum.Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELED = "canceled"


class Base(DeclarativeBase):
    
    def __repr__(self):
        return f"<{self.__class__.__name__} {','.join([f'{col}={getattr(self, col)}' for col in self.__table__.columns.keys()])}>"

class UsersOrm(Base):
    __tablename__ = 'users'

    id: Mapped[intpk]
    username: Mapped[str]
    hashed_password: Mapped[bytes]
    role: Mapped[UserRole] = mapped_column(default=UserRole.USER)

    clients: Mapped[list["ClientsOrm"]] = relationship(back_populates="manager", foreign_keys="[ClientsOrm.manager_id]")

class ClientsOrm(Base):
    __tablename__ = 'clients'

    id: Mapped[intpk]
    username: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE", name="user_id"))
    manager_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL", name="manager_id"))

    manager: Mapped["UsersOrm"] = relationship(back_populates="clients", foreign_keys=[manager_id])
    orders: Mapped[list["OrdersOrm"]] = relationship(back_populates="client")

class OrdersOrm(Base):
    __tablename__ = 'orders'

    id: Mapped[intpk]
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"))
    name: Mapped[str]
    status: Mapped[OrderStatus] = mapped_column(default=OrderStatus.NEW)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    client: Mapped["ClientsOrm"] = relationship(back_populates="orders")

class FilesOrm(Base):
    __tablename__ = 'files'

    id: Mapped[intpk]
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"))
    filename: Mapped[str]
    uploaded_at: Mapped[created_at]
