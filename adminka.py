from sqladmin import ModelView
from fastapi import Request, HTTPException, status
from jwt.exceptions import InvalidTokenError
import jwt


from models import UsersOrm, ClientsOrm, OrdersOrm, FilesOrm
from config import settings



class SecureModelView(ModelView):
    def is_accessible(self, request: Request) -> bool:
        token = request.cookies.get("access_token")
        if not token: raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authenticated")
        try:
            key: str = settings.auth_jwt.public_key_path.read_text()
            algorithm: str = settings.auth_jwt.algorithm
            payload = jwt.decode(jwt=token, key=key, algorithms=[algorithm])
        except InvalidTokenError:
            return False
        user_role = payload.get("role")
        if user_role!="admin": return False
        return True
        

class UserAdmin(SecureModelView, model=UsersOrm):
    column_list = [UsersOrm.id, UsersOrm.username, UsersOrm.role]  # Какие поля показывать
    column_searchable_list = [UsersOrm.username]  # По каким полям можно искать
    column_sortable_list = [UsersOrm.id, UsersOrm.username]  # По каким полям можно сортировать
    can_delete = True  # Запрет/разрешение на удаление записей
    icon = "fa-solid fa-user"  # Иконка в боковом меню

class ClientAdmin(SecureModelView, model=ClientsOrm):
    column_list = [ClientsOrm.id, ClientsOrm.username, ClientsOrm.manager_id]

class OrderAdmin(SecureModelView, model=OrdersOrm):
    column_list = [OrdersOrm.id, OrdersOrm.name, OrdersOrm.status, OrdersOrm.client_id]
    column_formatters = {OrdersOrm.status: lambda m, a: m.status.value}  # Отображение Enum
        
class FilesAdmin(SecureModelView, model=FilesOrm):
    column_list = [FilesOrm.id, FilesOrm.filename, FilesOrm.client_id]

def add_views(admin):
    admin.add_view(UserAdmin)
    admin.add_view(ClientAdmin)
    admin.add_view(OrderAdmin)
    admin.add_view(FilesAdmin)
