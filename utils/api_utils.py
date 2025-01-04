from fastapi import HTTPException

from utils.user_utils import execute_api_request, get_user_and_token


async def handle_api_request(main_user_id: int, api_function, **kwargs):
    """
    Универсальная функция для обработки запросов к API.

    Args:
        main_user_id (int): ID пользователя.
        api_function (Callable): Функция API для выполнения.
        **kwargs: Дополнительные именованные аргументы для функции API.

    Returns:
        dict: Результат выполнения функции API.
    """
    try:
        # Получаем пользователя и токен
        user, access_token = await get_user_and_token(main_user_id)

        # Выполняем запрос через execute_api_request
        result = await execute_api_request(user, api_function, access_token=access_token, **kwargs)

        return result

    except HTTPException as e:
        # Пробрасываем HTTPException
        raise e

    except Exception as e:
        # Обработка неожиданных ошибок
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
