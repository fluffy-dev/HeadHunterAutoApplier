from celery import Celery
from hh.config.redis import settings as redis_settings

celery_app = Celery(
    "hh_automator",
    broker=redis_settings.redis_url(),
    backend=redis_settings.redis_url(),
    include=["hh.worker.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)