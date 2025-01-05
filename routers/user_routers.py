from fastapi import APIRouter, HTTPException
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.transactions import in_transaction

from models.user_model import UserCreate, User, UserUpdate
from models.user_stats_model import UserStats
from scripts_2gis.login import take_access_token_async
from scripts_2gis.take_user_info import fetch_user_and_filials_info

router = APIRouter()

# Создаем Pydantic модель для UserStats
UserStatsPydantic = pydantic_model_creator(UserStats, name="UserStats")


@router.post("/create_or_update_user", status_code=201)
async def create_or_update_user(user_data: UserCreate):
    # Проверяем, существует ли пользователь с таким main_user_id
    existing_user = await User.get_or_none(main_user_id=user_data.main_user_id)

    # Запрашиваем токен доступа через API 2ГИС
    try:
        access_token = await take_access_token_async(user_data.username, user_data.hashed_password)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Login failed: {e}")

    try:
        user_info_and_filials = await fetch_user_and_filials_info(access_token)
    except Exception as e:
        raise HTTPException(status_code=501, detail=f"Не удалось получить информацию о пользователе и его филиалах: {e}")

    if existing_user:
        try:
            # Обновляем данные пользователя
            existing_user.username = user_data.username
            existing_user.hashed_password = user_data.hashed_password
            existing_user.access_token = access_token

            # Обновляем информацию о пользователе в базе
            await existing_user.save()

            return {
                "message": "User updated successfully",
                "id": existing_user.id,
                "user_info_and_filials": user_info_and_filials
            }

        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Не удалось обновить пользователя: {e}")

    else:
        # Если пользователь не существует, создаем нового
        try:
            # Создаем нового пользователя
            async with in_transaction():
                user = await User.create(
                    main_user_id=user_data.main_user_id,
                    username=user_data.username,
                    hashed_password=user_data.hashed_password,
                    access_token=access_token
                )

            return {
                "message": "Пользователь успешно создан",
                "id": user.id,
                "user_info_and_filials": user_info_and_filials
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Не удалось создать пользователя: {e}")


@router.get("/get_user_info", status_code=200)
async def get_user_and_filials_info(main_user_id: int):
    """
    Возвращает информацию о пользователе и его филиалах, используя access_token.
    Если токен недействителен, запрашивает новый токен, сохраняет его в БД и повторяет запрос.
    """
    # Проверяем, существует ли пользователь с таким user_id
    user = await User.get_or_none(main_user_id=main_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Проверяем, есть ли access_token
    access_token = user.access_token
    if not access_token:
        raise HTTPException(status_code=403, detail="Токен доступа для пользователя не найден")

    try:
        # Первый вызов fetch_user_and_filials_info
        result = await fetch_user_and_filials_info(access_token)
    except Exception as e:
        # Проверяем, является ли ошибка связанной с токеном (401)
        if isinstance(e, HTTPException) and "401" in str(e.detail):
            try:
                # Обновляем токен
                new_access_token = await take_access_token_async(user.username, user.hashed_password)

                # Сохраняем новый токен в базе
                async with in_transaction():
                    user.access_token = new_access_token
                    await user.save()

                # Повторяем запрос с новым токеном
                result = await fetch_user_and_filials_info(new_access_token)
            except Exception as inner_e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Не удалось обновить токен доступа: {inner_e}",
                )
        else:
            raise HTTPException(status_code=500, detail=f"Не удалось получить информацию о пользователе и его филиалах: {e}")

    return {"main_user_id": main_user_id, "data": result}


@router.put("/update_user/{main_user_id}", status_code=200)
async def update_user(main_user_id: int, user_data: UserUpdate):
    """
    Обновляет данные пользователя. Хотя бы одно поле должно быть передано.
    """
    # Проверяем, передано ли хотя бы одно поле
    if not any([user_data.main_user_id, user_data.username, user_data.hashed_password]):
        raise HTTPException(status_code=400, detail="Необходимо указать хотя бы одно поле")

    # Проверяем, существует ли пользователь
    user = await User.get_or_none(main_user_id=main_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Обновляем данные
    try:
        async with in_transaction():
            if user_data.main_user_id:
                user.main_user_id = user_data.main_user_id
            if user_data.username:
                user.username = user_data.username
            if user_data.hashed_password:
                user.hashed_password = user_data.hashed_password
                # Если обновлён пароль, запрашиваем новый access_token
                user.access_token = await take_access_token_async(
                    user_data.username or user.username,
                    user_data.hashed_password
                )

            await user.save()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Не удалось обновить пользователя: {e}")

    return {
        "message": "Пользователь успешно обновлён",
        "id": user.id,
        "updated_fields": user_data.dict(exclude_unset=True)
    }


@router.get("/stats/{filial_id}", status_code=200)
async def get_user_stats(filial_id: int):

    user_stats = await UserStats.get_or_none(filial_id=filial_id)

    # Если объект не найден, возвращаем сообщение об ошибке
    if not user_stats:
        raise HTTPException(status_code=404)

    return await UserStatsPydantic.from_tortoise_orm(user_stats)



