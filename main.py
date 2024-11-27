from fastapi import FastAPI, HTTPException
from tortoise.transactions import in_transaction

from config import init_db
from models.user_model import UserCreate, User

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    await init_db()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/create_user", status_code=201)
async def create_user(user_data: UserCreate):
    # Проверяем, существует ли пользователь с таким user_id
    existing_user = await User.get_or_none(user_id=user_data.user_id)
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this ID already exists")

    # Сохраняем пользователя в базу
    async with in_transaction():
        user = await User.create(
            user_id=user_data.user_id,
            username=user_data.username,
            hashed_password=user_data.hashed_password
        )

    return {"message": "User created successfully", "id": user.id}