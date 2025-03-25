import json
import logging
import os

from celery import shared_task

from core import helper
from service import aggregator, exceptions, generator, template, validate

logger = logging.getLogger(__name__)


@shared_task
def validate_report(template_id, args, report_id):
    logger.debug(
        f"Starting validation for report {report_id} with template {template_id}"
    )
    validator_instance = validate.Validator(
        template_id,
        args,
        [str(report.title).lower() for report in helper.get_all_templates(True)],
    )
    module_name, process_args = validator_instance.validate()
    return {
        "module_name": module_name,
        "process_args": process_args,
        "template_id": template_id,
        "report_id": report_id,
    }


@shared_task
def fetch_placeholders(data):
    logger.debug(f"Fetching placeholders for report {data['report_id']}")
    module_name, process_args, template_id, report_id = (
        data["module_name"],
        data["process_args"],
        data["template_id"],
        data["report_id"],
    )
    placeholders = aggregator.fetch_placeholders(module_name, template_id, process_args)
    return {
        "placeholders": placeholders,
        "template_id": template_id,
        "report_id": report_id,
    }


@shared_task
def generate_html(data):
    logger.debug(f"Generating HTML for report {data['report_id']}")
    placeholders, template_id, report_id = (
        data["placeholders"],
        data["template_id"],
        data["report_id"],
    )
    html, kwargs = template.generate_html(template_id, placeholders)
    return {"html": html, "kwargs": kwargs, "report_id": report_id}


@shared_task
def generate_pdf(data):
    logger.debug(f"Generating PDF for report {data['report_id']}")
    html, kwargs, report_id = data["html"], data["kwargs"], data["report_id"]
    generated_report = helper.get_report_by_id(report_id)
    generator.generate(html, generated_report.output_file, **kwargs)
    return {"html": html, "report_id": report_id}


@shared_task
def update_report_status(data):
    logger.debug(f"Updating report status for {data['report_id']}")
    html, report_id = data["html"], data["report_id"]
    generated_report = helper.get_report_by_id(report_id)
    helper.update_generated_report_status(generated_report.id, "G", html)
    return


@shared_task
def handle_errors(request, exc, traceback, stage, report_id):
    logger.error(f"Error in {stage} for report {report_id}: {exc}")

    if isinstance(exc, exceptions.DatabaseConnectionError):
        message = "Failed to establish a connection with the database."
    elif isinstance(exc, exceptions.NoDataFoundError):
        message = "No data found for the given arguments."
    else:
        message = f"Unexpected error happened during report generation. Contact platform administrator. Trace ID: {report_id}"  # noqa

    error_message = {
        "verbose_message": f"{stage} - {exc} - {traceback}",
        "message": message,
    }
    helper.update_generated_report_status(report_id, "F", json.dumps(error_message))
    return


def generate_report_async(template_id, args, report_id):
    task_chain = (
        validate_report.s(template_id, args, report_id).set(
            link_error=handle_errors.s("validate_report", report_id)
        )
        | fetch_placeholders.s().set(
            link_error=handle_errors.s("fetch_placeholders", report_id)
        )
        | generate_html.s().set(link_error=handle_errors.s("generate_html", report_id))
        | generate_pdf.s().set(link_error=handle_errors.s("generate_pdf", report_id))
        | update_report_status.s().set(
            link_error=handle_errors.s("update_report_status", report_id)
        )
    )
    result = task_chain.apply_async()
    return result


@shared_task
def remove_failed_reports():
    reports = helper.get_failed_report_older_than_6hrs()
    reports.delete()
    logger.info(f"{len(reports)} Failed reports deleted.")


@shared_task
def remove_old_pdfs():
    reports = helper.get_report_older_than_12hrs()
    for report in reports:
        relative_pdf = os.path.join("files/", f"{report.output_file}.pdf")
        pdf_filename = os.path.abspath(relative_pdf)
        logger.info(f"Removing: {pdf_filename}")
        if os.path.exists(pdf_filename):
            os.remove(pdf_filename)
            logger.info(f"Removed: {pdf_filename}")

        helper.update_generated_report_status(report.id, "D")

    logger.info(f"{len(reports)} Old reports's pdf deleted.")


@shared_task
def remove_old_reports():
    reports = helper.get_report_older_than_7days()
    reports.delete()
    logger.info(f"{len(reports)} Old reports deleted.")
