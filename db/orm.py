from sqlalchemy import select, insert, update, delete
from sqlalchemy.orm import selectinload

from db.database import new_session
from models import *
from schemas.users import UserGetDTO
from schemas.clients import ClientDTO, ShowOrderDTO, ClientRelDTO
from schemas.managers import ManagerDTO, ShowOrdersClientsDTO
from schemas.admins import UsersDTO


#multimodels start
async def get_superuser(user_id: int):
    async with new_session() as session:
        query = (select(UsersOrm.id, UsersOrm.username).where(UsersOrm.id==user_id))
        res = await session.execute(query)
        res_orm = res.first()
        if res_orm: res_dto = ManagerDTO.model_validate(res_orm, from_attributes=True)
        else: res_dto = None
        return res_dto
    
async def change_role(user_id: int, role: UserRole):
    async with new_session() as session:
        query = update(UsersOrm).values(role=role).filter_by(id=user_id)
        await session.execute(query)
        await session.commit()
        return True

async def get_clients(manager_id: int = None):
    async with new_session() as session:
        if manager_id:
            query = (select(ClientsOrm).where(ClientsOrm.manager_id==manager_id).options(selectinload(ClientsOrm.orders)))
        else:
            query = (select(ClientsOrm).options(selectinload(ClientsOrm.orders)))
        res = await session.execute(query)
        res_orm = res.unique().scalars().all()
        if res_orm: 
            # res_dto = [ClientRelDTO.model_validate({**orm_res.__dict__, 
            #                                         "orders": [ShowOrderDTO.model_validate(order, from_attributes=True) for order in orm_res.orders]
            #                                         }) for orm_res in res_orm]
            res_dto = [ClientRelDTO.model_validate(orm_res, from_attributes=True).model_copy(
                    update={'orders': [ShowOrderDTO.model_validate(order, from_attributes=True) for order in orm_res.orders]}) 
                for orm_res in res_orm]
        else: res_dto = []
        return res_dto

async def get_orders(manager_id: int = None):
    async with new_session() as session:
        if manager_id:
            query = (select(ClientsOrm).where(ClientsOrm.manager_id==manager_id).options(selectinload(ClientsOrm.orders)))
        else:
            query = (select(ClientsOrm).options(selectinload(ClientsOrm.orders)))
        res = await session.execute(query)
        res_orm = res.unique().scalars().all()
        res_dto = []
        if res_orm:
            for orm_res in res_orm:
                res_dto += [ShowOrdersClientsDTO.model_validate(order, from_attributes=True) for order in orm_res.orders]
        return res_dto

async def create_order(client_id: int, name: str, status: OrderStatus):
    async with new_session() as session:
        query = (insert(OrdersOrm).values(client_id=client_id, name=name, status=status).returning(OrdersOrm.id))
        res_q = await session.execute(query)
        res = res_q.first()
        await session.commit()
        return res[0]

async def del_order(order_id: int, client_id: int = None):
    async with new_session() as session:
        if client_id:
            query = delete(OrdersOrm).filter_by(id=order_id, client_id=client_id).returning(OrdersOrm.id)
        else:
            query = delete(OrdersOrm).filter_by(id=order_id).returning(OrdersOrm.id)
        res = await session.execute(query)
        await session.commit()
        return res.scalar()
#multimodels end

#users start
async def create_user(username: str, hash_password: bytes):
    async with new_session() as session:
        query = (insert(UsersOrm).values(username=username, hashed_password=hash_password))
        await session.execute(query)
        await session.commit()
        return True

async def get_user(id: int = None, username: str = None):
    async with new_session() as session:
        if id: query = (select(UsersOrm).where(UsersOrm.id==id))
        else: query = (select(UsersOrm).where(UsersOrm.username==username)) # для проверки существования юзера в бд при регистрации
        res = await session.execute(query)
        res_orm = res.scalar()
        if res_orm: res_dto = UserGetDTO.model_validate(res_orm, from_attributes=True)
        else: res_dto = None
        return res_dto
#users end

#clients
async def get_client(user_id: int = None, client_id: int = None):
    async with new_session() as session:
        if user_id: query = (select(ClientsOrm).where(ClientsOrm.user_id==user_id))
        else: query = (select(ClientsOrm).where(ClientsOrm.id==client_id))
        res = await session.execute(query)
        res_orm = res.scalar()
        if res_orm: res_dto = ClientDTO.model_validate(res_orm, from_attributes=True)
        else: res_dto = None
        return res_dto
    
async def get_client_orders(client_id: int):
    async with new_session() as session:
        query = (select(OrdersOrm).where(OrdersOrm.client_id==client_id))
        res = await session.execute(query)
        res_orm = res.scalars().all()
        if res_orm: res_dto = [ShowOrderDTO.model_validate(orm_res, from_attributes=True) for orm_res in res_orm]
        else: res_dto = []
        return res_dto

async def change_order(client_id: int, name: str, status: OrderStatus, order_id):
    async with new_session() as session:
        query = (update(OrdersOrm).values(name=name, status=status).filter_by(client_id=client_id, id=order_id).returning(OrdersOrm))
        res_q = await session.execute(query)
        res = res_q.scalar()
        await session.commit()
        if res: res_dto = ShowOrderDTO.model_validate(res, from_attributes=True)
        else: res_dto = None
        return res_dto

async def create_client(username: str, user_id: int):
    async with new_session() as session:
        query = insert(ClientsOrm).values(username=username, user_id=user_id)
        await session.execute(query)
        await session.commit()
        return True

async def delete_client(client_id: int):
    async with new_session() as session:
        query = delete(ClientsOrm).filter_by(id=client_id)
        await session.execute(query)
        await session.commit()
        return True
    
async def add_file(client_id: int, filename: str):
    async with new_session() as session:
        query = insert(FilesOrm).values(client_id=client_id, filename=filename)
        await session.execute(query)
        await session.commit()
        return True

async def get_file(client_id: int, filename: str = None):
    async with new_session() as session:
        query = (select(FilesOrm).filter_by(filename=filename, client_id=client_id))
        res = await session.execute(query)
        res_orm = res.scalar()
        return res_orm
#clients end

#managers start
async def appoint_manager(client_id: int, manager_id: int):
    async with new_session() as session:
        query = update(ClientsOrm).values(manager_id=manager_id).filter_by(id=client_id)
        await session.execute(query)
        await session.commit()
        return True
    
async def unassignment_manager(client_id: int):
    async with new_session() as session:
        query = update(ClientsOrm).values(manager_id=None).filter_by(id=client_id)
        await session.execute(query)
        await session.commit()
        return True
#managers end

#admins start
async def get_users():
    async with new_session() as session:
        query = (select(UsersOrm).options(selectinload(UsersOrm.clients).selectinload(ClientsOrm.orders)))
        res = await session.execute(query)
        res_orm = res.unique().scalars().all()
        if res_orm:
            res_dto = [UsersDTO.model_validate(orm_res, from_attributes=True).model_copy(
                update={'clients': [ClientRelDTO.model_validate(client, from_attributes=True).model_copy(
                    update={'orders': [ShowOrderDTO.model_validate(order, from_attributes=True) for order in client.orders]}
                ) for client in orm_res.clients]}
            ) for orm_res in res_orm]
        else: res_dto = []
        return res_dto
#admins end
