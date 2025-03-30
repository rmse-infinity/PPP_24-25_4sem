import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app/db/test.db")
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    if JWT_SECRET_KEY is None:
        raise ValueError("ОШИБКА: JWT_SECRET_KEY не задан в переменных окружения!")
