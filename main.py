from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqladmin import Admin

from db.database import setup_db, engine
from api import clients, managers, admins, users
from adminka import add_views


@asynccontextmanager
async def lifespan(app: FastAPI):
    await setup_db()
    print('Запуск')
    yield
    print('Выключение')


app = FastAPI(lifespan=lifespan)
app.include_router(clients.router)
app.include_router(managers.router)
app.include_router(admins.router)
app.include_router(users.router)

admin = Admin(app, engine, title="Админка FastAPI")
add_views(admin)
