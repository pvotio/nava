from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import NoReverseMatch, reverse
from django.utils.safestring import mark_safe
from guardian.shortcuts import get_objects_for_user

from core import helper
from core.api.v1.serializers import WriteReportSerializer
from core.forms import ReportGenerationForm
from core.models import Report


@staff_member_required
def download_html_view(request, report_id):
    report = Report.objects.get(pk=report_id)
    response = HttpResponse(report.output_content, content_type="text/html")
    response["Content-Disposition"] = (
        f'attachment; filename="{report.output_file}.html"'
    )
    return response


@staff_member_required
def generate_report_view(request, template_id, admin_site):
    if not is_user_authorized_for_report(request.user, template_id):
        return redirect_to_admin_index_with_error(
            request, "You do not have permission to generate this report."
        )

    if not helper.template_exists(template_id):
        return redirect_to_admin_index_with_warning(request, "Invalid report ID.")

    form = ReportGenerationForm(template_id=template_id)
    template = helper.get_template_by_pk(template_id)

    if request.method == "POST":
        form = ReportGenerationForm(request.POST, template_id=template_id)
        if process_report_form(request, form, template_id):
            return redirect(reverse("admin:index"))

    try:
        changelist_url = reverse(
            "admin:%s_%s_changelist"
            % (template._meta.app_label, template._meta.model_name)
        )
        change_url = reverse(
            "admin:%s_%s_change"
            % (template._meta.app_label, template._meta.model_name),
            args=[template.pk],
        )
    except NoReverseMatch:
        changelist_url = change_url = None

    context = {
        **admin_site.each_context(request),
        "title": "Generate Report",
        "subtitle": template.title,
        "form": form,
        "opts": template._meta,
        "object": template,
        "object_id": template.pk,
        "app_label": template._meta.app_label,
        "original": template,
        "changelist_url": changelist_url,
        "change_url": change_url,
    }

    return render(request, "admin/core_template_generate.html", context)


def is_user_authorized_for_report(user, template_id):
    user_reports = get_objects_for_user(user, "core.view_template")
    return user.is_superuser or user_reports.filter(id=template_id).exists()


def redirect_to_admin_index_with_error(request, message):
    messages.error(request, message)
    return redirect(reverse("admin:index"))


def redirect_to_admin_index_with_warning(request, message):
    messages.warning(request, message, extra_tags="safe")
    return redirect(reverse("admin:index"))


def process_report_form(request, form, template_id):
    cache_key = f"admin:report:generation:{request.user.id}"
    if cache.get(cache_key):
        messages.error(request, "You can generate a report once every 5 seconds.")
        return True

    if form.is_valid():
        data = {"template": template_id, "input_args": form.cleaned_data}
        serializer = WriteReportSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            url = reverse("core:report_result", args=[serializer.data["hash_id"]])
            cache.set(cache_key, 1, 5)
            messages.success(request, create_success_message(serializer, url))
        else:
            messages.error(request, create_error_message(serializer))
    return False


def create_success_message(serializer, url):
    return mark_safe(
        f'Requested report {serializer.data["hash_id"]} added to queue successfully. <a target="_blank" href="{url}">Download Report</a>.'  # noqa
    )


def create_error_message(serializer):
    return mark_safe(f"Error on serializing input data: {serializer.errors}")
