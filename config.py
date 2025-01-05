import os
from tortoise import Tortoise

# Определяем базовую директорию (где находится текущий файл)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Указываем путь к базе данных
DB_DIR = os.path.join(BASE_DIR, "db")
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)
DATABASE_FILE = os.path.join(BASE_DIR, "db", "db.sqlite3")

TORTOISE_ORM = {
    "connections": {"default": f"sqlite://{DATABASE_FILE}"},
    "apps": {
        "models": {
            "models": ["models.user_model", "models.user_stats_model", "models.reviews_model", "aerich.models"],
            "default_connection": "default",
        },
    },
}


# Настройка Tortoise ORM
async def init_db():
    await Tortoise.init(config=TORTOISE_ORM)
