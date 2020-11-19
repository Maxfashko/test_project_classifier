from importlib import import_module
import logging


def import_classmodule(path):
    try:
        module_name, class_name = path.rsplit(".", 1)
        module = import_module(module_name)
        _class = getattr(module, class_name)
        return _class
    except Exception as e:
        logging.warning(f"import_classmodule for <{path}> error: {e}")
        return None
