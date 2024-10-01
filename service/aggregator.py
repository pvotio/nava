import types

from core import helper
from service import dbagent


def load_module(module_name, template_id):
    script = helper.get_template_script(template_id)
    module = types.ModuleType(module_name)
    exec(script, module.__dict__)
    return getattr(module, "Report")


def load_validation_function(module_name, template_id):
    script = helper.get_template_validation_script(template_id)
    module = types.ModuleType(module_name)
    exec(script, module.__dict__)
    return getattr(module, "validate")


def fetch_placeholders(module_name, template_id, process_args):
    engine = dbagent.Engine(template_id)
    Module = load_module(module_name, template_id)(process_args, engine)
    return Module.fetch()
