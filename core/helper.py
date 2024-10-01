import uuid
from datetime import timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils import timezone

from core.models import Report, Template
from core.validators import validate_python

STATUS_CHOICES = [x for x, _ in Report.STATUS_CHOICES]


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


def is_status_valid(val):
    return val in STATUS_CHOICES


def is_template_active(pk):
    q = Template.objects.get(pk=pk)
    return q.is_active


def get_all_templates(active_only=None):
    q = Template.objects.all()
    if active_only:
        q = q.filter(is_active=True)

    return q


def get_template_by_pk(pk, active_only=None):
    q = Template.objects.get(pk=pk)
    if active_only:
        if not q.is_active:
            raise ObjectDoesNotExist()

    return q


def template_exists(pk, active_only=None):
    q = Template.objects.filter(pk=pk)
    if active_only:
        q = q.filter(is_active=True)

    return q.exists()


def get_template_html(pk):
    return str(get_template_by_pk(pk).html_template)


def get_template_script(pk):
    script = str(get_template_by_pk(pk).python_script)
    if not validate_python(script):
        raise ValueError("Detected potentially dangerous keyword or import")

    return script


def get_template_validation_script(pk):
    script = str(get_template_by_pk(pk).python_validation_script)
    if not validate_python(script):
        raise ValueError("Detected potentially dangerous keyword or import")

    return script


def get_template_arguments(pk):
    return list(
        get_template_by_pk(pk).arguments.values("name", "optional", "default_value")
    )


def report_exists(id):
    if is_valid_uuid(id):
        q = Report.objects.filter(hash_id=id)
    else:
        q = Report.objects.filter(pk=id)

    return q.exists()


def get_report_by_id(id):
    if is_valid_uuid(id):
        q = Report.objects.get(hash_id=id)
    else:
        q = Report.objects.get(pk=id)

    return q


def get_report_status(id):
    return get_report_by_id(id).status


def get_report_output_content(id):
    return get_report_by_id(id).output_content


def get_report_output_file(id):
    return get_report_by_id(id).output_file


def get_failed_report_older_than_6hrs():
    return Report.objects.filter(
        Q(status="F") & Q(created_at__lt=timezone.now() - timedelta(hours=6))
    )


def get_report_older_than_12hrs():
    return Report.objects.filter(
        Q(created_at__lt=timezone.now() - timedelta(hours=12))
        & (Q(status="P") | Q(status="G"))
    )


def get_report_older_than_7days():
    return Report.objects.filter(Q(created_at__lt=timezone.now() - timedelta(days=7)))


def create_report(report, output_file):
    if not isinstance(report, Template):
        report = get_template_by_pk(report)

    return Report.objects.create(report=report, output_file=output_file)


def update_generated_report_status(id, status, output_content=None):
    if not is_status_valid(status):
        raise ValueError(f"{status} is not a valid status to set.")

    obj = get_report_by_id(id)
    obj.status = status
    if output_content:
        obj.output_content = output_content

    obj.save()
    return get_report_by_id(id)
