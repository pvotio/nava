import os
from datetime import timedelta

from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("report")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    "remove-old-pdfs": {
        "task": "core.tasks.remove_old_pdfs",
        "schedule": timedelta(hours=1),
    },
    "remove-failed-reports": {
        "task": "core.tasks.remove_failed_reports",
        "schedule": timedelta(hours=1),
    },
    "remove-old-reports": {
        "task": "core.tasks.remove_old_reports",
        "schedule": timedelta(hours=4),
    },
}

app.conf.timezone = "UTC"


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
