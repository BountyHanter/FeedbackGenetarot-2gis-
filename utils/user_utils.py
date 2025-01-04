from fastapi import HTTPException
from tortoise.exceptions import DoesNotExist
from tortoise.transactions import in_transaction

from models.user_model import User
from models.user_stats_model import UserStats
from scripts_2gis.login import take_access_token_async


async def get_user_and_token(main_user_id: int):
    """
    Получает пользователя по user_id и возвращает access_token.
    Если пользователь не найден или токен отсутствует, вызывает соответствующую обработку.
    """
    user = await User.get_or_none(main_user_id=main_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Получаем access_token
    access_token = user.access_token
    if not access_token:
        access_token = await take_access_token_async(user.username, user.hashed_password)

    return user, access_token


async def execute_api_request(user, func, *args, **kwargs):
    """
    Выполняет запрос с автоматическим обновлением токена, если он недействителен.

    :param user: Объект пользователя, содержащий `username`, `hashed_password` и `access_token`.
    :param func: Асинхронная функция, которую нужно вызвать.
    :param args: Позиционные аргументы для функции.
    :param kwargs: Именованные аргументы для функции.
    :return: Результат выполнения функции.
    """
    try:
        # Первоначальный вызов функции
        result = await func(*args, **kwargs)
        return result
    except HTTPException as e:
        if e.status_code == 401:  # Если токен недействителен
            try:
                # Обновляем токен
                new_access_token = await take_access_token_async(user.username, user.hashed_password)

                # Сохраняем новый токен в базе
                async with in_transaction():
                    user.access_token = new_access_token
                    await user.save()

                # Повторяем запрос с новым токеном
                kwargs["access_token"] = new_access_token
                result = await func(*args, **kwargs)
                return result
            except Exception as inner_e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to refresh access token and retry: {inner_e}"
                )
        elif e.status_code == 404:  # Если ресурс не найден
            raise HTTPException(status_code=404, detail=e.detail)
        else:  # Обработка других ошибок
            raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")


async def get_user_id_by_main_id(main_user_id: int):
    try:
        user = await User.get(main_user_id=main_user_id)
        return user.id
    except DoesNotExist:
        return None


async def get_or_create_user_stats(filial_id: str):
    try:
        # Пытаемся получить объект UserStats
        user_stats = await UserStats.get(filial_id=filial_id)
    except DoesNotExist:
        # Если объект не найден, создаем новый
        user_stats = await UserStats.create(filial_id=filial_id)

    return user_stats
