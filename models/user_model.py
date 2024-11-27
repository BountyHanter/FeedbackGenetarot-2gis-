from tortoise.models import Model
from tortoise import fields
from pydantic import BaseModel, Field


class User(Model):
    id = fields.IntField(pk=True)
    user_id = fields.IntField(unique=True)  # ID пользователя с мейн сервера
    username = fields.CharField(max_length=50, unique=True)  # Логин
    hashed_password = fields.CharField(max_length=128)  # Хэшированный пароль
    api_key = fields.CharField(max_length=128, unique=True, null=True)  # API-ключ

    class Meta:
        table = "users"


class UserCreate(BaseModel):
    user_id: int  # ID пользователя с мейн сервера
    username: str  # Логин
    hashed_password: str  # Пароль

