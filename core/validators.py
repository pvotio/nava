def validate_python(code: str) -> bool:
    blacklist = [
        "import os",
        "import sys",
        "import subprocess",
        "import socket",
        "import shutil",
        "import pickle",
        "import ctypes",
        "import dl",
        "from ctypes import",
        "import pdb",
        "exec(",
        "eval(",
        "compile(",
        "input(",
        "getattr(",
        "setattr(",
        "delattr(",
        "__import__(",
        "__del__",
        "__getattribute__",
        "__setattr__",
        "__bases__",
    ]

    for item in blacklist:
        if item in code:
            return False

    return True


def validate_args(report_id, input_args):
    from core.helper import get_template_arguments

    missing_args = []
    args = get_template_arguments(report_id)
    for arg in args:
        if arg["optional"]:
            continue

        if arg["name"] not in input_args or not input_args[arg["name"]]:
            missing_args.append(arg["name"])

    return len(missing_args) == 0, missing_args
