import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import Report
from core.tasks import generate_report_async

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Report)
def trigger_report_generation(sender, instance, created, **kwargs):
    if created:
        logger.debug(f"Triggering report generation signal for {instance.id}")
        generate_report_async(instance.template.id, instance.input_args, instance.id)
