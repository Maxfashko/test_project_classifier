import abc
import logging
from typing import Any, List, Union

from vuka.utils import Config


class BaseBlock(abc.ABC):
    def __init__(self, config: Config = None):
        self._cfg: Config = config

        self.input = None
        if self._cfg is not None:
            if self._cfg.get("data") is not None:
                self.input = self._cfg.get("data").get("input")

            self.output = None
            if self._cfg.get("data") is not None:
                self.output = self._cfg.get("data").get("output")

            self.params = None
            if self._cfg.get("data") is not None:
                self.params = self._cfg.get("data").get("params")

    @classmethod
    def logger(cls, fun):
        def wrapper(self, *args, **kwargs):
            logging.debug("start block {}".format(self.__class__.__name__))
            ret = fun(self, *args, **kwargs)
            logging.debug("finish block {}".format(self.__class__.__name__))
            return ret

        return wrapper

    @abc.abstractmethod
    def __call__(self, containers: List) -> List:
        pass

    def get_input(self, container: List, default: str = "default") -> Any:
        """
            Принимает на вход имя аттрибута и проверяет его наличие в контейнере. Если аттрибут отсутствует возвращает
            аттрибут по-умолчанию.
        Args:
            container:
            default:

        Returns:
            Возвращает аттрибут класса Container
        """
        if self.input is not None:
            data = getattr(container, self.input)
            if data is not None:
                return data
        return getattr(container, default)

    def set_output(self, data, container: List, rewrite=None, default: str = "default") -> None:
        """
            Принимает на вход имя аттрибута и проверяет его наличие в контейнере. Устанавливает аттрибут, если он
            отсутствует в контейнере. Возвращает исключение, если аттрибут присутствует в контейнере и запрещена
            перезапись.
        Args:
            data:
            container: экземпляр класса контейнер.
            rewrite: Разрешить перезапись аттрибута класса при его наличии.
            default: Значение по-умолчанию для аттрибута.

        Returns:

        """
        if rewrite is None:
            rewrite = False

        if self.output is not None:

            # если в данном контейнере уже есть такой аттрибут и запрещена перезапись - выводим ошибку
            if getattr(container, self.output) is not None and rewrite is False:
                raise Exception(f"container already exists attribute {self.output}: {getattr(container, self.output)}")
            else:
                setattr(container, self.output, data)
        else:
            setattr(container, default, data)

    def get_params_rewrite_output(self):
        if self.params is not None:
            return self.params.rewrite_output
        return None

    @staticmethod
    def get_object_by_camera_id(camera_id: Any, objects: List) -> Union[Any, None]:
        """
        Возвращает экземпляр объекта, если поле camera_id эквивалентно аргументу camera_id
        Args:
            camera_id:
            objects: list

        Returns:

        """
        if not isinstance(objects, list):
            logging.error(f"{objects} is not a list!")
            return None

        for obj in objects:
            try:
                if obj.camera_id == camera_id:
                    return obj
            except Exception as e:
                logging.error(f"{e}")
        return None
