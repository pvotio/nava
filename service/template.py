from jinja2 import BaseLoader, Environment, TemplateNotFound

from core import helper
from service import utils


class DatabaseLoader(BaseLoader):
    def get_source(self, environment, template):
        source = helper.get_template_html(template)
        if source is None:
            raise TemplateNotFound(template)
        return source, None, lambda: True


def generate_html(template_id, placeholders):
    kwargs = {}
    placeholders = {k: (v if v is not None else "") for k, v in placeholders.items()}
    env = Environment(loader=DatabaseLoader())
    template = env.get_template(str(template_id))
    rendered_html = template.render(placeholders)

    for key in ["header", "footer"]:
        if key in placeholders:
            kwargs[key] = utils.attach_logo(placeholders[key])

    report = helper.get_template_by_pk(template_id)
    for key in ["orientation", "page_size"]:
        kwargs[key] = report.__getattribute__(key)

    return rendered_html, kwargs
