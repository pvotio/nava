import logging

from django.conf import settings

from service.request import session

logger = logging.getLogger(__name__)


def construct_payload(output_file_path, html, page_size, orientation, header, footer):
    data = {
        "landscape": "false",
        "outputFilename": output_file_path,
        "htmlContent": html,
        "pageSize": page_size,
    }

    if orientation == "L":
        data["landscape"] = "true"

    if header:
        data["headerContent"] = header

    if footer:
        data["footerContent"] = footer

    return data


def generate(
    html,
    output_file_path,
    page_size="A4",
    orientation="L",
    header=None,
    footer=None,
):
    data = construct_payload(
        output_file_path, html, page_size, orientation, header, footer
    )
    r = session.post(f"http://{settings.GENERATOR_HOST}/generate-pdf", data=data)

    if r.status_code == 200:
        logger.info(f"{output_file_path} generated successfully")
        logger.debug(f"{r.json()}")
        return True
    else:
        msg = r.json()["message"]
        logger.error(f"Error executing script: {msg}")
        return False
