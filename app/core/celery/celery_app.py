from celery import Celery

celery_app = Celery(
    "finapay",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/1",
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    task_default_delivery_mode="persistent",
)

import app.features.auth.infrastructure.tasks.task
import app.features.client.infrastructure.tasks.task
import app.features.commande.infrastructure.tasks.task