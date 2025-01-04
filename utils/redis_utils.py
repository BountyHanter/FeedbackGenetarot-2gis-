from redis import Redis

# Подключение к Redis
redis_client = Redis(host="redis", port=6379, db=0)


def remove_task_key(task_id: str):
    """
    Удаляет ключ `filial_task:{filial_id}` из Redis при завершении задачи.
    """
    # Ищем ключ, связанный с task_id
    for key in redis_client.scan_iter("filial_task:*"):
        if redis_client.get(key).decode() == task_id:
            redis_client.delete(key)
            print(f"Key {key.decode()} removed from Redis.")
            return
    print(f"No key found for task_id {task_id}.")
