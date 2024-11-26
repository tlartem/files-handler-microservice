from fastapi import FastAPI
from contextlib import asynccontextmanager

from fastapi.middleware.cors import CORSMiddleware

from src.api.file_routes import router as files_router
from src.db_conn import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app: FastAPI = FastAPI(
    lifespan=lifespan,
    title="File Management API",
    description="""
    API для работы с файлами. Поддерживаемые функции:
    - Загрузка файлов
    - Получение информации о файле
    - Скачивание файлов
    """,
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(files_router, prefix="/files", tags=["Files"])
