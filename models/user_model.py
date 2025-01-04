from typing import Optional

from tortoise.models import Model
from tortoise import fields
from pydantic import BaseModel


class User(Model):
    id = fields.IntField(pk=True)
    main_user_id = fields.IntField(unique=True)  # ID пользователя с мейн сервера
    username = fields.CharField(max_length=50, unique=True)  # Логин
    hashed_password = fields.CharField(max_length=128)  # Хэшированный пароль
    access_token = fields.CharField(max_length=128, unique=True, null=True)  # API-ключ

    class Meta:
        table = "users"


# Модель для входных данных
class UserUpdate(BaseModel):
    main_user_id: Optional[int] = None
    username: Optional[str] = None
    hashed_password: Optional[str] = None


class UserCreate(BaseModel):
    main_user_id: int  # ID пользователя с мейн сервера
    username: str  # Логин
    hashed_password: str  # Пароль

