import copy

import six

from msc import models as parent


def is_str(x):
    """Whether the input is an string instance."""
    return isinstance(x, six.string_types)


class ModelProvider:
    @staticmethod
    def get_model(model_cfg):
        model_info = copy.deepcopy(model_cfg)

        model_type = model_info.pop("type")
        try:
            if is_str(model_type):
                model_type = getattr(parent, model_type)
            return model_type(**model_info)
        except Exception:
            raise
