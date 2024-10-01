from core import helper
from service import aggregator, dbagent, exceptions


class Validator:
    def __init__(self, template_id, args, modules) -> None:
        self.template_id = template_id
        self.args = args
        self.modules = modules

    def validate(self):
        module_name = self.__validate_template()
        validated_args = self.__validate_args()
        self.__validate_db_record_existance(module_name, validated_args)
        return module_name, validated_args

    def __validate_template(self):
        if not helper.template_exists(self.template_id, active_only=True):
            raise exceptions.InvalidTemplateIDError()

        title = str(helper.get_template_by_pk(self.template_id).title).lower()
        if title not in self.modules:
            raise exceptions.InvalidTemplateIDError()

        return title

    def __validate_args(self):
        missing_args = []
        args = helper.get_template_arguments(self.template_id)
        for arg in args:
            if arg["optional"]:
                continue

            if arg["name"] not in self.args or not self.args[arg["name"]]:
                missing_args.append(arg["name"])

        if missing_args:
            raise exceptions.InvalidArgsError(missing_args)

        process_args = {}
        for arg in args:
            if arg["name"] in self.args and self.args[arg["name"]]:
                if isinstance(self.args[arg["name"]], list):
                    process_args[arg["name"]] = self.args[arg["name"]][0]
                else:
                    process_args[arg["name"]] = self.args[arg["name"]]

            elif arg["optional"]:
                if arg["default_value"] == "exclude":
                    continue

                process_args[arg["name"]] = arg["default_value"]

        return process_args

    def __validate_db_record_existance(self, module_name, validated_args):
        engine = dbagent.Engine(self.template_id)
        validate = aggregator.load_validation_function(module_name, self.template_id)
        if not validate(validated_args, engine):
            raise exceptions.NoDataFoundError()
