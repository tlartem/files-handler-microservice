from celery import Celery
from src.config import settings

app = Celery(
    "tasks",
    broker=settings.BROKER_URL,
    backend=settings.RESULT_BACKEND,
)
