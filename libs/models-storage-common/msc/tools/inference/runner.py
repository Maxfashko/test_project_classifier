from importlib import import_module
from typing import Dict, List, Union

from vuka.core import State
from vuka.utils import Config, ConfigDict


def load_class(path: str, config: Dict, args: Dict = {}):
    try:
        module_name, class_name = path.rsplit(".", 1)
        module = import_module(module_name)
        _class = getattr(module, class_name)
        _class = _class(config, **args)
        return _class
    except Exception:
        raise


class Runner:
    """
    Deep Learning Runner for different models runs inference
    """

    def __init__(self, config: str = None, device_id: Union[int, str] = None) -> None:
        super(Runner, self).__init__()
        self._config = Config.fromfile(config)
        self._device_id: Union[int, str] = device_id
        self.pipeline = []

        state = State()
        state.device_id = self._device_id

        for k, v in self._config.items():
            if isinstance(v, ConfigDict):
                try:
                    _block_class = load_class(self._config[k]["module"], self._config[k])
                except Exception as e:
                    raise Exception(f"block_name {k}", e)

                self.pipeline.append(_block_class)

    def __call__(self, containers: List) -> List:
        """
        Args:
            containers: List

        Returns:
            List

        """
        for _cl in self.pipeline:
            containers = _cl(containers)
        return containers
