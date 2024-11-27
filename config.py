from tortoise import Tortoise


# Настройка Tortoise ORM
async def init_db():
    await Tortoise.init(
        db_url="sqlite://db.sqlite3",  # Указываем SQLite как базу данных
        modules={"models": ["models.user_model"]},
    )
    await Tortoise.generate_schemas()  # Автоматически создаёт таблицы, если их нет
