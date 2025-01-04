from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from celery_service.celery_config import celery_app
from config import init_db
from utils.redis_utils import redis_client
from utils.user_utils import get_or_create_user_stats

router = APIRouter()


class UserStatsRequest(BaseModel):
    main_user_id: int
    filial_id: int


@router.post("/start_stats_collection")
async def start_stats_collection(request: UserStatsRequest):
    """
    Инициирует сбор статистики.
    """
    # Проверяем, есть ли уже активная задача для filial_id
    if redis_client.exists(f"filial_task:{request.filial_id}"):
        raise HTTPException(
            status_code=400,
            detail=f"Task for filial_id {request.filial_id} is already in progress"
        )

    # Отправляем задачу в Celery
    task = celery_app.send_task(
        "tasks.collect_stats",
        kwargs={
            "main_user_id": request.main_user_id,
            "filial_id": request.filial_id
        }
    )

    # Сохраняем filial_id с task_id в Redis
    redis_client.set(f"filial_task:{request.filial_id}", task.id)

    # Инициализация Tortoise ORM
    await init_db()
    user_stats = await get_or_create_user_stats(str(request.filial_id))
    await user_stats.save()

    return {"message": "Stats collection started", "task_id": task.id}


@router.get("/task_status/{task_id}")
async def get_task_status(task_id: str):
    """
    Проверяет статус задачи по task_id.
    """
    result = AsyncResult(task_id, app=celery_app)

    # Проверяем статус задачи
    status = result.status
    response = {
        "task_id": task_id,
        "status": status,
    }

    # Если задача завершена успешно, добавляем результат
    if status == "SUCCESS":
        response["result"] = result.result

    # Если задача завершилась ошибкой, добавляем информацию об ошибке
    elif status == "FAILURE":
        response["error"] = str(result.result)

    return response
