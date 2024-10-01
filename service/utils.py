import base64
import os
import re

from django.conf import settings


def get_path(html):
    match = re.search(r"\{\{path:(.*?)\}\}", html)
    if match:
        return match.group(1)


def get_report_logo_base64(path):
    if path.startswith("/"):
        path = path[1:]

    logo_extension = os.path.splitext(path)[1].lower()
    mime_type = "image/jpeg"
    if logo_extension == ".png":
        mime_type = "image/png"
    elif logo_extension == ".svg":
        mime_type = "image/svg+xml"

    with open(settings.MEDIA_ROOT / path, "rb") as r:
        image_data = r.read()

    encoded_image = base64.b64encode(image_data).decode("utf-8")
    return f"data:{mime_type};base64,{encoded_image}"


def attach_logo(html):
    if "{{path" not in html:
        return html

    file_path = get_path(html)
    image_base64 = get_report_logo_base64(file_path)
    if image_base64:
        placeholder = f"path:{file_path}"
        html = html.replace("{{" + placeholder + "}}", image_base64)

    return html
