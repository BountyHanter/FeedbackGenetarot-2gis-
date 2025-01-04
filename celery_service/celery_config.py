# Настройка Celery
from celery import Celery
import celery_service.tasks

celery_app = Celery(
    "tasks",
    broker="redis://redis:6379/0",  # Имя сервиса Redis
    backend="redis://redis:6379/0"  # Имя сервиса Redis
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],  # Разрешённые форматы
    result_serializer="json",  # Формат для хранения результата
    timezone="UTC",  # Часовой пояс
    enable_utc=True,
)